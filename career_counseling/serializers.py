from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile,
    Question,
    UserResponse,
    CareerPath,
    CareerRecommendation,
    AssessmentReport
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = '__all__'
        read_only_fields = ('response_vector',)

class CareerPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerPath
        fields = '__all__'

class CareerRecommendationSerializer(serializers.ModelSerializer):
    career_path = CareerPathSerializer(read_only=True)

    class Meta:
        model = CareerRecommendation
        fields = '__all__'

class AssessmentReportSerializer(serializers.ModelSerializer):
    recommendations = CareerRecommendationSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = AssessmentReport
        fields = '__all__'
        read_only_fields = ('report_file',)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password', 'first_name', 'last_name')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user 