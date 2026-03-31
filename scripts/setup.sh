#!/bin/bash
# Local environment setup for the refactored project structure

echo "🚀 Setting up FixMyPaper local development environment..."

# 1. Backend Setup
echo "🏗️  Setting up backend..."
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 2. Frontend Setup
echo "🏗️  Setting up frontend..."
cd frontend
npm install
cd ..

# 3. Environment Variables
if [ ! -f .env ]; then
  echo "📄 Creating .env template..."
  cp backend/.env.example .env
fi

echo "✅ Setup complete! Run 'source venv/bin/activate' to start developing."
