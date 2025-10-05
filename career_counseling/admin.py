from django.contrib import admin
from .models import UserProfile, Question, UserResponse, CareerPath, CareerRecommendation, AssessmentReport

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'education_level', 'field_of_study', 'created_at')
    search_fields = ('user__username', 'field_of_study')
    list_filter = ('education_level', 'created_at')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'question_type', 'weight', 'created_at')
    list_filter = ('question_type', 'created_at')
    search_fields = ('question_text',)

@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'question__question_text')

@admin.register(CareerPath)
class CareerPathAdmin(admin.ModelAdmin):
    list_display = ('title', 'average_salary', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)

@admin.register(CareerRecommendation)
class CareerRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'career_path', 'confidence_score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'career_path__title')

@admin.register(AssessmentReport)
class AssessmentReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',) 