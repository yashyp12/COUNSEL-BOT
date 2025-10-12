from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .models import Question, UserResponse, CareerRecommendation, AssessmentReport, UserProfile, CareerPath
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
import json
from django.template.loader import render_to_string
import pdfkit
import os

def home(request):
    return render(request, 'home.html')

@login_required
def profile(request):
    user_responses = UserResponse.objects.filter(user=request.user).order_by('-created_at')
    career_recommendations = CareerRecommendation.objects.filter(user=request.user).order_by('-confidence_score')
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Calculate profile completion
    total_fields = 4  # first_name, last_name, education_level, field_of_study
    completed_fields = sum([
        bool(request.user.first_name),
        bool(request.user.last_name),
        bool(profile.education_level),
        bool(profile.field_of_study)
    ])
    profile_completion = (completed_fields / total_fields) * 100
    
    context = {
        'user_responses': user_responses[:5],  # Limit to 5 most recent
        'career_recommendations': career_recommendations[:5],  # Limit to top 5
        'profile_completion': int(profile_completion),
        'profile': profile  # Add profile to context
    }
    return render(request, 'profile.html', context)

@login_required
def assessment(request):
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
            
            return JsonResponse({'status': 'success', 'message': 'Assessment completed successfully'})
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error', 
                'message': 'Invalid data format. Please try again.'
            }, status=400)
        except Question.DoesNotExist:
            return JsonResponse({
                'status': 'error', 
                'message': 'Invalid question ID'
            }, status=400)
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Assessment submission error for user {request.user.id}: {str(e)}')
            return JsonResponse({
                'status': 'error', 
                'message': 'An error occurred while processing your assessment. Please try again.'
            }, status=500)
    
    # Get questions for assessment
    questions = Question.objects.all().order_by('?')[:10]
    return render(request, 'assessment.html', {'questions': questions})

def generate_recommendations(user):
    # Get user's responses
    responses = UserResponse.objects.filter(user=user)
    
    # Analyze responses and generate recommendations
    skill_analysis = analyze_skills(responses)
    interest_analysis = analyze_interests(responses)
    personality_insights = analyze_personality(responses)
    
    # Get career paths
    career_paths = CareerPath.objects.all()
    
    # Delete old recommendations to avoid duplicates
    CareerRecommendation.objects.filter(user=user).delete()
    
    # Generate recommendations based on analysis
    recommendations = []
    for career_path in career_paths:
        confidence_score = calculate_career_match(
            career_path,
            skill_analysis,
            interest_analysis,
            personality_insights
        )
        
        if confidence_score > 0.5:  # Only recommend careers with >50% match
            recommendation = CareerRecommendation.objects.create(
                user=user,
                career_path=career_path,
                confidence_score=confidence_score,
                reasoning=generate_recommendation_reasoning(
                    career_path,
                    skill_analysis,
                    interest_analysis,
                    personality_insights
                )
            )
            recommendations.append(recommendation)
    
    # Create assessment report
    AssessmentReport.objects.create(
        user=user,
        skill_analysis=skill_analysis,
        interest_analysis=interest_analysis,
        personality_insights=personality_insights
    )

def analyze_skills(responses):
    # Initialize skill categories
    skills = {
        "Problem Solving": 0,
        "Communication": 0,
        "Technical": 0,
        "Leadership": 0,
        "Creativity": 0
    }
    
    # Map questions to skill categories
    skill_mapping = {
        "How would you rate your problem-solving abilities?": {
            "Excellent": {"Problem Solving": 100},
            "Good": {"Problem Solving": 75},
            "Average": {"Problem Solving": 50},
            "Needs Improvement": {"Problem Solving": 25}
        },
        "How comfortable are you with public speaking?": {
            "Very Comfortable": {"Communication": 100},
            "Somewhat Comfortable": {"Communication": 75},
            "Neutral": {"Communication": 50},
            "Uncomfortable": {"Communication": 25}
        }
    }
    
    # Analyze responses
    for response in responses:
        if response.question.question_text in skill_mapping:
            skill_scores = skill_mapping[response.question.question_text].get(response.response_text, {})
            for skill, score in skill_scores.items():
                skills[skill] = score
    
    return skills

