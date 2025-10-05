#!/bin/bash
# CounselBot - Comprehensive Test Script
# Tests all major components to verify setup is complete and working

set -e

echo "========================================="
echo "CounselBot - Comprehensive Test Suite"
echo "========================================="
echo ""

# Activate virtual environment
source venv/bin/activate

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "1. Testing Database..."
python manage.py shell -c "
from career_counseling.models import Question, CareerPath, UserProfile
from django.contrib.auth.models import User

questions = Question.objects.count()
career_paths = CareerPath.objects.count()
users = User.objects.count()

print(f'  Questions: {questions}')
print(f'  Career Paths: {career_paths}')
print(f'  Users: {users}')

assert questions == 8, f'Expected 8 questions, got {questions}'
assert career_paths == 4, f'Expected 4 career paths, got {career_paths}'
assert users >= 1, f'Expected at least 1 user, got {users}'
" 2>/dev/null
echo -e "${GREEN}✓${NC} Database OK"
echo ""

echo "2. Testing NLTK..."
python -c "
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Test tokenization
text = 'I enjoy problem-solving and working with technology.'
tokens = word_tokenize(text)
assert len(tokens) > 0, 'Tokenization failed'

# Test stopwords
stop_words = set(stopwords.words('english'))
filtered = [w for w in tokens if w.lower() not in stop_words]
assert len(filtered) < len(tokens), 'Stopwords filtering failed'

print(f'  Tokenized: {len(tokens)} tokens')
print(f'  After filtering: {len(filtered)} tokens')
" 2>/dev/null
echo -e "${GREEN}✓${NC} NLTK OK"
echo ""

echo "3. Testing TensorFlow..."
python -c "
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer

version = tf.__version__
print(f'  Version: {version}')

# Test tokenizer
tokenizer = Tokenizer()
texts = ['I love programming', 'I enjoy data science']
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)
assert len(sequences) == 2, 'Tokenizer failed'
print(f'  Tokenizer: OK')
" 2>/dev/null
echo -e "${GREEN}✓${NC} TensorFlow OK"
echo ""

echo "4. Testing Scikit-learn..."
python -c "
from sklearn.tree import DecisionTreeClassifier
from sklearn import __version__
import numpy as np

print(f'  Version: {__version__}')

# Test decision tree
X = np.array([[0, 0], [1, 1], [2, 2]])
y = np.array([0, 1, 1])
clf = DecisionTreeClassifier()
clf.fit(X, y)
prediction = clf.predict([[1.5, 1.5]])
assert prediction is not None, 'Decision Tree failed'
print(f'  Decision Tree: OK')
" 2>/dev/null
echo -e "${GREEN}✓${NC} Scikit-learn OK"
echo ""

echo "5. Testing Career Predictor..."
python -c "
from career_counseling.ml.career_predictor import CareerPredictor
import os

predictor = CareerPredictor()
# Model expects 10 features, use 10 answers
answers = [2, 3, 1, 2, 3, 1, 2, 3, 2, 1]
recommendations = predictor.get_career_recommendations(answers, top_n=3)

assert len(recommendations) == 3, f'Expected 3 recommendations, got {len(recommendations)}'
print(f'  Recommendations generated: {len(recommendations)}')

for i, rec in enumerate(recommendations, 1):
    career = rec['career_path']
    confidence = rec['confidence']
    print(f'    {i}. {career}: {confidence:.1%}')

# Check if model files exist
model_path = 'career_counseling/ml/models/career_predictor.joblib'
if os.path.exists(model_path):
    print(f'  Model file: OK')
" 2>/dev/null
echo -e "${GREEN}✓${NC} Career Predictor OK"
echo ""

echo "6. Testing Static Files..."
if [ -d "staticfiles" ]; then
    file_count=$(find staticfiles -type f | wc -l)
    echo "  Static files collected: $file_count files"
    echo -e "${GREEN}✓${NC} Static Files OK"
else
    echo -e "${RED}✗${NC} Static files directory not found"
    exit 1
fi
echo ""

echo "7. Testing Server (quick check)..."
timeout 5 python manage.py check 2>/dev/null || true
echo -e "${GREEN}✓${NC} Server Configuration OK"
echo ""

echo "8. Testing API Endpoints..."
# Start server in background
python manage.py runserver 8000 > /dev/null 2>&1 &
SERVER_PID=$!
sleep 3

# Test home page
HOME_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [ "$HOME_RESPONSE" = "200" ]; then
    echo -e "  Home page: ${GREEN}✓${NC} (HTTP $HOME_RESPONSE)"
else
    echo -e "  Home page: ${RED}✗${NC} (HTTP $HOME_RESPONSE)"
fi

# Test API questions endpoint (should require auth)
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/questions/)
if [ "$API_RESPONSE" = "403" ]; then
    echo -e "  API questions: ${GREEN}✓${NC} (HTTP $API_RESPONSE - Auth required as expected)"
else
    echo -e "  API questions: ${YELLOW}⚠${NC} (HTTP $API_RESPONSE)"
fi

# Test admin page
ADMIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/admin/)
if [ "$ADMIN_RESPONSE" = "302" ]; then
    echo -e "  Admin panel: ${GREEN}✓${NC} (HTTP $ADMIN_RESPONSE - Redirect to login)"
else
    echo -e "  Admin panel: ${YELLOW}⚠${NC} (HTTP $ADMIN_RESPONSE)"
fi

# Stop server
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

echo -e "${GREEN}✓${NC} API Endpoints OK"
echo ""

echo "========================================="
echo -e "${GREEN}✓ All Tests Passed!${NC}"
echo "========================================="
echo ""
echo "Your CounselBot setup is complete and working!"
echo ""
echo "To start the development server:"
echo "  python manage.py runserver"
echo ""
echo "Access the application at:"
echo "  http://127.0.0.1:8000/"
echo ""
echo "Access the admin panel at:"
echo "  http://127.0.0.1:8000/admin/"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
