import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

class CareerPredictor:
    def __init__(self):
        self.model = DecisionTreeClassifier(
            max_depth=5,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        self.label_encoder = LabelEncoder()
        self.career_paths = [
            'Software Development',
            'Data Science',
            'UI/UX Design',
            'Project Management',
            'Business Analysis',
            'DevOps Engineering',
            'Quality Assurance',
            'Product Management'
        ]
        self.model_path = 'career_counseling/ml/models/career_predictor.joblib'
        self.encoder_path = 'career_counseling/ml/models/label_encoder.joblib'
        
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # Initialize or load the model
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            self.label_encoder = joblib.load(self.encoder_path)
        else:
            self._initialize_model()

    def _initialize_model(self):
        # Initialize the label encoder with career paths
        self.label_encoder.fit(self.career_paths)
        
        # Generate synthetic training data based on question categories
        # This is a simplified example - in production, you'd use real data
        n_samples = 1000
        n_features = 10  # Number of questions
        
        X = np.random.randint(0, 4, (n_samples, n_features))  # 4 options per question
        
        # Define rules for career paths based on answer patterns
        y = np.zeros(n_samples, dtype=int)
        for i in range(n_samples):
            # Example rules (simplified)
            if X[i, 0] == 0 and X[i, 1] == 0:  # Strong problem-solving and leadership
                y[i] = 0  # Software Development
            elif X[i, 2] == 1 and X[i, 3] == 0:  # Data-oriented and technical
                y[i] = 1  # Data Science
            elif X[i, 4] == 1 and X[i, 5] == 1:  # Creative and visual
                y[i] = 2  # UI/UX Design
            elif X[i, 6] == 3 and X[i, 7] == 3:  # Communication and management
                y[i] = 3  # Project Management
            else:
                y[i] = np.random.randint(0, len(self.career_paths))
        
        # Train the model
        self.model.fit(X, y)
        
        # Save the model and encoder
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.label_encoder, self.encoder_path)

    def predict_career(self, answers):
        """
        Predict career path based on assessment answers
        
        Args:
            answers (list): List of answer indices (0-3) for each question
            
        Returns:
            dict: Predicted career path and confidence score
        """
        # Convert answers to numpy array and reshape for prediction
        X = np.array(answers).reshape(1, -1)
        
        # Get prediction and probability
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        # Get confidence score
        confidence = probabilities[prediction]
        
        # Get career path name
        career_path = self.label_encoder.inverse_transform([prediction])[0]
        
        return {
            'career_path': career_path,
            'confidence': float(confidence),
            'all_probabilities': {
                path: float(prob) 
                for path, prob in zip(self.career_paths, probabilities)
            }
        }

    def get_career_recommendations(self, answers, top_n=3):
        """
        Get top N career recommendations based on assessment answers
        
        Args:
            answers (list): List of answer indices (0-3) for each question
            top_n (int): Number of top recommendations to return
            
        Returns:
            list: List of dictionaries containing career paths and confidence scores
        """
        X = np.array(answers).reshape(1, -1)
        probabilities = self.model.predict_proba(X)[0]
        
        # Get indices of top N careers
        top_indices = np.argsort(probabilities)[-top_n:][::-1]
        
        recommendations = []
        for idx in top_indices:
            career_path = self.label_encoder.inverse_transform([idx])[0]
            confidence = float(probabilities[idx])
            recommendations.append({
                'career_path': career_path,
                'confidence': confidence
            })
        
        return recommendations 