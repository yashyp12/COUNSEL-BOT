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
        'user_responses': user_responses,
        'career_recommendations': career_recommendations,
        'profile_completion': profile_completion
    }
    return render(request, 'profile.html', context)

@login_required
def assessment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            responses = data.get('responses', [])
            
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
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
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
    required_skills = set([skill.lower() for skills in career_path.required_skills.values() for skill in skills])
    skill_match = sum(skill_analysis.get(skill, 0) for skill in required_skills) / (len(required_skills) * 100)
    
    # Calculate interest match based on career title and description
    interest_match = 0
    if "software" in career_path.title.lower() or "developer" in career_path.title.lower():
        interest_match = interest_analysis.get("Technology", 0) / 100
    elif "healthcare" in career_path.title.lower() or "medical" in career_path.title.lower():
        interest_match = interest_analysis.get("Healthcare", 0) / 100
    elif "business" in career_path.title.lower() or "finance" in career_path.title.lower():
        interest_match = interest_analysis.get("Business", 0) / 100
    elif "designer" in career_path.title.lower() or "creative" in career_path.title.lower():
        interest_match = interest_analysis.get("Creative", 0) / 100
    
    # Calculate personality match
    personality_match = sum(personality_insights.values()) / (len(personality_insights) * 100)
    
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
    for skill_type, skills in career_path.required_skills.items():
        for skill in skills:
            if skill_analysis.get(skill, 0) >= 75:
                matching_skills.append(skill)
    
    if matching_skills:
        reasons.append(f"You have strong skills in {', '.join(matching_skills)}, which are essential for this role.")
    
    # Add interest-based reasons
    career_interests = []
    if "software" in career_path.title.lower() or "developer" in career_path.title.lower():
        if interest_analysis.get("Technology", 0) >= 75:
            career_interests.append("technology")
    elif "healthcare" in career_path.title.lower():
        if interest_analysis.get("Healthcare", 0) >= 75:
            career_interests.append("healthcare")
    elif "business" in career_path.title.lower():
        if interest_analysis.get("Business", 0) >= 75:
            career_interests.append("business")
    elif "designer" in career_path.title.lower():
        if interest_analysis.get("Creative", 0) >= 75:
            career_interests.append("creative work")
    
    if career_interests:
        reasons.append(f"Your strong interest in {', '.join(career_interests)} aligns well with this career path.")
    
    # Add personality-based reasons
    strong_traits = [trait for trait, score in personality_insights.items() if score >= 75]
    if strong_traits:
        reasons.append(f"Your {', '.join(strong_traits).lower()} traits would be valuable in this role.")
    
    # Add education and outlook
    reasons.append(f"With the required {career_path.education_requirements['minimum']}, you can enter this field.")
    reasons.append(f"Career outlook: {career_path.job_outlook}")
    
    return " ".join(reasons)

@login_required
def recommendations(request):
    recommendations = CareerRecommendation.objects.filter(user=request.user).order_by('-confidence_score')
    if not recommendations.exists():
        messages.warning(request, 'Please complete the assessment to get career recommendations.')
        return redirect('assessment')
    
    # Get the latest assessment report
    report = AssessmentReport.objects.filter(user=request.user).order_by('-created_at').first()
    
    context = {
        'recommendations': recommendations,
        'report': report,
        'skill_analysis': report.skill_analysis if report else {},
        'interest_analysis': report.interest_analysis if report else {},
        'personality_insights': report.personality_insights if report else {}
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
        messages.warning(request, 'No assessment report found.')
        return redirect('assessment')
    
    # Get career recommendations
    recommendations = CareerRecommendation.objects.filter(user=request.user).order_by('-confidence_score')
    
    # Prepare context for PDF
    context = {
        'user': request.user,
        'report': report,
        'recommendations': recommendations,
        'skill_analysis': report.skill_analysis,
        'interest_analysis': report.interest_analysis,
        'personality_insights': report.personality_insights
    }
    
    # Render the PDF template
    html_string = render_to_string('pdf/assessment_report.html', context)
    
    # Configure PDF options
    options = {
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'no-outline': None
    }
    
    # Create PDF
    pdf = pdfkit.from_string(html_string, False, options=options)
    
    # Create response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="career_assessment_report.pdf"'
    
    return response 