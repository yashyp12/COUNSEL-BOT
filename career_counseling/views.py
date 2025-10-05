from django.shortcuts import render, redirect
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import (
    UserProfile,
    Question,
    UserResponse,
    CareerPath,
    CareerRecommendation,
    AssessmentReport,
    AssessmentResult
)
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    QuestionSerializer,
    UserResponseSerializer,
    CareerPathSerializer,
    CareerRecommendationSerializer,
    AssessmentReportSerializer,
    UserRegistrationSerializer
)
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import json
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .ml.career_predictor import CareerPredictor

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

class UserRegistrationView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user': UserSerializer(user).data,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    @action(detail=False, methods=['get'])
    def get_assessment(self, request):
        questions = self.get_queryset().order_by('?')[:10]  # Random 10 questions
        return Response(QuestionSerializer(questions, many=True).data)

class UserResponseViewSet(viewsets.ModelViewSet):
    queryset = UserResponse.objects.all()
    serializer_class = UserResponseSerializer

    def get_queryset(self):
        return UserResponse.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        response = serializer.save(user=self.request.user)
        self._process_response(response)

    def _process_response(self, response):
        # Tokenize and process the response text
        tokens = word_tokenize(response.response_text.lower())
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words]
        
        # Create response vector using TF-IDF or word embeddings
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts([' '.join(tokens)])
        sequence = tokenizer.texts_to_sequences([' '.join(tokens)])
        vector = pad_sequences(sequence, maxlen=50)
        
        # Save the processed vector
        response.response_vector = vector.tolist()
        response.save()

class CareerRecommendationView(APIView):
    def post(self, request):
        user = request.user
        responses = UserResponse.objects.filter(user=user)
        
        if not responses.exists():
            return Response({
                'message': 'Please complete the assessment first'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Prepare data for the decision tree
        X = []
        for response in responses:
            if response.response_vector:
                X.extend(response.response_vector[0])
        
        # Get all career paths
        career_paths = CareerPath.objects.all()
        
        # Train decision tree (simplified for example)
        clf = DecisionTreeClassifier()
        # In real implementation, you would have proper training data
        y = np.random.randint(0, len(career_paths), size=len(X))
        X = np.array(X).reshape(-1, 1)
        clf.fit(X, y)
        
        # Make predictions
        predictions = clf.predict_proba(X)
        
        # Create recommendations
        recommendations = []
        for i, career_path in enumerate(career_paths):
            confidence = float(np.mean(predictions[:, i]) if i < predictions.shape[1] else 0)
            recommendation = CareerRecommendation.objects.create(
                user=user,
                career_path=career_path,
                confidence_score=confidence,
                reasoning="Based on your responses and our analysis"
            )
            recommendations.append(recommendation)
        
        # Create assessment report
        report = self._generate_report(user, recommendations)
        
        return Response({
            'recommendations': CareerRecommendationSerializer(recommendations, many=True).data,
            'report': AssessmentReportSerializer(report).data
        })

    def _generate_report(self, user, recommendations):
        # Analyze skills and interests
        responses = UserResponse.objects.filter(user=user)
        skill_analysis = self._analyze_responses(responses, 'SKILLS')
        interest_analysis = self._analyze_responses(responses, 'INTERESTS')
        personality_insights = self._analyze_responses(responses, 'PERSONALITY')
        
        # Create visualization
        plt.figure(figsize=(10, 6))
        careers = [r.career_path.title for r in recommendations[:5]]
        scores = [r.confidence_score for r in recommendations[:5]]
        sns.barplot(x=scores, y=careers)
        plt.title('Top Career Recommendations')
        
        # Save plot to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        graphic = base64.b64encode(image_png)
        
        # Create report
        report = AssessmentReport.objects.create(
            user=user,
            skill_analysis=skill_analysis,
            interest_analysis=interest_analysis,
            personality_insights=personality_insights
        )
        report.recommendations.set(recommendations)
        
        return report

    def _analyze_responses(self, responses, response_type):
        type_responses = responses.filter(question__question_type=response_type)
        analysis = {
            'scores': {},
            'summary': f"Analysis of {response_type.lower()} based on {len(type_responses)} responses"
        }
        
        for response in type_responses:
            # Implement more sophisticated analysis based on response vectors
            analysis['scores'][response.question.question_text] = {
                'response': response.response_text,
                'confidence': 0.8  # Placeholder for actual confidence calculation
            }
        
        return analysis

@login_required
def assessment(request):
    if request.method == 'POST':
        # Get all answers from the form
        answers = []
        for key in request.POST:
            if key.startswith('question_'):
                answer_index = int(request.POST[key])
                answers.append(answer_index)
        
        # Initialize the career predictor
        predictor = CareerPredictor()
        
        # Get career recommendations
        recommendations = predictor.get_career_recommendations(answers)
        primary_recommendation = recommendations[0]
        
        # Save the assessment result
        AssessmentResult.objects.create(
            user=request.user,
            answers=answers,
            recommended_career=primary_recommendation['career_path'],
            confidence_score=primary_recommendation['confidence']
        )
        
        messages.success(request, 'Assessment completed successfully!')
        return redirect('assessment_results')
    
    # Get all questions for the assessment
    questions = Question.objects.all()
    return render(request, 'career_counseling/assessment.html', {
        'questions': questions
    })

@login_required
def assessment_results(request):
    # Get the user's latest assessment result
    result = AssessmentResult.objects.filter(user=request.user).order_by('-created_at').first()
    
    if not result:
        messages.warning(request, 'Please complete the assessment first.')
        return redirect('assessment')
    
    # Initialize the career predictor to get all probabilities
    predictor = CareerPredictor()
    career_details = predictor.predict_career(result.answers)
    
    return render(request, 'career_counseling/assessment_results.html', {
        'result': result,
        'career_details': career_details
    }) 