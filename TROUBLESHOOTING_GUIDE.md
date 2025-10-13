# CounselBot - Comprehensive Troubleshooting Guide

## 📋 Table of Contents
1. [Critical System Failures](#critical-system-failures)
2. [PDF Generation Issues](#pdf-generation-issues)
3. [User Registration Problems](#user-registration-problems)
4. [Profile Management Issues](#profile-management-issues)
5. [Assessment Submission Errors](#assessment-submission-errors)
6. [Database Issues](#database-issues)
7. [Authentication & Login Problems](#authentication--login-problems)
8. [Frontend & UI Issues](#frontend--ui-issues)
9. [Performance Problems](#performance-problems)
10. [Deployment Issues](#deployment-issues)

---

## Critical System Failures

### 🚨 Application Won't Start

#### Symptom
```bash
python manage.py runserver
# Error: ModuleNotFoundError: No module named 'django'
```

#### Solution
```bash
# 1. Verify virtual environment is activated
which python  # Should show path with 'venv'

# 2. If not activated, activate it
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. Reinstall dependencies
pip install -r requirements.txt

# 4. Verify installation
python -c "import django; print(django.get_version())"
```

---

## PDF Generation Issues

### 🔴 CRITICAL: "wkhtmltopdf is not installed or not accessible"

This is the **#1 most common blocking issue** for PDF generation.

#### Symptoms
- PDF download button fails
- Error message: "PDF generation failed"
- Error in logs: "OSError: No wkhtmltopdf executable found"

#### Root Causes
1. wkhtmltopdf not installed
2. wkhtmltopdf not in system PATH
3. Incorrect wkhtmltopdf path in Django
4. File permissions issues

#### Complete Solution

**Step 1: Install wkhtmltopdf**

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y wkhtmltopdf

# Verify installation
which wkhtmltopdf
# Expected output: /usr/bin/wkhtmltopdf

wkhtmltopdf --version
# Expected output: wkhtmltopdf 0.12.6
```

**macOS:**
```bash
brew install wkhtmltopdf

# Verify installation
which wkhtmltopdf
# Expected output: /usr/local/bin/wkhtmltopdf
```

**Windows:**
1. Download from: https://wkhtmltopdf.org/downloads.html
2. Install MSI package (choose "Add to PATH")
3. Restart terminal
4. Verify:
   ```cmd
   where wkhtmltopdf
   wkhtmltopdf --version
   ```

**Step 2: Verify Django Can Find It**

```bash
python manage.py shell
```

```python
import subprocess
import os

# Test 1: Check if wkhtmltopdf is in PATH
try:
    result = subprocess.run(['which', 'wkhtmltopdf'], 
                          capture_output=True, text=True)
    print("wkhtmltopdf path:", result.stdout.strip())
except Exception as e:
    print("Error:", e)

# Test 2: Test wkhtmltopdf directly
try:
    result = subprocess.run(['wkhtmltopdf', '--version'], 
                          capture_output=True, text=True)
    print("Version:", result.stdout)
except Exception as e:
    print("Error:", e)

# Test 3: Check common paths
common_paths = [
    '/usr/bin/wkhtmltopdf',
    '/usr/local/bin/wkhtmltopdf',
    'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
]
for path in common_paths:
    if os.path.exists(path):
        print(f"Found at: {path}")

exit()
```

**Step 3: Test PDF Generation**

```bash
python manage.py shell
```

```python
import pdfkit

# Test basic PDF generation
html_content = '<html><body><h1>Test PDF</h1></body></html>'

try:
    # Generate PDF
    pdf = pdfkit.from_string(html_content, False)
    print(f"✅ Success! Generated PDF of {len(pdf)} bytes")
except OSError as e:
    print(f"❌ OSError: {e}")
    print("wkhtmltopdf is not properly installed")
except Exception as e:
    print(f"❌ Error: {e}")

exit()
```

**Step 4: Configure Django Settings (If Needed)**

If wkhtmltopdf is in a non-standard location, add to `counselbot/settings.py`:

```python
# At the bottom of settings.py
WKHTMLTOPDF_CMD = '/path/to/wkhtmltopdf'  # Custom path
```

**Step 5: Test End-to-End**

1. Log in to application
2. Complete an assessment
3. Go to recommendations page
4. Click "Download Report"
5. PDF should download successfully

#### Alternative Solution: Use Different PDF Library

If wkhtmltopdf continues to cause issues, consider alternatives:

```bash
# Option 1: WeasyPrint (pure Python)
pip install WeasyPrint

# Option 2: ReportLab (more control)
pip install reportlab

# Update views.py to use alternative library
```

---

### PDF Generation Produces Empty or Broken PDF

#### Symptoms
- PDF downloads but won't open
- PDF is 0 bytes or very small
- PDF viewer shows error

#### Solutions

**Check Template Rendering:**
```bash
python manage.py shell
```

```python
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from career_counseling.models import AssessmentReport, CareerRecommendation

# Get a test user
user = User.objects.first()

# Get report data
report = AssessmentReport.objects.filter(user=user).first()
recommendations = CareerRecommendation.objects.filter(user=user)

# Test template rendering
context = {
    'user': user,
    'report': report,
    'recommendations': recommendations,
}

try:
    html = render_to_string('pdf/assessment_report.html', context)
    print(f"✅ Template rendered: {len(html)} characters")
    print("First 200 chars:", html[:200])
except Exception as e:
    print(f"❌ Template error: {e}")

exit()
```

**Check for Template Errors:**
- Verify `templates/pdf/assessment_report.html` exists
- Check for undefined variables in template
- Test with minimal template first

---

### PDF Generation Times Out

#### Symptoms
- Request hangs for >30 seconds
- Eventually returns 504 or 500 error
- Server logs show timeout

#### Solutions

```python
# In career_counseling/frontend_views.py
# Adjust pdfkit options for faster generation

options = {
    'page-size': 'Letter',
    'encoding': 'UTF-8',
    'quiet': '',
    'enable-local-file-access': None,
    # Add these for faster generation:
    'disable-javascript': None,
    'no-images': None,  # Remove if images needed
    'lowquality': None,  # Faster but lower quality
}
```

---

## User Registration Problems

### 🔴 "A user with that username already exists" (False Positives)

#### Symptoms
- New users can't register
- Error appears even with unique username
- Database shows username doesn't exist

#### Root Cause Analysis

This was a **critical bug** that has been **FIXED** in the latest version. The fix is in `career_counseling/serializers.py`:

```python
class UserRegistrationSerializer(serializers.ModelSerializer):
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with that username already exists."
            )
        return value
```

#### Verify Fix is Applied

```bash
# Check serializers.py has validation
grep -A 3 "validate_username" career_counseling/serializers.py
```

Expected output:
```python
def validate_username(self, value):
    if User.objects.filter(username=value).exists():
        raise serializers.ValidationError("A user with that username already exists.")
    return value
```

#### If Issue Persists

**Test in Django shell:**
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

# Check if username exists
username = "testuser123"
exists = User.objects.filter(username=username).exists()
print(f"Username '{username}' exists: {exists}")

# If exists, view user
if exists:
    user = User.objects.get(username=username)
    print(f"User ID: {user.id}")
    print(f"Date joined: {user.date_joined}")
    print(f"Active: {user.is_active}")

exit()
```

**Clear test users:**
```python
from django.contrib.auth.models import User

# Delete test users (CAUTION: Only in development!)
User.objects.filter(username__startswith='test').delete()

exit()
```

---

### Registration Form Submission Fails

#### Symptoms
- Form submits but nothing happens
- JavaScript console shows errors
- Page reloads without registration

#### Check Browser Console (F12)

Common errors:
- `403 Forbidden` → CSRF token issue
- `400 Bad Request` → Invalid data format
- `500 Internal Server Error` → Backend error

#### Solution for CSRF Errors

Verify `templates/registration/register.html` includes:

```javascript
// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}

// Include in AJAX request
$.ajax({
    url: '/api/register/',
    method: 'POST',
    contentType: 'application/json',
    headers: {
        'X-CSRFToken': getCookie('csrftoken')
    },
    data: JSON.stringify(formData),
    // ...
});
```

---

### Email Validation Fails

#### Symptoms
- "A user with that email already exists" error
- Email format rejected

#### Solutions

**Check email validation:**
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

# Check if email exists
email = "test@example.com"
exists = User.objects.filter(email=email).exists()
print(f"Email '{email}' exists: {exists}")

# Django allows duplicate emails by default
# Our serializer should prevent this
exit()
```

**Verify serializer validation:**
```bash
grep -A 3 "validate_email" career_counseling/serializers.py
```

Expected:
```python
def validate_email(self, value):
    if User.objects.filter(email=value).exists():
        raise serializers.ValidationError("A user with that email already exists.")
    return value
```

---

## Profile Management Issues

### 🔴 Profile Data Not Saving/Updating

#### Symptoms
- Profile form submits but data doesn't save
- Changes revert after page reload
- No error messages shown

#### Root Cause

This was **FIXED** in `career_counseling/serializers.py` with proper `update()` method:

```python
class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    
    def update(self, instance, validated_data):
        # Extract user fields
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        
        # Update user fields
        if first_name is not None:
            instance.user.first_name = first_name
        if last_name is not None:
            instance.user.last_name = last_name
        if first_name is not None or last_name is not None:
            instance.user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
```

#### Verify Fix

```bash
# Check serializers.py
grep -A 20 "class UserProfileSerializer" career_counseling/serializers.py
```

#### Test Profile Update

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from career_counseling.models import UserProfile

# Get a user
user = User.objects.first()
profile = user.userprofile

# Update profile
profile.education_level = "Bachelor's Degree"
profile.field_of_study = "Computer Science"
profile.save()

# Update user
user.first_name = "John"
user.last_name = "Doe"
user.save()

print("✅ Profile updated successfully")
print(f"Name: {user.get_full_name()}")
print(f"Education: {profile.education_level}")

exit()
```

---

### Profile Not Created for New Users

#### Symptoms
- `DoesNotExist: UserProfile matching query does not exist`
- Profile page shows error

#### Solution

Verify signal is working in `career_counseling/signals.py`:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
```

Verify signals are registered in `career_counseling/apps.py`:

```python
class CareerCounselingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'career_counseling'

    def ready(self):
        import career_counseling.signals
```

---

## Assessment Submission Errors

### 🔴 "Error submitting responses" Despite Successful Submission

#### Symptoms
- Assessment submits successfully
- Backend saves data
- Frontend shows error message
- User confused about status

#### Root Cause

This was **FIXED** by:
1. Removing duplicate submission handlers
2. Proper status code checking in JavaScript
3. Better error handling

#### Verify Fix

Check `templates/assessment.html` has only ONE submission handler:

```javascript
$('#assessment-form').on('submit', function(e) {
    e.preventDefault();
    
    // ... collection code ...
    
    $.ajax({
        url: '/assessment/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ responses: responses }),
        success: function(response) {
            // Check if response indicates success
            if (response.status === 'success') {
                showAlert('Assessment completed successfully!', 'success');
                setTimeout(() => {
                    window.location.href = '/recommendations/';
                }, 1500);
            }
        },
        error: function(xhr) {
            // Proper error handling
            let errorMsg = 'Error submitting assessment';
            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMsg = xhr.responseJSON.message;
            }
            showAlert(errorMsg, 'danger');
        }
    });
});
```

Check `static/js/main.js` does NOT have duplicate handler:

```bash
grep -n "submitAssessment" static/js/main.js
# Should NOT have assessment submission code
```

---

### Assessment Questions Not Loading

#### Symptoms
- Assessment page is blank
- No questions displayed
- Console shows no errors

#### Solutions

**Check database has questions:**
```bash
python manage.py shell
```

```python
from career_counseling.models import Question

count = Question.objects.count()
print(f"Total questions in database: {count}")

if count == 0:
    print("❌ No questions found! Need to add questions.")
else:
    print("✅ Questions exist")
    # Show first few
    for q in Question.objects.all()[:3]:
        print(f"- {q.question_text}")

exit()
```

**Add sample questions:**
```python
from career_counseling.models import Question

questions = [
    "What is your preferred work environment?",
    "Do you enjoy working with people or independently?",
    "What are your strongest skills?",
    # Add more...
]

for q_text in questions:
    Question.objects.get_or_create(
        question_text=q_text,
        defaults={
            'question_type': 'multiple_choice',
            'options': ['Option 1', 'Option 2', 'Option 3']
        }
    )

print(f"✅ Created {len(questions)} questions")
exit()
```

---

## Database Issues

### Database Locked Error

#### Symptoms
```
sqlite3.OperationalError: database is locked
```

#### Solutions

**Quick fix:**
```bash
# Stop all Django processes
pkill -f "python manage.py runserver"

# Wait a moment
sleep 2

# Restart server
python manage.py runserver
```

**Permanent fix - Use proper database:**
```bash
# For production, use PostgreSQL or MySQL
# Update settings.py:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'counselbot',
        'USER': 'counselbot_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

### Migration Conflicts

#### Symptoms
```
Conflicting migrations detected
```

#### Solution

```bash
# Show migration status
python manage.py showmigrations

# If conflicts, reset migrations (DEVELOPMENT ONLY!)
# Backup database first!
cp db.sqlite3 db.sqlite3.backup

# Delete all migrations except __init__.py
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate fresh migrations
python manage.py makemigrations
python manage.py migrate
```

---

## Authentication & Login Problems

### Can't Log In After Registration

#### Solutions

**Reset password via Django shell:**
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

username = "your_username"
user = User.objects.get(username=username)

# Set new password
user.set_password("new_password")
user.save()

print(f"✅ Password reset for {username}")
exit()
```

**Check user is active:**
```python
from django.contrib.auth.models import User

user = User.objects.get(username="your_username")
print(f"Active: {user.is_active}")
print(f"Staff: {user.is_staff}")

if not user.is_active:
    user.is_active = True
    user.save()
    print("✅ User activated")

exit()
```

---

### Session Expires Too Quickly

#### Solution

Add to `counselbot/settings.py`:

```python
# Session settings
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
```

---

## Frontend & UI Issues

### CSS Not Loading

#### Check static files:
```bash
python manage.py collectstatic --noinput

# Verify files exist
ls -la staticfiles/css/
ls -la staticfiles/js/
```

#### Check template includes:
```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
```

---

### JavaScript Errors in Console

#### Common errors and fixes:

**"$ is not defined"**
- jQuery not loaded
- Check `<script src="{% static 'js/jquery.min.js' %}"></script>`

**"CSRF token missing"**
- See CSRF token solutions above

**"Unexpected token in JSON"**
- Response is HTML instead of JSON
- Check API endpoint returns JSON

---

## Performance Problems

### Slow Page Loads

```python
# Add to settings.py for development debugging

# Django Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']

# Install
# pip install django-debug-toolbar
```

### Slow Assessment Processing

```python
# Optimize database queries in views
# Use select_related and prefetch_related

recommendations = CareerRecommendation.objects.filter(
    user=request.user
).select_related('career_path').order_by('-confidence_score')[:5]
```

---

## Deployment Issues

### Static Files Not Serving in Production

```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Use whitenoise
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... other middleware
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## Quick Diagnostic Commands

```bash
# Check Django configuration
python manage.py check

# Check database status
python manage.py showmigrations

# Check static files
python manage.py collectstatic --dry-run

# Test imports
python -c "from career_counseling import models, views, serializers"

# Check environment
pip list | grep -i django
python --version
which wkhtmltopdf
```

---

## Emergency Reset (Development Only)

If all else fails and you need to start fresh:

```bash
# Backup first!
cp db.sqlite3 db.sqlite3.backup
cp -r static static.backup

# Reset database
rm db.sqlite3

# Clear cache
rm -rf __pycache__ */__pycache__ */*/__pycache__
rm -rf staticfiles/*

# Fresh start
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

---

## Still Having Issues?

1. **Check logs carefully** - Read the full error message
2. **Search documentation** - Check README.md and other guides
3. **Test in isolation** - Use Django shell to test components
4. **Ask for help** - Create a GitHub issue with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Python version, etc.)
   - What you've already tried

---

**Remember:** Most issues are configuration or environment problems, not code bugs. Double-check your setup first!