def analyze_interests(responses):
    # Initialize interest categories
    interests = {
        "Technology": 0,
        "Healthcare": 0,
        "Business": 0,
        "Creative": 0
    }
    
    # Map questions to interest categories
    interest_mapping = {
        "Which of these activities interests you the most?": {
            "Working with Technology": {"Technology": 100},
            "Helping People": {"Healthcare": 100},
            "Creative Arts": {"Creative": 100},
            "Business and Finance": {"Business": 100}
        },
        "What type of work environment do you prefer?": {
            "Office Setting": {"Business": 75, "Technology": 75},
            "Laboratory": {"Technology": 100, "Healthcare": 75},
            "Creative Studio": {"Creative": 100},
            "Outdoor/Field Work": {"Healthcare": 100}
        }
    }
    
    # Analyze responses
    for response in responses:
        if response.question.question_text in interest_mapping:
            interest_scores = interest_mapping[response.question.question_text].get(response.response_text, {})
            for interest, score in interest_scores.items():
                interests[interest] = max(interests[interest], score)
    
    return interests

def analyze_personality(responses):
    # Initialize personality traits
    personality = {
        "Analytical": 0,
        "Creative": 0,
        "Leadership": 0,
        "Teamwork": 0
    }
    
    # Map questions to personality traits
    personality_mapping = {
        "How do you typically handle stress?": {
            "Stay Calm and Focused": {"Analytical": 100},
            "Take a Break and Reorganize": {"Creative": 75},
            "Seek Support": {"Teamwork": 100},
            "Work Through It": {"Leadership": 75}
        },
        "What's your preferred work style?": {
            "Independent": {"Analytical": 100},
            "Team Collaboration": {"Teamwork": 100},
            "Mixed": {"Creative": 75, "Teamwork": 75},
            "Leadership Role": {"Leadership": 100}
        }
    }
    
    # Analyze responses
    for response in responses:
        if response.question.question_text in personality_mapping:
            trait_scores = personality_mapping[response.question.question_text].get(response.response_text, {})
            for trait, score in trait_scores.items():
                personality[trait] = max(personality[trait], score)
    
    return personality

def calculate_career_match(career_path, skill_analysis, interest_analysis, personality_insights):
    # Define weights for different factors
    weights = {
        'skills': 0.4,
        'interests': 0.3,
        'personality': 0.3
    }
    
    # Calculate skill match
    skill_match = 0
    try:
        if isinstance(career_path.required_skills, dict):
            # Flatten all skills from the dict
            all_skills = []
            for skill_list in career_path.required_skills.values():
                if isinstance(skill_list, list):
                    all_skills.extend([s.lower() for s in skill_list])
            
            if all_skills:
                # Match user skills against required skills
                total_score = 0
                for skill_key, skill_value in skill_analysis.items():
                    skill_key_lower = skill_key.lower()
                    for req_skill in all_skills:
                        if skill_key_lower in req_skill or req_skill in skill_key_lower:
                            total_score += skill_value
                            break
                skill_match = min(total_score / (len(all_skills) * 100), 1.0)
    except (AttributeError, TypeError):
        skill_match = 0.5  # Default to neutral if there's an error
    
    # Calculate interest match based on career title and description
    interest_match = 0
    career_title_lower = career_path.title.lower()
    if "software" in career_title_lower or "developer" in career_title_lower or "engineer" in career_title_lower:
        interest_match = interest_analysis.get("Technology", 0) / 100
    elif "healthcare" in career_title_lower or "medical" in career_title_lower or "nurse" in career_title_lower:
        interest_match = interest_analysis.get("Healthcare", 0) / 100
    elif "business" in career_title_lower or "finance" in career_title_lower or "manager" in career_title_lower:
        interest_match = interest_analysis.get("Business", 0) / 100
    elif "designer" in career_title_lower or "creative" in career_title_lower or "artist" in career_title_lower:
        interest_match = interest_analysis.get("Creative", 0) / 100
    else:
        # Default to average of all interests
        interest_match = sum(interest_analysis.values()) / (len(interest_analysis) * 100) if interest_analysis else 0.5
    
    # Calculate personality match
    personality_match = sum(personality_insights.values()) / (len(personality_insights) * 100) if personality_insights else 0.5
    
    # Calculate overall match score
    match_score = (
        weights['skills'] * skill_match +
        weights['interests'] * interest_match +
        weights['personality'] * personality_match
    )
    
    return match_score * 100  # Convert to percentage

