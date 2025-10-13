# CounselBot - Complete Local Development Setup Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step-by-Step Installation](#step-by-step-installation)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)
7. [Common Issues & Solutions](#common-issues--solutions)

---

## Prerequisites

### System Requirements

#### Required Software
- **Python**: 3.11.9 (recommended) or Python 3.10+ (minimum)
- **pip**: Latest version (21.0+)
- **wkhtmltopdf**: 0.12.6 (system-level PDF generation tool)
- **Database**: SQLite (for development) or PostgreSQL/MySQL (for production)
- **Git**: For cloning the repository

#### Operating System Support
- ✅ Linux (Ubuntu 20.04+, Debian 10+)
- ✅ macOS (10.15+)
- ✅ Windows 10/11 (with WSL recommended)

### Hardware Requirements
- **RAM**: Minimum 4GB (8GB recommended for ML models)
- **Storage**: 2GB free space
- **CPU**: 2+ cores recommended

---

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yashyp12/COUNSEL-BOT.git
cd COUNSEL-BOT
```

### 2. Python Environment Setup

#### Option A: Using pyenv (Recommended)

```bash
# Install pyenv (if not already installed)
# On Linux/macOS:
curl https://pyenv.run | bash

# Install Python 3.11.9
pyenv install 3.11.9
pyenv local 3.11.9

# Verify Python version
python --version  # Should show Python 3.11.9
```

#### Option B: Using System Python

```bash
# Verify Python version
python3 --version  # Should be 3.10 or higher

# Use python3 explicitly if needed
alias python=python3
```

### 3. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate.bat

# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# Your prompt should now show (venv)
```

### 4. Install Python Dependencies

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# This will install:
# - Django 3.2+
# - Django REST Framework
# - TensorFlow (ML framework)
# - scikit-learn (ML library)
# - NLTK (Natural Language Processing)
# - pdfkit (PDF generation)
# - And many other dependencies...
```

**Note:** TensorFlow installation may take 5-10 minutes depending on your internet speed.

### 5. Install wkhtmltopdf (Critical for PDF Generation)

#### Ubuntu/Debian Linux

```bash
sudo apt-get update
sudo apt-get install -y wkhtmltopdf

# Verify installation
which wkhtmltopdf
wkhtmltopdf --version
```

#### macOS

```bash
# Using Homebrew
brew install wkhtmltopdf

# Verify installation
which wkhtmltopdf
wkhtmltopdf --version
```

#### Windows

1. Download installer from: https://wkhtmltopdf.org/downloads.html
2. Install the MSI package (select "Add to PATH" during installation)
3. Restart your terminal
4. Verify installation:
   ```cmd
   where wkhtmltopdf
   wkhtmltopdf --version
   ```

#### Troubleshooting wkhtmltopdf

If `wkhtmltopdf` command is not found after installation:

**Linux:**
```bash
# Find the binary location
sudo find / -name wkhtmltopdf 2>/dev/null

# Create symlink if needed
sudo ln -s /usr/local/bin/wkhtmltopdf /usr/bin/wkhtmltopdf
```

**macOS:**
```bash
# Check Homebrew installation
brew info wkhtmltopdf

# If not in PATH, add to your shell profile
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Windows:**
```cmd
# Add to PATH manually
# Go to: System Properties > Advanced > Environment Variables
# Add: C:\Program Files\wkhtmltopdf\bin
```

### 6. Download NLTK Data

NLTK requires downloading additional data files for natural language processing:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
```

Or use interactive download:
```bash
python
>>> import nltk
>>> nltk.download()  # Opens GUI to select packages
>>> exit()
```

---

## Configuration

### 1. Create Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

### 2. Edit .env File

Open `.env` in your text editor and configure the following:

```bash
# Django Configuration
SECRET_KEY=your_django_secret_key_here_change_this_in_production
DEBUG=True

# Database Configuration (SQLite is default for development)
DATABASE_URL=sqlite:///db.sqlite3

# Google OAuth (Optional - for social login)
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret_here

# Email Configuration (Optional - for password reset)
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_specific_password
```

#### Generate Django Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste it as your `SECRET_KEY` in `.env`.

#### Google OAuth Setup (Optional)

If you want to enable Google login:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Google+ API"
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:8000/auth/complete/google-oauth2/`
   - `http://127.0.0.1:8000/auth/complete/google-oauth2/`
6. Copy Client ID and Secret to `.env`

---

## Database Setup

### 1. Run Database Migrations

```bash
# Create database tables
python manage.py migrate

# You should see output like:
# Operations to perform:
#   Apply all migrations: admin, auth, career_counseling, contenttypes, sessions, social_django
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   ... (more migrations)
```

### 2. Create Superuser (Admin Account)

```bash
python manage.py createsuperuser

# Follow the prompts:
# Username: admin
# Email: admin@example.com
# Password: (choose a strong password)
# Password (again): (confirm password)
```

### 3. Load Sample Data (Optional)

If there are fixtures or sample data:

```bash
# Check for fixtures
ls career_counseling/fixtures/

# Load fixtures if available
python manage.py loaddata career_counseling/fixtures/sample_data.json
```

### 4. Verify Database

```bash
# Check database status
python manage.py dbshell

# For SQLite, this opens sqlite3 shell
# List tables:
.tables

# Exit:
.exit
```

---

## Running the Application

### 1. Collect Static Files

Django needs to collect all static files (CSS, JS, images) into one location:

```bash
python manage.py collectstatic --noinput

# You should see:
# X static files copied to '/path/to/COUNSEL-BOT/staticfiles'
```

### 2. Start Development Server

```bash
python manage.py runserver

# Server should start on: http://127.0.0.1:8000/
```

You should see output like:
```
System check identified no issues (0 silenced).
October 12, 2025 - 13:30:00
Django version 3.2.x, using settings 'counselbot.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### 3. Access the Application

Open your browser and navigate to:

- **Home Page**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Docs**: http://127.0.0.1:8000/api/

### 4. Test the Application

#### Quick Test Checklist
- [ ] Home page loads successfully
- [ ] Can navigate to registration page
- [ ] Can create a new account
- [ ] Can log in with created account
- [ ] Can access profile page
- [ ] Can start assessment
- [ ] Can view recommendations
- [ ] Can download PDF report

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'django'"

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: TensorFlow GPU warnings

**Example:**
```
Could not find cuda drivers on your machine, GPU will not be used.
```

**Solution:** These are informational messages, not errors. TensorFlow will use CPU instead of GPU. This is fine for development.

### Issue: "wkhtmltopdf is not installed or not accessible"

**Solution:**
```bash
# Verify installation
which wkhtmltopdf  # Linux/macOS
where wkhtmltopdf  # Windows

# If not found, reinstall (see Step 5 above)

# Check Django can find it
python manage.py shell
>>> import subprocess
>>> subprocess.run(['which', 'wkhtmltopdf'])
>>> exit()
```

### Issue: NLTK data not found

**Error:**
```
Resource punkt not found.
```

**Solution:**
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Issue: Database migration errors

**Solution:**
```bash
# Backup existing database
cp db.sqlite3 db.sqlite3.backup

# Delete database and migrations
rm db.sqlite3
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate migrations and database
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Issue: Static files not loading (CSS/JS missing)

**Solution:**
```bash
# Collect static files again
python manage.py collectstatic --clear --noinput

# Verify STATIC_ROOT in settings.py
python manage.py shell
>>> from django.conf import settings
>>> print(settings.STATIC_ROOT)
>>> exit()
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use a different port
python manage.py runserver 8080

# Or find and kill the process using port 8000
# Linux/macOS:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## Common Issues & Solutions

### PDF Generation Problems

#### Symptom: PDF downloads fail

**Check wkhtmltopdf:**
```bash
# Test wkhtmltopdf directly
echo '<h1>Test</h1>' | wkhtmltopdf - test.pdf
ls -lh test.pdf
```

**Check Python integration:**
```bash
python manage.py shell
>>> import pdfkit
>>> pdfkit.from_string('<h1>Test</h1>', 'test.pdf')
>>> exit()
```

**Check file permissions:**
```bash
# Ensure Django can write to temporary directories
ls -ld /tmp
chmod 1777 /tmp  # If needed
```

### Database Issues

#### Symptom: "database is locked" error

**Solution:**
```bash
# Close all connections to database
# Stop the development server (Ctrl+C)
# Restart server
python manage.py runserver
```

#### Symptom: Migration conflicts

**Solution:**
```bash
# Fake the conflicting migration
python manage.py migrate --fake app_name migration_name

# Or reset migrations (development only!)
python manage.py migrate --fake-initial
```

### Authentication Problems

#### Symptom: Can't log in after registration

**Solution:**
```bash
# Reset user password via Django shell
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='your_username')
>>> user.set_password('new_password')
>>> user.save()
>>> exit()
```

#### Symptom: Google OAuth not working

**Solution:**
1. Check `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` in `.env`
2. Verify redirect URIs in Google Cloud Console
3. Ensure `social_django` is in `INSTALLED_APPS`
4. Check browser console for CORS errors

### Performance Issues

#### Symptom: Slow page loads

**Solution:**
```bash
# Enable Django debug toolbar (development only)
pip install django-debug-toolbar

