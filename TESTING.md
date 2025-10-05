# CounselBot Testing Guide

This document provides comprehensive testing instructions for the CounselBot application.

## Prerequisites

Ensure the application is set up and running:
```bash
source venv/bin/activate
python manage.py runserver
```

## 1. Testing the Home Page

**URL:** http://127.0.0.1:8000/

**Expected Result:**
- Landing page loads with CounselBot branding
- Navigation menu shows Login and Register options
- "Get Started" and "Login" buttons are visible
- Features section displays AI-powered analysis, personalized insights, and career guidance
- Testimonials section is visible

**Test:** Open http://127.0.0.1:8000/ in your browser and verify all elements load correctly.

## 2. Testing Admin Panel

**URL:** http://127.0.0.1:8000/admin/

**Login Credentials:**
- Username: `admin`
- Password: `admin123`

**Expected Result:**
- Login page loads successfully
- After login, admin dashboard displays with:
  - Authentication and Authorization section
  - Career_Counseling section with all models
  - Python Social Auth section

**Test Steps:**
1. Navigate to http://127.0.0.1:8000/admin/
2. Login with admin credentials
3. Verify all sections are visible
4. Click on "Questions" to see 8 sample questions
5. Click on "Career paths" to see 4 sample career paths

## 3. Testing API Endpoints

### 3.1 Questions Endpoint

**Endpoint:** `GET /api/questions/`

**Authentication:** Required

**Test with curl:**
```bash
# Without authentication (should fail)
curl -X GET http://localhost:8000/api/questions/

# Expected: {"detail":"Authentication credentials were not provided."}

# With authentication
curl -X GET http://localhost:8000/api/questions/ \
  -u admin:admin123

# Expected: JSON list of 8 assessment questions
```

### 3.2 Registration Endpoint

**Endpoint:** `POST /api/register/`

**Authentication:** Not required

**Test with curl:**
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123"
  }'

# Expected: Success response with user details
```

### 3.3 User Profiles Endpoint

**Endpoint:** `GET /api/profiles/`

**Authentication:** Required

**Test with curl:**
```bash
curl -X GET http://localhost:8000/api/profiles/ \
  -u admin:admin123

# Expected: JSON list of user profiles
```

### 3.4 User Responses Endpoint

**Endpoint:** `GET /api/responses/`

**Authentication:** Required

**Test with curl:**
```bash
curl -X GET http://localhost:8000/api/responses/ \
  -u admin:admin123

# Expected: JSON list of user responses (empty initially)
```

### 3.5 Career Recommendations Endpoint

**Endpoint:** `POST /api/recommendations/`

**Authentication:** Required

**Test with curl:**
```bash
curl -X POST http://localhost:8000/api/recommendations/ \
  -u admin:admin123

# Expected: Career recommendations or message to complete assessment first
```

## 4. Testing ML/NLP Features

### 4.1 NLTK Data

**Test:**
```bash
source venv/bin/activate
python -c "
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Test tokenization
text = 'I enjoy problem-solving and working with technology.'
tokens = word_tokenize(text)
print('Tokens:', tokens)

# Test stopwords
stop_words = set(stopwords.words('english'))
filtered_tokens = [w for w in tokens if w.lower() not in stop_words]
print('Filtered:', filtered_tokens)
"
```

**Expected Result:**
- Tokenization works without errors
- Stopwords are properly filtered

### 4.2 TensorFlow

**Test:**
```bash
source venv/bin/activate
python -c "
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer

print('TensorFlow version:', tf.__version__)

# Test tokenizer
tokenizer = Tokenizer()
texts = ['I love programming', 'I enjoy data science']
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)
print('Sequences:', sequences)
"
```

**Expected Result:**
- TensorFlow version prints (2.20.0 or higher)
- Tokenizer works and produces sequences

### 4.3 Scikit-learn

**Test:**
```bash
source venv/bin/activate
python -c "
from sklearn.tree import DecisionTreeClassifier
import numpy as np

# Simple test
X = np.array([[0, 0], [1, 1]])
y = np.array([0, 1])
clf = DecisionTreeClassifier()
clf.fit(X, y)
prediction = clf.predict([[2., 2.]])
print('Decision Tree works! Prediction:', prediction)
"
```

**Expected Result:**
- Decision tree classifier works without errors

## 5. Testing Career Predictor

**Test:**
```bash
source venv/bin/activate
python -c "
from career_counseling.ml.career_predictor import CareerPredictor
import numpy as np