def generate_recommendation_reasoning(career_path, skill_analysis, interest_analysis, personality_insights):
    reasons = []
    
    # Add skill-based reasons
    matching_skills = []
    try:
        if isinstance(career_path.required_skills, dict):
            for skill_type, skills in career_path.required_skills.items():
                if isinstance(skills, list):
                    for skill in skills:
                        # Check if user has this skill with a high score
                        for user_skill, score in skill_analysis.items():
                            if score >= 75 and (skill.lower() in user_skill.lower() or user_skill.lower() in skill.lower()):
                                matching_skills.append(skill)
    except (AttributeError, TypeError):
        pass
    
    if matching_skills:
        reasons.append(f"You have strong skills in {', '.join(matching_skills[:3])}, which are essential for this role.")
    
    # Add interest-based reasons
    career_interests = []
    career_title_lower = career_path.title.lower()
    if "software" in career_title_lower or "developer" in career_title_lower:
        if interest_analysis.get("Technology", 0) >= 75:
            career_interests.append("technology")
    elif "healthcare" in career_title_lower:
        if interest_analysis.get("Healthcare", 0) >= 75:
            career_interests.append("healthcare")
    elif "business" in career_title_lower:
        if interest_analysis.get("Business", 0) >= 75:
            career_interests.append("business")
    elif "designer" in career_title_lower:
        if interest_analysis.get("Creative", 0) >= 75:
            career_interests.append("creative work")
    
    if career_interests:
        reasons.append(f"Your strong interest in {', '.join(career_interests)} aligns well with this career path.")
    
    # Add personality-based reasons
    strong_traits = [trait for trait, score in personality_insights.items() if score >= 75]
    if strong_traits:
        reasons.append(f"Your {', '.join(strong_traits[:2]).lower()} traits would be valuable in this role.")
    
    # Add education and outlook
    try:
        if isinstance(career_path.education_requirements, dict) and 'minimum' in career_path.education_requirements:
            reasons.append(f"With the required {career_path.education_requirements['minimum']}, you can enter this field.")
    except (AttributeError, TypeError, KeyError):
        pass
    
    if career_path.job_outlook:
        reasons.append(f"Career outlook: {career_path.job_outlook}")
    
    return " ".join(reasons) if reasons else "This career matches your profile based on your assessment responses."

@login_required
def recommendations(request):
    recommendations = CareerRecommendation.objects.filter(user=request.user).order_by('-confidence_score')
    if not recommendations.exists():
        messages.warning(request, 'Please complete the assessment to get career recommendations.')
        return redirect('assessment')
    
    # Get the latest assessment report
    report = AssessmentReport.objects.filter(user=request.user).order_by('-created_at').first()
    
    # Ensure we have data to display
    skill_analysis = report.skill_analysis if report and report.skill_analysis else {}
    interest_analysis = report.interest_analysis if report and report.interest_analysis else {}
    personality_insights = report.personality_insights if report and report.personality_insights else {}
    
    context = {
        'recommendations': recommendations[:10],  # Limit to top 10 recommendations
        'report': report,
        'skill_analysis': skill_analysis,
        'interest_analysis': interest_analysis,
        'personality_insights': personality_insights
    }
    return render(request, 'recommendations.html', context)

@login_required
def assessment_detail(request, response_id):
    response = UserResponse.objects.get(id=response_id, user=request.user)
    return render(request, 'assessment_detail.html', {'response': response})

@login_required
def career_detail(request, career_id):
    recommendation = CareerRecommendation.objects.get(
        user=request.user,
        career_path_id=career_id
    )
    return render(request, 'career_detail.html', {'recommendation': recommendation})

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Set additional fields
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()
            
            # Create user profile
            UserProfile.objects.create(user=user)
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def download_report(request):
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
    
    # Prepare context for PDF
    context = {
        'user': request.user,
        'report': report,
        'recommendations': recommendations,
        'skill_analysis': report.skill_analysis,
        'interest_analysis': report.interest_analysis,
        'personality_insights': report.personality_insights
    }
    
    try:
        # Render the PDF template
        html_string = render_to_string('pdf/assessment_report.html', context)
        
        # Configure PDF options
        options = {
            'page-size': 'Letter',
            'encoding': 'UTF-8',
            'custom-header': [
                ('Accept-Encoding', 'gzip')
            ],
            'no-outline': None,
            'quiet': ''
        }
        
        # Configure pdfkit with proper wkhtmltopdf path
        config = None
        try:
            # Try to find wkhtmltopdf in common locations
            import subprocess
            wkhtmltopdf_path = subprocess.check_output(['which', 'wkhtmltopdf']).decode().strip()
            config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        except Exception:
            # If which command fails, try default path
            if os.path.exists('/usr/bin/wkhtmltopdf'):
                config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
        
        # Create PDF
        pdf = pdfkit.from_string(html_string, False, options=options, configuration=config)
        
        # Create response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="career_assessment_report.pdf"'
        
        return response
    except OSError as e:
        messages.error(request, 'PDF generation failed: wkhtmltopdf is not installed or not accessible. Please contact administrator.')
        return redirect('recommendations')
    except Exception as e:
        messages.error(request, f'Error generating PDF report: {str(e)}. Please try again or contact support.')
        return redirect('recommendations') 