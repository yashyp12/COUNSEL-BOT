from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView,
    UserProfileViewSet,
    QuestionViewSet,
    UserResponseViewSet,
    CareerRecommendationView
)

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'responses', UserResponseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('recommendations/', CareerRecommendationView.as_view(), name='career-recommendations'),
] 