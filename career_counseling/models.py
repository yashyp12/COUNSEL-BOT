from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    education_level = models.CharField(max_length=50, blank=True, null=True)
    field_of_study = models.CharField(max_length=100, blank=True, null=True)
    skills = models.JSONField(default=dict)
    interests = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Question(models.Model):
    QUESTION_TYPES = (
        ('SKILLS', 'Skills Assessment'),
        ('INTERESTS', 'Interest Assessment'),
        ('PERSONALITY', 'Personality Assessment'),
        ('SITUATION', 'Situational Assessment'),
    )

    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    options = models.JSONField(default=list)
    weight = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question_type}: {self.question_text[:50]}..."

class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response_text = models.TextField()
    response_vector = models.JSONField(null=True, blank=True)  # For NLP processed response
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'question']

    def __str__(self):
        return f"{self.user.username}'s response to {self.question.id}"

class CareerPath(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    required_skills = models.JSONField()
    education_requirements = models.JSONField()
    average_salary = models.CharField(max_length=50)
    job_outlook = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CareerRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    career_path = models.ForeignKey(CareerPath, on_delete=models.CASCADE)
    confidence_score = models.FloatField()
    reasoning = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-confidence_score']

    def __str__(self):
        return f"{self.career_path.title} recommendation for {self.user.username}"

class AssessmentReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommendations = models.ManyToManyField(CareerRecommendation)
    skill_analysis = models.JSONField()
    interest_analysis = models.JSONField()
    personality_insights = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    report_file = models.FileField(upload_to='reports/', null=True, blank=True)

    def __str__(self):
        return f"Career Assessment Report for {self.user.username}" 