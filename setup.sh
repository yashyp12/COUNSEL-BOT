#!/bin/bash
echo "========================================="
echo "CounselBot - Setup Script (Git Bash)"
echo "========================================="

# 1. Check Python version
echo
echo "1. Checking Python version..."
python --version

# 2. Remove old virtual environment (optional)
if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
fi

# 3. Create virtual environment
echo
echo "2. Creating virtual environment..."
python -m venv venv
echo "✓ Virtual environment created"

# 4. Activate virtual environment
echo
echo "3. Activating virtual environment..."
source venv/Scripts/activate
echo "✓ Virtual environment activated"

# 5. Upgrade pip and install dependencies
echo
echo "4. Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# 6. Download NLTK data
echo
echo "5. Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
echo "✓ NLTK data downloaded"

# 7. Check/create .env file
echo
echo "6. Checking environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env file created. Please update it with your credentials."
else
    echo "✓ .env file exists"
fi

# 8. Run migrations
echo
echo "7. Running database migrations..."
python manage.py makemigrations
python manage.py migrate
echo "✓ Migrations completed"

# 9. Collect static files
echo
echo "8. Collecting static files..."
python manage.py collectstatic --noinput
echo "✓ Static files collected"

# 10. Setup complete
echo
echo "========================================="
echo "✅ Setup completed successfully!"
echo "Run: source venv/Scripts/activate"
echo "Then: python manage.py runserver"
echo "========================================="