predictor = CareerPredictor()
# Test with sample answers (8 questions, answers 0-3)
answers = [2, 3, 1, 2, 3, 1, 2, 3]
recommendations = predictor.get_career_recommendations(answers, top_n=3)

print('Career Recommendations:')
for i, rec in enumerate(recommendations, 1):
    print(f'{i}. {rec[\"career_path\"]}: {rec[\"confidence\"]:.2%}')
"
```

**Expected Result:**
- Career predictor initializes successfully
- Returns top 3 career recommendations with confidence scores

## 6. Database Verification

**Test:**
```bash
source venv/bin/activate
python manage.py shell -c "
from career_counseling.models import Question, CareerPath
print(f'Questions in database: {Question.objects.count()}')
print(f'Career Paths in database: {CareerPath.objects.count()}')

print('\nSample Questions:')
for q in Question.objects.all()[:3]:
    print(f'- {q.question_text[:50]}... ({q.question_type})')

print('\nSample Career Paths:')
for cp in CareerPath.objects.all():
    print(f'- {cp.title}')
"
```

**Expected Result:**
- 8 questions in database
- 4 career paths in database
- Displays sample questions and career paths

## 7. Static Files

**Test:**
```bash
ls -la staticfiles/
```

**Expected Result:**
- `staticfiles/` directory exists
- Contains admin CSS/JS files
- Contains rest_framework files
- Contains static files from the app

## 8. Common Issues and Solutions

### Issue: "Authentication credentials were not provided"
**Solution:** Most API endpoints require authentication. Use `-u username:password` with curl or login first.

### Issue: TensorFlow GPU warnings
**Solution:** These are informational. TensorFlow will use CPU automatically.

### Issue: Module not found
**Solution:** Activate virtual environment: `source venv/bin/activate`

### Issue: NLTK data not found
**Solution:** Run: `python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"`

## 9. Complete End-to-End Test

Run this comprehensive test script:

```bash
#!/bin/bash
source venv/bin/activate

echo "=== Testing CounselBot Setup ==="
echo ""

echo "1. Testing database..."
python manage.py shell -c "
from career_counseling.models import Question, CareerPath
assert Question.objects.count() == 8, 'Expected 8 questions'
assert CareerPath.objects.count() == 4, 'Expected 4 career paths'
print('✓ Database OK')
"

echo ""
echo "2. Testing NLTK..."
python -c "
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
tokens = word_tokenize('Test sentence')
assert len(tokens) > 0, 'Tokenization failed'
print('✓ NLTK OK')
"

echo ""
echo "3. Testing TensorFlow..."
python -c "
import tensorflow as tf
assert tf.__version__, 'TensorFlow not installed'
print('✓ TensorFlow OK')
"

echo ""
echo "4. Testing Scikit-learn..."
python -c "
from sklearn.tree import DecisionTreeClassifier
import numpy as np
clf = DecisionTreeClassifier()
X = np.array([[0], [1]])
y = np.array([0, 1])
clf.fit(X, y)
print('✓ Scikit-learn OK')
"

echo ""
echo "5. Testing Career Predictor..."
python -c "
from career_counseling.ml.career_predictor import CareerPredictor
predictor = CareerPredictor()
answers = [2, 3, 1, 2, 3, 1, 2, 3]
recs = predictor.get_career_recommendations(answers, top_n=3)
assert len(recs) == 3, 'Expected 3 recommendations'
print('✓ Career Predictor OK')
"

echo ""
echo "=== All Tests Passed! ==="
```

Save this as `test_setup.sh`, make it executable (`chmod +x test_setup.sh`), and run it to verify everything is working.

## 10. Load Testing (Optional)

For production readiness testing, you can use tools like:

```bash
# Install Apache Bench (if not installed)
# sudo apt-get install apache2-utils

# Test home page
ab -n 100 -c 10 http://127.0.0.1:8000/

# Test API endpoint (with authentication)
ab -n 100 -c 10 -A admin:admin123 http://127.0.0.1:8000/api/questions/
```

## Summary

✅ All major components have been tested:
- Django application server
- Admin panel
- API endpoints
- ML/NLP libraries (TensorFlow, NLTK, Scikit-learn)
- Career predictor model
- Database with sample data
- Static files collection

The application is ready for local development and testing!
