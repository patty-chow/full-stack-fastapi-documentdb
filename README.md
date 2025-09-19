# Full Stack FastAPI with DocumentDB

A modern full-stack web application template built with FastAPI, React, and DocumentDB (MongoDB). This template provides a solid foundation for building scalable web applications with a Python backend and React frontend.

## 🚀 Quick Start

To get started with this template, simply clone the repository:

```bash
git clone git@github.com:fastapi/full-stack-fastapi-template.git my-full-stack
cd my-full-stack
```

> **Note**: This is a DocumentDB variant of the FastAPI full-stack template. If you want the original PostgreSQL version, use the command above. For this DocumentDB version, clone:
> ```bash
> git clone git@github.com:patty-chow/full-stack-fastapi-documentdb.git my-full-stack
> ```

## 🏗️ Features

- **FastAPI** backend with automatic API documentation
- **React** frontend with modern JavaScript
- **DocumentDB/MongoDB** for data persistence
- **Docker** support for easy deployment
- **CORS** enabled for frontend-backend communication
- **Async/await** support throughout the application
- **Type hints** with Pydantic models
- **Hot reload** for development

## 📋 Prerequisites

- Docker and Docker Compose (for containerized development)
- Python 3.8+ (for local development)
- Node.js 16+ (for local development)
- MongoDB or AWS DocumentDB (for database)

## 🛠️ Development Setup

### Option 1: Docker Development (Recommended)

1. **Start the development environment:**
   ```bash
   ./dev-start.sh
   ```

   This will:
   - Start MongoDB in a Docker container
   - Build and start the FastAPI backend
   - Build and start the React frontend
   - Set up all necessary networks and volumes

2. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development

1. **Start local development:**
   ```bash
   ./dev-local.sh
   ```

   This requires MongoDB to be running locally or accessible via connection string.

2. **Manual setup** (if you prefer step-by-step):

   **Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your settings
   uvicorn app.main:app --reload
   ```

   **Frontend:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 📁 Project Structure

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── crud/           # Database operations
│   │   ├── db/             # Database connection
│   │   ├── schemas/        # Pydantic models
│   │   └── main.py         # FastAPI application
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/               # React frontend
│   ├── public/
│   ├── src/
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── dev-start.sh           # Docker development script
├── dev-local.sh           # Local development script
└── README.md
```

## 🔧 Configuration

### Backend Configuration

The backend can be configured using environment variables. Copy `.env.example` to `.env` and adjust the values:

```env
# API Settings
API_V1_STR="/api/v1"
PROJECT_NAME="Full Stack FastAPI DocumentDB"

# CORS
BACKEND_CORS_ORIGINS="http://localhost:3000"

# DocumentDB/MongoDB
DOCUMENTDB_CONNECTION_STRING="mongodb://localhost:27017"
DOCUMENTDB_DATABASE_NAME="fastapi_db"

# For AWS DocumentDB:
# DOCUMENTDB_CONNECTION_STRING="mongodb://username:password@cluster-endpoint:27017/?ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
```

### DocumentDB vs MongoDB

This template works with both:

- **MongoDB** (for local development and MongoDB Atlas)
- **AWS DocumentDB** (for production AWS deployments)

Simply update the `DOCUMENTDB_CONNECTION_STRING` in your `.env` file to switch between them.

## 🚀 Deployment

### Docker Deployment

1. **Production build:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

2. **Individual service builds:**
   ```bash
   # Backend only
   docker build -t fastapi-backend ./backend
   
   # Frontend only
   docker build -t react-frontend ./frontend
   ```

### Cloud Deployment

This template is ready for deployment on:

- **AWS** (with DocumentDB)
- **Google Cloud** (with MongoDB Atlas)
- **Azure** (with CosmosDB MongoDB API)
- **Heroku** (with MongoDB Atlas)

## 📚 API Documentation

Once the backend is running, visit:

- **Interactive API docs (Swagger UI):** http://localhost:8000/docs
- **Alternative API docs (ReDoc):** http://localhost:8000/redoc

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of the excellent [FastAPI](https://fastapi.tiangolo.com/) framework
- Inspired by the [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)
- Uses [React](https://reactjs.org/) for the frontend
- Database integration with [Motor](https://motor.readthedocs.io/) (async MongoDB driver)