# CounselBot - AI-Powered Career Counseling System

CounselBot is an intelligent career counseling web application that leverages machine learning and natural language processing to provide personalized career recommendations to students.

## Features

- User authentication with username/password and Google OAuth
- Interactive questionnaire with situation-based questions
- ML-powered career path analysis using Decision Trees
- NLP-based response processing
- Personalized career reports with graphical insights
- Downloadable recommendation reports
- RESTful API architecture

## Tech Stack

- **Backend**: Django, Django REST Framework
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **ML/AI**: TensorFlow, Scikit-learn, NLTK
- **Data Visualization**: Matplotlib, Seaborn
- **Authentication**: Django Auth, Google OAuth
- **Database**: SQLite (development) / PostgreSQL (production)

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/counsel-bot.git
cd counsel-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory and add:
```
SECRET_KEY=your_django_secret_key
DEBUG=True
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

## Project Structure

```
counsel-bot/
├── counselbot/              # Django project directory
├── career_counseling/       # Main Django app
├── ml_models/              # Machine learning models
├── static/                 # Static files (CSS, JS, images)
├── templates/              # HTML templates
├── manage.py              
├── requirements.txt       
└── README.md             
```

## API Endpoints

- `/api/auth/` - Authentication endpoints
- `/api/questions/` - Get questionnaire
- `/api/analyze/` - Submit responses for analysis
- `/api/recommendations/` - Get career recommendations
- `/api/report/` - Generate and download report

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 