#!/bin/bash

# Development startup script for FastAPI DocumentDB application

echo "🚀 Starting FastAPI DocumentDB Development Environment"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend .env file from example..."
    cp backend/.env.example backend/.env
fi

# Start the services
echo "🐳 Starting services with Docker Compose..."
docker-compose up -d mongodb

echo "⏳ Waiting for MongoDB to be ready..."
sleep 10

echo "🔧 Starting backend and frontend..."
docker-compose up --build

echo "✅ Development environment is ready!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"