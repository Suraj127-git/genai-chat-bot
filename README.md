# Medical Chat Bot

> AI-Powered Clinical Decision Support System with Document Processing

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

A full-stack medical chatbot that helps healthcare professionals analyze patient cases, process medical documents (PDF/DOCX/TXT), and generate evidence-based clinical recommendations using AI.

### Key Features

- 🔐 **Secure Authentication** - JWT-based auth with refresh tokens
- 📄 **Document Processing** - Upload and analyze medical documents
- 🤖 **AI Clinical Analysis** - GroqAI-powered insights with RAG
- 💾 **Vector Search** - Semantic document search with ChromaDB
- 📊 **Decision History** - Track all clinical analyses
- ⚡ **Production Ready** - K3s deployment with auto-scaling

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB
- GroqAI API key

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
uvicorn app.main:app --reload
```

Backend: `http://localhost:8000`  
API Docs: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

### 3. MongoDB (Optional - Docker)

```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## 📚 Documentation

- **[📖 Project Guide](./docs/PROJECT_GUIDE.md)** - Complete project overview, architecture, and setup
- **[🚀 Deployment Guide](./docs/DEPLOYMENT_GUIDE.md)** - Deploy to VPS, AWS, Hostinger, or K3s

## 🏗️ Architecture

```
Frontend (React) ←→ Backend (FastAPI) ←→ MongoDB
                          ↓
                      ChromaDB + GroqAI
```

## 📂 Project Structure

```
├── backend/          # FastAPI Python backend
├── frontend/         # React TypeScript frontend
├── infra/            # K3s deployment configs
├── docs/             # Documentation
└── .github/          # CI/CD pipeline
```

## 🔧 Tech Stack

**Backend:** Python, FastAPI, MongoDB, ChromaDB, LangChain, GroqAI  
**Frontend:** React, TypeScript, Redux, Tailwind CSS  
**Infrastructure:** Docker, K3s, Traefik, GitHub Actions

## 📡 API Endpoints

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - Login with JWT
- `POST /api/v1/documents/upload` - Upload documents
- `POST /api/v1/clinical/analyze` - AI clinical analysis
- `GET /api/v1/clinical/history` - Decision history

Full API documentation: `http://localhost:8000/docs`

## 🐳 Docker Deployment

```bash
# Build images
docker build -t medical-backend -f infra/docker/backend.Dockerfile backend/
docker build -t medical-frontend -f infra/docker/frontend.Dockerfile frontend/

# Run
docker run -p 8000:8000 --env-file backend/.env medical-backend
docker run -p 80:80 medical-frontend
```

## ☸️ K3s Deployment

```bash
cd infra/k3s/scripts
./deploy-all.sh  # Linux/Mac
# or
.\deploy-all.ps1  # Windows
```

## 🧪 Testing

```bash
# Backend
cd backend
pytest tests/ -v --cov=app

# Frontend
cd frontend
npm test -- --coverage
```

## 🔒 Security

- JWT authentication with bcrypt
- HTTPS/TLS ready
- CORS configuration
- Rate limiting
- Security headers
- Input validation

## 📊 Performance

- API response: < 200ms
- AI analysis: 2-5 seconds
- Supports 100+ concurrent users
- Auto-scaling with K3s

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

- Check `/health` endpoint for status
- Review logs for errors
- See [Troubleshooting Guide](./docs/DEPLOYMENT_GUIDE.md#troubleshooting)

---

**Built with ❤️ for healthcare professionals**

For detailed setup and deployment instructions, see the [documentation](./docs/).