# Add to INSTALLED_APPS in settings.py
# Add to MIDDLEWARE in settings.py
# Configure in settings.py
```

#### Symptom: Assessment takes too long

**Solution:**
- Reduce number of career paths in database
- Optimize ML model calculations
- Add caching for recommendations

---

## Development Best Practices

### 1. Use Version Control

```bash
# Create a new branch for your work
git checkout -b feature/my-new-feature

# Commit regularly
git add .
git commit -m "Add new feature"

# Push to remote
git push origin feature/my-new-feature
```

### 2. Keep Dependencies Updated

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### 3. Test Before Committing

```bash
# Run Django checks
python manage.py check

# Run migrations check
python manage.py makemigrations --dry-run --check

# Test critical paths
python manage.py test  # If tests exist
```

### 4. Use Environment Variables

Never commit sensitive information to Git:
- Database credentials
- Secret keys
- API keys
- OAuth secrets

Always use `.env` file and keep it in `.gitignore`.

---

## Next Steps

After successful setup:

1. **Explore the Admin Panel**: http://127.0.0.1:8000/admin/
   - Add career paths
   - Add assessment questions
   - View user data

2. **Create Sample Data**:
   - Register a test user
   - Complete an assessment
   - View recommendations
   - Download PDF report

3. **Customize the Application**:
   - Edit templates in `templates/`
   - Modify styles in `static/css/`
   - Add new features in `career_counseling/`

4. **Read the Documentation**:
   - `README.md` - Project overview
   - `BUGFIX_SUMMARY.md` - Known issues and fixes
   - `WORKFLOW_FIXES_SUMMARY.md` - Recent improvements

---

## Getting Help

If you encounter issues not covered in this guide:

1. **Check Existing Documentation**:
   - README.md
   - TROUBLESHOOTING_GUIDE.md (if available)
   - GitHub Issues

2. **Check Logs**:
   ```bash
   # Django console output
   # Browser console (F12)
   # Server logs
   ```

3. **Enable Debug Mode**:
   ```bash
   # In .env file
   DEBUG=True
   ```

4. **Ask for Help**:
   - Create a GitHub issue
   - Include error messages
   - Include steps to reproduce
   - Include your environment details

---

## System Requirements Summary

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.10 | 3.11.9 |
| RAM | 4GB | 8GB |
| Storage | 2GB | 5GB |
| CPU | 2 cores | 4 cores |
| OS | Ubuntu 20.04 | Ubuntu 22.04 |

---

## Checklist for Successful Setup

- [ ] Python 3.11.9 installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] wkhtmltopdf installed and accessible
- [ ] NLTK data downloaded
- [ ] `.env` file configured
- [ ] Database migrations completed
- [ ] Superuser created
- [ ] Static files collected
- [ ] Development server running
- [ ] Home page accessible
- [ ] Admin panel accessible
- [ ] PDF generation tested

---

**Setup Complete!** 🎉

You're now ready to start developing with CounselBot!
