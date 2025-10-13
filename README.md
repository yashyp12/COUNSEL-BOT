# CounselBot - AI-Powered Career Counseling System

CounselBot is an intelligent career counseling web application that leverages machine learning and natural language processing to provide personalized career recommendations to students.

## 🎉 Recent Updates (October 2025)

**All critical system issues have been resolved!** Version 2.0 is now production-ready with:

- ✅ **PDF Generation Fixed** - wkhtmltopdf properly installed and configured
- ✅ **User Registration Working** - Enhanced validation, no more false errors
- ✅ **Profile Updates Functional** - Users can update their information successfully
- ✅ **Assessment Submission Clean** - No more false error messages
- ✅ **Comprehensive Documentation** - Complete setup and troubleshooting guides

**Test Results:** 52/52 tests passed (100% success rate)

See [FIXES_SUMMARY.md](FIXES_SUMMARY.md) for complete details on all improvements.

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

## 📚 Documentation

**NEW:** Comprehensive documentation now available!

- **[COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)** - Detailed step-by-step installation guide for all platforms
- **[TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)** - Solutions for common issues and problems
- **[TESTING_REPORT.md](TESTING_REPORT.md)** - Comprehensive testing results (52 tests, 100% pass rate)
- **[FIXES_SUMMARY.md](FIXES_SUMMARY.md)** - Summary of all bug fixes and improvements

## Setup Instructions

### ⚡ Quick Start

For the most comprehensive and up-to-date setup instructions, see **[COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)**.

### Quick Setup (Automated)

Run the automated setup script:
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies including TensorFlow, scikit-learn, and NLTK
- Download required NLTK data (punkt, stopwords, punkt_tab)
- Set up environment variables (from .env.example)
- Run database migrations
- Collect static files

### Manual Setup

**Recommended Python Version:** 3.11.9 (or Python 3.10+)

1. Clone the repository:
```bash
git clone https://github.com/yashyp12/COUNSEL-BOT.git
cd COUNSEL-BOT
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Install wkhtmltopdf (CRITICAL for PDF generation):**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y wkhtmltopdf

# macOS
brew install wkhtmltopdf

# Windows - Download from: https://wkhtmltopdf.org/downloads.html
```

5. Download NLTK data:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
```

5. Set up environment variables:
Create a `.env` file in the root directory by copying `.env.example`:
```bash
cp .env.example .env
```

Then update the `.env` file with your credentials:
```
SECRET_KEY=your_django_secret_key_here
DEBUG=True
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret_here
DATABASE_URL=sqlite:///db.sqlite3
```

6. Run migrations:
```bash
python manage.py migrate
```

7. Collect static files:
```bash
python manage.py collectstatic --noinput
```

8. Create a superuser (optional, for admin access):
```bash
python manage.py createsuperuser
```

9. Start the development server:
```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

### Docker Setup (Alternative)

For a containerized setup with Docker:

1. Make sure Docker and Docker Compose are installed

2. Build and run:
```bash
docker-compose up --build
```

3. Access the application at: **http://localhost:8000/**

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

All API endpoints require authentication (except registration).

- **GET** `/api/questions/` - Get list of assessment questions
- **POST** `/api/responses/` - Submit user responses to questions
- **GET** `/api/responses/` - Get user's submitted responses
- **POST** `/api/recommendations/` - Get career recommendations based on responses
- **GET** `/api/profiles/` - Get user profiles
- **POST** `/api/register/` - Register a new user (no authentication required)

### Example API Usage

```bash
# Register a new user
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'

# Get questions (requires authentication)
curl -X GET http://localhost:8000/api/questions/ \
  -H "Authorization: Basic <base64_encoded_credentials>"

# Get career recommendations (requires authentication)
curl -X POST http://localhost:8000/api/recommendations/ \
  -H "Authorization: Basic <base64_encoded_credentials>"
```

## Troubleshooting

For comprehensive troubleshooting guidance, see **[TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)**.

### Common Issues (Quick Reference)

1. **PDF generation fails: "wkhtmltopdf is not installed"**
   - **Solution:** Install wkhtmltopdf system package
   - Ubuntu/Debian: `sudo apt-get install wkhtmltopdf`
   - macOS: `brew install wkhtmltopdf`
   - Windows: Download from https://wkhtmltopdf.org/downloads.html
   - See [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md#pdf-generation-issues) for detailed help

2. **User registration fails: "A user with that username already exists"**
   - Check if username truly exists in database
   - See [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md#user-registration-problems) for solutions

3. **Profile updates not saving**
   - Already fixed in latest version
   - Verify you're using the updated serializers
   - See [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md#profile-management-issues) for details

4. **TensorFlow warnings about GPU**
   - These are informational messages and can be ignored if you don't have a GPU
   - TensorFlow will automatically use CPU for computations

5. **NLTK data not found errors**
   - Run: `python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"`
   - Or use the setup script which handles this automatically

6. **Database migration errors**
   - If you have an old database with conflicts, backup and recreate:
     ```bash
     mv db.sqlite3 db.sqlite3.backup
     python manage.py migrate
     ```

7. **Module not found errors**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

### Testing the Setup

After setup, verify everything works:

```bash
# Check if server starts without errors
python manage.py runserver

# Access the home page
curl http://localhost:8000/

# Check admin panel
# Visit: http://localhost:8000/admin/

# Test API endpoints (create a user first)
curl http://localhost:8000/api/questions/
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 