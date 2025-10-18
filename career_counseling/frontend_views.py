"""
Career Counseling Frontend Views
Main view functions for assessment, recommendations, and PDF report generation
Uses ReportLab for PDF generation (pure Python - no external dependencies)
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .models import Question, UserResponse, CareerRecommendation, AssessmentReport, UserProfile, CareerPath
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
import json
import logging

# Setup logging
logger = logging.getLogger(__name__)


def home(request):
    """Home page view"""
    return render(request, 'home.html')


@login_required
def profile(request):
    """User profile view showing assessment history and recommendations"""
    user_responses = UserResponse.objects.filter(user=request.user).order_by('-created_at')
    career_recommendations = CareerRecommendation.objects.filter(user=request.user).order_by('-confidence_score')
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Calculate profile completion percentage
    total_fields = 4
    completed_fields = sum([
        bool(request.user.first_name),
        bool(request.user.last_name),
        bool(profile.education_level),
        bool(profile.field_of_study)
    ])
    profile_completion = (completed_fields / total_fields) * 100
    
    # Get all user responses and log them for debugging
    all_responses = user_responses.all()
    logger.info(f"Found {all_responses.count()} responses for user {request.user.username}")
    for response in all_responses:
        logger.info(f"Response ID: {response.id}, Type: {response.question.question_type}, Date: {response.created_at}")

    context = {
        'user_responses': all_responses,  # Show all responses instead of just 5
        'career_recommendations': career_recommendations[:5],
        'profile_completion': int(profile_completion),
        'profile': profile
    }
    return render(request, 'profile.html', context)


@login_required
def assessment(request):
    """Handle career assessment form submission and response storage"""
    if request.method == 'POST':
        # Handle AJAX POST requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                responses = data.get('responses', {})
                
                # Validate that we have responses
                if not responses:
                    return JsonResponse({
                        'status': 'error', 
                        'message': 'No responses provided. Please answer all questions.'
                    }, status=400)
                
                # Delete existing responses for this user
                UserResponse.objects.filter(user=request.user).delete()
                
                # Save user responses
                saved_responses = []
                for question_text, response_text in responses.items():
                    try:
                        question_text_clean = question_text.strip()
                        question = Question.objects.get(question_text=question_text_clean)
                        response = UserResponse.objects.create(
                            user=request.user,
                            question=question,
                            response_text=response_text
                        )
                        saved_responses.append(response)
                        logger.info(f"Saved response for: {question_text_clean}")
                    except Question.DoesNotExist:
                        logger.warning(f"Question not found: '{question_text_clean}'")
                        # Try to find similar question
                        similar = Question.objects.filter(question_text__icontains=question_text_clean[:20]).first()
                        if similar:
                            logger.info(f"Found similar question: {similar.question_text}")
                        continue
                
                if not saved_responses:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'No valid responses could be saved.'
                    }, status=400)
                
                # Generate career recommendations
                generate_recommendations(request.user)
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Assessment completed successfully',
                    'redirect_url': '/recommendations/'
                })
                
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid response format'
                }, status=400)
            except Exception as e:
                logger.error(f"Assessment error: {str(e)}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error processing assessment'
                }, status=500)
        
        # Handle regular form POST requests
        else:
            try:
                responses = {}
                for key, value in request.POST.items():
                    if key.startswith('question_'):
                        question_id = key.split('_')[1]
                        responses[question_id] = value
                
                if not responses:
                    messages.error(request, 'Please answer all questions.')
                    return redirect('assessment')
                
                # Delete existing responses
                UserResponse.objects.filter(user=request.user).delete()
                
                # Save new responses
                for question_id, response_text in responses.items():
                    try:
                        question = Question.objects.get(id=question_id)
                        UserResponse.objects.create(
                            user=request.user,
                            question=question,
                            response_text=response_text
                        )
                    except Question.DoesNotExist:
                        continue
                
                # Generate recommendations
                generate_recommendations(request.user)
                return redirect('recommendations')
                
            except Exception as e:
                logger.error(f"Assessment error: {str(e)}")
                messages.error(request, 'Error processing assessment. Please try again.')
                return redirect('assessment')
                
    # GET request - show assessment form
    questions = Question.objects.all().order_by('id')
    
    return render(request, 'career_counseling/assessment.html', {
        'questions': questions
    })
def generate_recommendations(user):
    """Generate career recommendations based on user responses"""
    try:
        # Get user responses
        user_responses = UserResponse.objects.filter(user=user)
        
        if not user_responses.exists():
            logger.warning(f"No responses found for user {user.username}")
            return
        
        logger.info(f"Generating recommendations for user: {user.username}")
        logger.info(f"User has {user_responses.count()} responses")
        
        # Get all career paths
        career_paths = CareerPath.objects.all()
        logger.info(f"Scoring against {career_paths.count()} career paths")
        
        # Clear existing recommendations
        CareerRecommendation.objects.filter(user=user).delete()
        
        # Score each career path
        all_scores = []
        for career_path in career_paths:
            score = calculate_career_score(user_responses, career_path)
            all_scores.append((career_path, score))
            logger.info(f"Score for {career_path.title}: {score}")
        
        # Create recommendations for all career paths (not just those with score > 0)
        for career_path, score in all_scores:
            # Generate reasoning even for lower scores
            reasoning = generate_recommendation_reasoning(user_responses, career_path, score)
            
            CareerRecommendation.objects.create(
                user=user,
                career_path=career_path,
                confidence_score=score,
                reasoning=reasoning
            )
            logger.info(f"Created recommendation: {career_path.title} with score {score}")
        
        # Generate or update assessment report
        generate_assessment_report(user)
        logger.info(f"Recommendations generated for user: {user.username}")
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


def calculate_career_score(user_responses, career_path):
    """Calculate match score between user responses and career path"""
    try:
        total_score = 0
        response_count = user_responses.count()
        
        if response_count == 0:
            return 0
        
        # Since responses don't directly contain skill keywords, we'll use a simpler approach:
        # Give a base score to all careers, with some variance based on question types
        
        base_score = 0.5  # Start with 50% for everyone
        
        # Check question types to adjust score
        for response in user_responses:
            question = response.question
            response_lower = response.response_text.lower()
            
            # Boost score for specific question type answers
            if question.question_type == 'SKILLS':
                if response_lower in ['excellent', 'very good', 'good', 'proficient']:
                    base_score += 0.05
            elif question.question_type == 'INTERESTS':
                base_score += 0.02
            elif question.question_type == 'PERSONALITY':
                base_score += 0.01
        
        # Normalize to 0-1 range
        score = min(1.0, max(0.0, base_score))
        
        logger.info(f"Score for {career_path.title}: {score:.2f}")
        return score
        
    except Exception as e:
        logger.error(f"Error calculating career score: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 0.5  # Return default score on error


def generate_recommendation_reasoning(user_responses, career_path, score):
    """Generate explanation for why a career was recommended"""
    try:
        reasons = []
        
        # Get career path requirements
        required_skills = career_path.required_skills
        if isinstance(required_skills, str):
            required_skills = json.loads(required_skills)
        
        # Extract all skills from the dictionary
        all_skills = []
        if isinstance(required_skills, dict):
            all_skills.extend(required_skills.get('technical', []))
            all_skills.extend(required_skills.get('soft', []))
        else:
            all_skills = required_skills if isinstance(required_skills, list) else []
        
        # Find matching skills from user responses
        matching_skills = []
        for response in user_responses:
            response_lower = response.response_text.lower()
            for skill in all_skills:
                if skill.lower() in response_lower and skill not in matching_skills:
                    matching_skills.append(skill)
        
        # Build reasoning text
        if matching_skills:
            reasons.append(f"You have strong skills in {', '.join(matching_skills[:3])}, which are essential for this role.")
        
        reasons.append(f"Your assessment responses align {int(score*100)}% with the requirements for this career path.")
        
        education_reqs = career_path.education_requirements
        if isinstance(education_reqs, str):
            education_reqs = json.loads(education_reqs)
        
        # Handle both dict and list formats for education requirements
        if education_reqs:
            if isinstance(education_reqs, dict):
                # If it's a dict, try to get values
                req_list = []
                if 'minimum' in education_reqs:
                    req_list.append(str(education_reqs.get('minimum', '')))
                if 'preferred' in education_reqs:
                    req_list.append(str(education_reqs.get('preferred', '')))
                if req_list:
                    reasons.append(f"This role typically requires: {', '.join(filter(None, req_list))}.")
            elif isinstance(education_reqs, list):
                reasons.append(f"This role typically requires: {', '.join(education_reqs[:2])}.")
        
        salary_info = career_path.average_salary
        if salary_info:
            reasons.append(f"Average salary: {salary_info}.")
        
        return " ".join(reasons)
        
    except Exception as e:
        logger.error(f"Error generating reasoning: {str(e)}")
        return "Based on your assessment responses, this career path is a good match for your profile."


def generate_assessment_report(user):
    """Create or update assessment report with analysis"""
    try:
        user_responses = UserResponse.objects.filter(user=user)
        
        # Prepare analysis data
        skill_analysis = {}
        interest_analysis = {}
        personality_insights = {}
        
        # Extract skills from responses
        for idx, response in enumerate(user_responses, 1):
            question = response.question
            if question.question_type == 'SKILLS':
                skill_analysis[f"Response {idx}"] = response.response_text
            elif question.question_type == 'INTERESTS':
                interest_analysis[f"Response {idx}"] = response.response_text
            elif question.question_type == 'PERSONALITY':
                personality_insights[f"Trait {idx}"] = response.response_text
        
        # Delete existing reports and create a new one
        AssessmentReport.objects.filter(user=user).delete()
        
        # Create fresh report
        report = AssessmentReport.objects.create(
            user=user,
            skill_analysis=skill_analysis,
            interest_analysis=interest_analysis,
            personality_insights=personality_insights
        )
        
        logger.info(f"Assessment report generated for user: {user.username}")
        
    except Exception as e:
        logger.error(f"Error generating assessment report: {str(e)}")


@login_required
def recommendations(request):
    """Display career recommendations for the user"""
    try:
        recommendations = CareerRecommendation.objects.filter(user=request.user).order_by('-confidence_score')
        
        logger.info(f"Loading recommendations for user: {request.user.username}")
        logger.info(f"Found {recommendations.count()} recommendations")
        
        for rec in recommendations:
            logger.info(f"  - {rec.career_path.title}: {rec.confidence_score}")
        
        context = {
            'recommendations': recommendations,
            'recommendation_count': recommendations.count()
        }
        return render(request, 'recommendations.html', context)
        
    except Exception as e:
        logger.error(f"Error loading recommendations: {str(e)}")
        messages.error(request, 'Error loading recommendations')
        return redirect('home')


@login_required
def career_detail(request, career_id):
    """Display detailed information about a specific career"""
    try:
        career = CareerPath.objects.get(id=career_id)
        recommendation = CareerRecommendation.objects.filter(
            user=request.user,
            career_path=career
        ).first()
        
        context = {
            'career': career,
            'recommendation': recommendation
        }
        return render(request, 'career_detail.html', context)
        
    except CareerPath.DoesNotExist:
        messages.error(request, 'Career not found')
        return redirect('recommendations')
    except Exception as e:
        logger.error(f"Error loading career detail: {str(e)}")
        messages.error(request, 'Error loading career details')
        return redirect('recommendations')


@login_required
def assessment_detail(request, assessment_id):
    """Display assessment results and details"""
    logger.info(f"Starting assessment_detail view for ID: {assessment_id}")
    try:
        # Log user information
        logger.info(f"User: {request.user.username} (authenticated: {request.user.is_authenticated})")
        
        # Get the user response
        response = UserResponse.objects.get(id=assessment_id, user=request.user)
        logger.info(f"Found UserResponse: id={response.id}, question_type={response.question.question_type}")
        
        # Get recommendations
        recommendations = CareerRecommendation.objects.filter(user=request.user).order_by('-confidence_score')
        logger.info(f"Found {recommendations.count()} recommendations")
        
        context = {
            'response': response,
            'recommendations': recommendations
        }
        logger.info("Rendering template with context")
        return render(request, 'assessment_detail.html', context)
        
    except UserResponse.DoesNotExist as e:
        logger.error(f"UserResponse not found: ID={assessment_id}, User={request.user.username}")
        logger.error(f"Full error: {str(e)}")
        messages.error(request, 'Assessment response not found. Please try again.')
        return redirect('profile')
    except Exception as e:
        logger.error(f"Unexpected error in assessment_detail: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        messages.error(request, f'Error loading assessment details: {str(e)}')
        return redirect('profile')


@login_required
def download_report(request):
    """
    Download assessment report as PDF using ReportLab
    Pure Python PDF generation - no external system dependencies needed
    """
    try:
        # Get the latest assessment report
        report = AssessmentReport.objects.filter(user=request.user).order_by('-created_at').first()
        if not report:
            messages.warning(request, 'No assessment report found. Please complete an assessment first.')
            return redirect('assessment')
        
        # Get career recommendations
        recommendations = CareerRecommendation.objects.filter(user=request.user).order_by('-confidence_score')
        
        if not recommendations.exists():
            messages.warning(request, 'No career recommendations found. Please complete an assessment first.')
            return redirect('assessment')
        
        # Generate PDF using ReportLab
        from .pdf_generator import generate_pdf_report
        pdf_buffer = generate_pdf_report(request.user, report, recommendations)
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="career_assessment_report.pdf"'
        
        logger.info(f"PDF report downloaded by user: {request.user.username}")
        return response
        
    except ImportError as e:
        logger.error(f"ReportLab import error: {str(e)}")
        messages.error(request, 'PDF generation library not available. Please contact administrator.')
        return redirect('recommendations')
    
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        messages.error(request, f'Error generating PDF report: {str(e)}')
        return redirect('recommendations')


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            messages.success(request, 'Registration successful! Please log in.')
            logger.info(f"New user registered: {user.username}")
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})
