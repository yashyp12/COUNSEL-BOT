"""
URL configuration for counselbot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from career_counseling import frontend_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('career_counseling.urls')),
    path('', frontend_views.home, name='home'),
    path('profile/', frontend_views.profile, name='profile'),
    path('assessment/', frontend_views.assessment, name='assessment'),
    path('recommendations/', frontend_views.recommendations, name='recommendations'),
    path('assessment/<int:assessment_id>/', frontend_views.assessment_detail, name='assessment_detail'),
    path('career/<int:career_id>/', frontend_views.career_detail, name='career_detail'),
    path('register/', frontend_views.register, name='register'),
    path('download-report/', frontend_views.download_report, name='download_report'),
    path('', include('django.contrib.auth.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
]