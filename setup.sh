#!/bin/bash
# CounselBot - Automated Setup Script
# This script sets up the Django project for local development

set -e  # Exit on error

echo "========================================="
echo "CounselBot - Setup Script"
echo "========================================="
echo ""

# Check Python version
echo "1. Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "2. Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "3. Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "4. Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "5. Installing dependencies from requirements.txt..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Download NLTK data
echo ""
echo "6. Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('punkt_tab', quiet=True)"
echo "✓ NLTK data downloaded"

# Check if .env file exists
echo ""
echo "7. Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠ .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✓ .env file created. Please update it with your credentials."
else
    echo "✓ .env file exists"
fi

# Run migrations
echo ""
echo "8. Running database migrations..."
python manage.py migrate
echo "✓ Migrations completed"

# Collect static files
echo ""
echo "9. Collecting static files..."
python manage.py collectstatic --noinput
echo "✓ Static files collected"

# Summary
echo ""
echo "========================================="
echo "✓ Setup completed successfully!"
echo "========================================="
echo ""
echo "To start the development server, run:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "The application will be available at: http://127.0.0.1:8000/"
echo ""
echo "API Endpoints:"
echo "  - http://127.0.0.1:8000/api/questions/"
echo "  - http://127.0.0.1:8000/api/analyze/"
echo "  - http://127.0.0.1:8000/api/recommendations/"
echo "  - http://127.0.0.1:8000/api/report/"
echo ""
echo "Note: Update the .env file with your Google OAuth credentials if needed."
echo "========================================="
