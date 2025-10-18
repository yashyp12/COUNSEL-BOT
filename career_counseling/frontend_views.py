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
    
    context = {
        'user_responses': user_responses[:5],
        'career_recommendations': career_recommendations[:5],
        'profile_completion': int(profile_completion),
        'profile': profile
    }
    return render(request, 'profile.html', context)


@login_required
def assessment(request):
    """Handle career assessment form submission and response storage"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            responses = data.get('responses', [])
            
            # Validate that we have responses
            if not responses:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'No responses provided. Please answer all questions.'
                }, status=400)
            
            # Validate each response has required fields
            for response_data in responses:
                if 'question_id' not in response_data or 'response' not in response_data:
                    return JsonResponse({
                        'status': 'error', 
                        'message': 'Invalid response format. Please try again.'
                    }, status=400)
                
                # Validate question exists
                if not Question.objects.filter(id=response_data.get('question_id')).exists():
                    return JsonResponse({
                        'status': 'error', 
                        'message': f'Invalid question ID: {response_data.get("question_id")}'
                    }, status=400)
            
            # Delete any existing responses for this user to avoid unique constraint errors
            UserResponse.objects.filter(user=request.user).delete()
            
            # Save user responses
            for response_data in responses:
                question_id = response_data.get('question_id')
                response_text = response_data.get('response')
                
                question = Question.objects.get(id=question_id)
                UserResponse.objects.create(
                    user=request.user,
                    question=question,
                    response_text=response_text
                )
            
            # Generate career recommendations
            generate_recommendations(request.user)
            
            logger.info(f"Assessment completed for user: {request.user.username}")
            return JsonResponse({'status': 'success', 'message': 'Assessment completed successfully'})
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON received in assessment submission")
            return JsonResponse({
                'status': 'error', 
                'message': 'Invalid data format. Please try again.'
            }, status=400)
        except Question.DoesNotExist:
            logger.error("Invalid question ID referenced in assessment")
            return JsonResponse({
                'status': 'error', 
                'message': 'Invalid question ID'
            }, status=400)
        except Exception as e:
            logger.error(f"Assessment error: {str(e)}")
            return JsonResponse({
                'status': 'error', 
                'message': f'Error saving assessment: {str(e)}'
            }, status=500)
    
    # GET request - show assessment form
    questions = Question.objects.all()
    return render(request, 'career_counseling/assessment.html', {'questions': questions})


def generate_recommendations(user):
    """Generate career recommendations based on user responses"""
    try:
        # Get user responses
        user_responses = UserResponse.objects.filter(user=user)
        
        if not user_responses.exists():
            logger.warning(f"No responses found for user {user.username}")
            return
        
        # Get all career paths
        career_paths = CareerPath.objects.all()
        
        # Clear existing recommendations
        CareerRecommendation.objects.filter(user=user).delete()
        
        # Score each career path
        for career_path in career_paths:
            score = calculate_career_score(user_responses, career_path)
            
            if score > 0:
                # Generate reasoning
                reasoning = generate_recommendation_reasoning(user_responses, career_path, score)
                
                CareerRecommendation.objects.create(
                    user=user,
                    career_path=career_path,
                    confidence_score=score,
                    reasoning=reasoning
                )
        
        # Generate or update assessment report
        generate_assessment_report(user)
        logger.info(f"Recommendations generated for user: {user.username}")
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")


def calculate_career_score(user_responses, career_path):
    """Calculate match score between user responses and career path"""
    try:
        total_score = 0
        response_count = user_responses.count()
        
        if response_count == 0:
            return 0
        
        required_skills = career_path.required_skills
        if isinstance(required_skills, str):
            required_skills = json.loads(required_skills)
        
        # Simple scoring: match keywords from responses with required skills
        for response in user_responses:
            response_lower = response.response_text.lower()
            for skill in required_skills:
                skill_lower = skill.lower()
                if skill_lower in response_lower:
                    total_score += 10
        
        # Normalize score to 0-1 range
        max_score = response_count * len(required_skills) * 10
        score = min(1.0, max(0.0, total_score / max_score if max_score > 0 else 0))
        
        return score
        
    except Exception as e:
        logger.error(f"Error calculating career score: {str(e)}")
        return 0


def generate_recommendation_reasoning(user_responses, career_path, score):
    """Generate explanation for why a career was recommended"""
    try:
        reasons = []
        
        # Get career path requirements
        required_skills = career_path.required_skills
        if isinstance(required_skills, str):
            required_skills = json.loads(required_skills)
        
        # Find matching skills from user responses
        matching_skills = []
        for response in user_responses:
            response_lower = response.response_text.lower()
            for skill in required_skills:
                if skill.lower() in response_lower and skill not in matching_skills:
                    matching_skills.append(skill)
        
        # Build reasoning text
        if matching_skills:
            reasons.append(f"You have strong skills in {', '.join(matching_skills[:3])}, which are essential for this role.")
        
        reasons.append(f"Your assessment responses align {int(score*100)}% with the requirements for this career path.")
        
        education_reqs = career_path.education_requirements
        if isinstance(education_reqs, str):
            education_reqs = json.loads(education_reqs)
        
        if education_reqs:
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
        
        # Create or update report
        report, created = AssessmentReport.objects.get_or_create(
            user=user,
            defaults={
                'skill_analysis': skill_analysis,
                'interest_analysis': interest_analysis,
                'personality_insights': personality_insights
            }
        )
        
        if not created:
            report.skill_analysis = skill_analysis
            report.interest_analysis = interest_analysis
            report.personality_insights = personality_insights
            report.save()
        
        logger.info(f"Assessment report generated for user: {user.username}")
        
    except Exception as e:
        logger.error(f"Error generating assessment report: {str(e)}")


@login_required
def recommendations(request):
    """Display career recommendations for the user"""
    try:
        recommendations = CareerRecommendation.objects.filter(user=request.user).order_by('-confidence_score')
        
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
    try:
        report = AssessmentReport.objects.get(id=assessment_id, user=request.user)
        recommendations = CareerRecommendation.objects.filter(user=request.user).order_by('-confidence_score')
        
        context = {
            'report': report,
            'recommendations': recommendations
        }
        return render(request, 'assessment_detail.html', context)
        
    except AssessmentReport.DoesNotExist:
        messages.error(request, 'Assessment not found')
        return redirect('profile')
    except Exception as e:
        logger.error(f"Error loading assessment detail: {str(e)}")
        messages.error(request, 'Error loading assessment details')
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
