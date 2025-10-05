from django.db import migrations

def add_sample_questions(apps, schema_editor):
    Question = apps.get_model('career_counseling', 'Question')
    
    # Skills Assessment Questions
    Question.objects.create(
        question_text="How would you rate your problem-solving abilities?",
        question_type="SKILLS",
        options=["Excellent", "Good", "Average", "Needs Improvement"],
        weight=1.0
    )
    
    Question.objects.create(
        question_text="How comfortable are you with public speaking?",
        question_type="SKILLS",
        options=["Very Comfortable", "Somewhat Comfortable", "Neutral", "Uncomfortable"],
        weight=1.0
    )
    
    # Interest Assessment Questions
    Question.objects.create(
        question_text="Which of these activities interests you the most?",
        question_type="INTERESTS",
        options=["Working with Technology", "Helping People", "Creative Arts", "Business and Finance"],
        weight=1.0
    )
    
    Question.objects.create(
        question_text="What type of work environment do you prefer?",
        question_type="INTERESTS",
        options=["Office Setting", "Outdoor/Field Work", "Creative Studio", "Laboratory"],
        weight=1.0
    )
    
    # Personality Assessment Questions
    Question.objects.create(
        question_text="How do you typically handle stress?",
        question_type="PERSONALITY",
        options=["Stay Calm and Focused", "Take a Break and Reorganize", "Seek Support", "Work Through It"],
        weight=1.0
    )
    
    Question.objects.create(
        question_text="What's your preferred work style?",
        question_type="PERSONALITY",
        options=["Independent", "Team Collaboration", "Mixed", "Leadership Role"],
        weight=1.0
    )
    
    # Situational Assessment Questions
    Question.objects.create(
        question_text="How would you handle a tight deadline?",
        question_type="SITUATION",
        options=["Create a Detailed Plan", "Work Extra Hours", "Delegate Tasks", "Negotiate Extension"],
        weight=1.0
    )
    
    Question.objects.create(
        question_text="What's your approach to learning new skills?",
        question_type="SITUATION",
        options=["Self-Study", "Formal Training", "Hands-on Practice", "Mentorship"],
        weight=1.0
    )

def remove_sample_questions(apps, schema_editor):
    Question = apps.get_model('career_counseling', 'Question')
    Question.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('career_counseling', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_sample_questions, remove_sample_questions),
    ] 