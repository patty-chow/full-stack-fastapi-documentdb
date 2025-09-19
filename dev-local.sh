#!/bin/bash

# Local development script (without Docker)

echo "🚀 Starting FastAPI DocumentDB Local Development"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+"
    exit 1
fi

# Setup backend
echo "🔧 Setting up backend..."
cd backend
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file from example"
fi

if [ ! -d venv ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo "🚀 Starting FastAPI backend on port 8000..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Setup frontend
echo "🔧 Setting up frontend..."
cd ../frontend
if [ ! -d node_modules ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

echo "🚀 Starting React frontend on port 3000..."
npm start &
FRONTEND_PID=$!

echo "✅ Development environment is ready!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID" INT
wait