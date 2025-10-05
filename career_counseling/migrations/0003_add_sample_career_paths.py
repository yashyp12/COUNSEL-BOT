from django.db import migrations

def add_sample_career_paths(apps, schema_editor):
    CareerPath = apps.get_model('career_counseling', 'CareerPath')
    
    # Technology Careers
    CareerPath.objects.create(
        title="Software Developer",
        description="Design and develop software applications and systems",
        required_skills={
            "technical": ["Programming", "Problem Solving", "System Design"],
            "soft": ["Communication", "Teamwork", "Time Management"]
        },
        education_requirements={
            "minimum": "Bachelor's Degree in Computer Science or related field",
            "preferred": "Master's Degree in Software Engineering"
        },
        average_salary="$85,000 - $120,000",
        job_outlook="Strong growth expected with increasing demand for software solutions"
    )
    
    CareerPath.objects.create(
        title="Data Scientist",
        description="Analyze complex data sets to help organizations make better decisions",
        required_skills={
            "technical": ["Statistics", "Machine Learning", "Data Analysis"],
            "soft": ["Critical Thinking", "Communication", "Business Acumen"]
        },
        education_requirements={
            "minimum": "Bachelor's Degree in Statistics, Mathematics, or Computer Science",
            "preferred": "Master's Degree in Data Science"
        },
        average_salary="$90,000 - $130,000",
        job_outlook="High demand with growing importance of data-driven decision making"
    )
    
    # Healthcare Careers
    CareerPath.objects.create(
        title="Healthcare Administrator",
        description="Manage healthcare facilities and coordinate medical services",
        required_skills={
            "technical": ["Healthcare Systems", "Financial Management", "Regulatory Compliance"],
            "soft": ["Leadership", "Communication", "Problem Solving"]
        },
        education_requirements={
            "minimum": "Bachelor's Degree in Healthcare Administration",
            "preferred": "Master's Degree in Healthcare Management"
        },
        average_salary="$70,000 - $100,000",
        job_outlook="Steady growth with increasing healthcare needs"
    )
    
    # Creative Careers
    CareerPath.objects.create(
        title="UX/UI Designer",
        description="Design user-friendly interfaces and experiences for digital products",
        required_skills={
            "technical": ["Design Tools", "User Research", "Prototyping"],
            "soft": ["Creativity", "Communication", "Empathy"]
        },
        education_requirements={
            "minimum": "Bachelor's Degree in Design or related field",
            "preferred": "Master's Degree in Human-Computer Interaction"
        },
        average_salary="$75,000 - $110,000",
        job_outlook="Growing demand with focus on user experience"
    )

def remove_sample_career_paths(apps, schema_editor):
    CareerPath = apps.get_model('career_counseling', 'CareerPath')
    CareerPath.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('career_counseling', '0002_add_sample_questions'),
    ]

    operations = [
        migrations.RunPython(add_sample_career_paths, remove_sample_career_paths),
    ] 