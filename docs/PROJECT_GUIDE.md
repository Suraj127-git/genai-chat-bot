# Medical Chat Bot - Complete Project Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [Local Development Setup](#local-development-setup)
7. [Configuration](#configuration)
8. [API Documentation](#api-documentation)
9. [Security](#security)
10. [Testing](#testing)

---

## 🎯 Project Overview

The Medical Chat Bot is a full-stack AI-powered clinical decision support system that helps healthcare professionals analyze patient cases, process medical documents, and generate evidence-based recommendations.

### Key Capabilities
- **Document Processing**: Upload and analyze PDF, DOCX, and TXT medical documents
- **AI Clinical Analysis**: Generate clinical insights using GroqAI (Mixtral 8x7B) with RAG
- **Secure Authentication**: JWT-based user authentication with refresh tokens
- **Decision History**: Track and review all clinical decision analyses
- **Vector Search**: Semantic document search using ChromaDB embeddings
- **Production Ready**: Complete K3s deployment with auto-scaling

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Traefik Ingress                       │
│          (TLS, CORS, Headers, Rate Limiting)            │
└─────┬────────────────────────────────────────┬──────────┘
      │                                        │
┌──────▼──────┐                        ┌───────▼──────┐
│  Frontend   │                        │   Backend    │
│  (React)    │◄──────────────────────►│  (FastAPI)   │
│             │      REST API          │              │
│ • Redux     │                        │ • MongoDB    │
│ • Tailwind  │                        │ • ChromaDB   │
│ • TypeScript│                        │ • LangChain  │
└─────────────┘                        │ • GroqAI     │
                                       └──────┬───────┘
                                              │
                                 ┌────────────┴────────────┐
                                 │                         │
                          ┌──────▼──────┐          ┌──────▼──────┐
                          │   MongoDB   │          │  ChromaDB   │
                          │  (External) │          │  (External) │
                          └─────────────┘          └─────────────┘
```

### Component Breakdown

**Frontend (React + TypeScript)**
- User interface for authentication, document upload, and clinical queries
- Redux Toolkit for state management
- Tailwind CSS for responsive design
- Axios for API communication with auto token refresh

**Backend (FastAPI + Python)**
- RESTful API with 13 endpoints
- JWT authentication with bcrypt password hashing
- Document processing pipeline (PDF/DOCX → Text → Vectors)
- AI clinical decision generation with RAG
- MongoDB for data persistence
- ChromaDB for vector embeddings

**Infrastructure (K3s + Docker)**
- Separate namespaces for frontend and backend
- Auto-scaling with HPA (2-10 backend pods, 2-6 frontend pods)
- Traefik ingress with security middlewares
- Multi-stage Docker builds for optimized images

---

## ✨ Features

### 1. Authentication & User Management
- User registration with email validation
- Secure login with JWT tokens (access + refresh)
- Protected routes and API endpoints
- Session management with automatic token refresh

### 2. Document Processing
- **Upload**: Drag-and-drop interface for PDF, DOCX, TXT files
- **Extraction**: Automatic text extraction from documents
- **Vectorization**: Text chunking and embedding generation
- **Storage**: GridFS for files, ChromaDB for vectors
- **Management**: List, view, and delete documents

### 3. AI Clinical Decision Support
- **Query Interface**: Natural language medical questions
- **Document Selection**: Choose relevant documents for context
- **RAG Pipeline**: Semantic search + LLM generation
- **Analysis**: AI-generated clinical insights with confidence scores
- **Citations**: Source attribution with relevance scores
- **History**: Track all past clinical decisions

### 4. Production Features
- Health check endpoints
- Error handling and logging
- Rate limiting (100 req/min)
- CORS configuration
- Security headers (HSTS, CSP, X-Frame-Options)
- Auto-scaling based on CPU/memory

---

## 🔧 Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Programming language |
| FastAPI | 0.115+ | Web framework |
| MongoDB | Latest | Document database |
| ChromaDB | 0.5+ | Vector database |
| LangChain | 0.3+ | LLM framework |
| GroqAI | Latest | LLM inference (Mixtral 8x7B) |
| Motor | 3.6+ | Async MongoDB driver |
| Pydantic | 2.10+ | Data validation |
| PyJWT | Latest | JWT tokens |
| Passlib | Latest | Password hashing |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18+ | UI framework |
| TypeScript | 5.7+ | Type safety |
| Redux Toolkit | 2.2+ | State management |
| React Router | 6.26+ | Client-side routing |
| Tailwind CSS | 3.4+ | Styling |
| Axios | 1.7+ | HTTP client |
| Vite | 6.0+ | Build tool |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| K3s | Kubernetes distribution |
| Traefik | Ingress controller |
| GitHub Actions | CI/CD pipeline |

---

## 📂 Project Structure

```
genai-chat-bot/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/            # API endpoints
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── documents.py   # Document management
│   │   │   └── clinical.py    # Clinical AI
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py      # Settings
│   │   │   └── security.py    # JWT & auth
│   │   ├── db/                # Database connections
│   │   │   ├── mongodb.py     # MongoDB
│   │   │   └── chromadb.py    # ChromaDB
│   │   ├── models/            # Pydantic models
│   │   ├── services/          # Business logic
│   │   ├── chains/            # LangChain workflows
│   │   └── main.py            # FastAPI app
│   ├── tests/                 # Test suite
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment template
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── app/              # Redux store
│   │   ├── features/         # Feature modules
│   │   │   ├── auth/         # Login/Register
│   │   │   ├── documents/    # Document upload
│   │   │   ├── clinical/     # Clinical AI
│   │   │   └── history/      # Decision history
│   │   ├── components/       # Reusable components
│   │   ├── services/         # API client
│   │   └── types/            # TypeScript types
│   ├── package.json          # Node dependencies
│   └── vite.config.ts        # Vite configuration
│
├── infra/                    # Infrastructure
│   ├── docker/               # Dockerfiles
│   ├── k3s/                  # K3s manifests
│   │   ├── namespaces/       # Namespace configs
│   │   ├── backend/          # Backend resources
│   │   ├── frontend/         # Frontend resources
│   │   ├── ingress/          # Traefik ingress
│   │   └── scripts/          # Deployment scripts
│   └── README.md
│
├── docs/                     # Documentation
│   ├── PROJECT_GUIDE.md      # This file
│   └── DEPLOYMENT_GUIDE.md   # Deployment instructions
│
└── .github/workflows/        # CI/CD pipeline
```

---

## 💻 Local Development Setup

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- MongoDB (local or cloud)
- GroqAI API key

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd genai-chat-bot
```

### Step 2: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env and add your credentials:
# - GROQ_API_KEY (required)
# - SECRET_KEY (generate a secure random string)
# - MONGODB_URL (if using external MongoDB)
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend (in new terminal)
cd frontend

# Install dependencies
npm install
```

### Step 4: Start Services

**Terminal 1 - MongoDB (if using Docker):**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Terminal 2 - Backend:**
```bash
cd backend
venv\Scripts\activate  # or source venv/bin/activate
uvicorn app.main:app --reload
```
Backend runs at: `http://localhost:8000`  
API Docs: `http://localhost:8000/docs`

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs at: `http://localhost:5173`

---

## ⚙️ Configuration

### Backend Environment Variables

Create `backend/.env` file:

```env
# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=medical_chatbot

# ChromaDB (uses local persistence by default)
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_PERSIST_DIR=./chroma_data

# AI API (REQUIRED)
GROQ_API_KEY=your_groq_api_key_here

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-min-32-chars-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=True

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# File Upload
MAX_UPLOAD_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,txt,doc,docx
```

### Frontend Configuration

The frontend automatically proxies `/api` requests to `http://localhost:8000` during development (configured in `vite.config.ts`).

For production, update the API base URL in `frontend/src/services/api.ts`.

---

## 📡 API Documentation

### Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://your-domain.com/api/v1`

### Interactive Documentation
Visit `http://localhost:8000/docs` for Swagger UI with all endpoints.

### Authentication Flow

1. **Register**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "doctor@hospital.com",
  "password": "secure_password",
  "full_name": "Dr. John Doe"
}
```

2. **Login**
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=doctor@hospital.com&password=secure_password
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

3. **Use Token**
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### Document Upload

```http
POST /api/v1/documents/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <binary_file_data>
```

### Clinical Analysis

```http
POST /api/v1/clinical/analyze
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "query": "What is the diagnosis based on the lab results?",
  "document_ids": ["doc_id_1", "doc_id_2"],
  "include_history": true
}
```

---

## 🔒 Security

### Implemented Security Measures

1. **Authentication**
   - JWT tokens with expiration
   - Refresh token mechanism
   - Bcrypt password hashing (cost factor: 12)

2. **API Security**
   - CORS configuration
   - Rate limiting (100 req/min, 200 burst)
   - Input validation with Pydantic
   - SQL injection prevention (NoSQL)

3. **Headers**
   - HSTS (Strict-Transport-Security)
   - CSP (Content-Security-Policy)
   - X-Frame-Options: SAMEORIGIN
   - X-Content-Type-Options: nosniff

4. **File Upload**
   - Type validation (PDF, DOCX, TXT only)
   - Size limits (50MB max)
   - Virus scanning (recommended for production)

### Production Security Checklist

- [ ] Change SECRET_KEY to a strong random value
- [ ] Use HTTPS/TLS certificates
- [ ] Enable firewall rules
- [ ] Use environment-specific secrets
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Database access restrictions
- [ ] API rate limiting per user

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test -- --coverage
```

### Manual Testing

1. **Health Check**
```bash
curl http://localhost:8000/health
```

2. **Register User**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'
```

3. **Login**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"
```

---

## 📊 Performance

### Expected Performance
- API response time: < 200ms (without AI)
- AI analysis time: 2-5 seconds (depends on document size)
- Document upload: < 10 seconds for 50MB files
- Concurrent users: 100+ (with auto-scaling)

### Optimization Tips
- Use Redis for caching (future enhancement)
- Enable CDN for frontend assets
- Optimize database indexes
- Use connection pooling
- Enable gzip compression

---

## 🐛 Troubleshooting

### Common Issues

**Backend won't start**
- Check MongoDB is running
- Verify GROQ_API_KEY is set in .env
- Ensure all dependencies are installed

**Frontend can't connect to backend**
- Verify backend is running on port 8000
- Check CORS settings in backend/.env
- Clear browser cache

**Document upload fails**
- Check file size (max 50MB)
- Verify file type (PDF, DOCX, TXT only)
- Ensure MongoDB GridFS is working

**AI analysis fails**
- Verify GROQ_API_KEY is valid
- Check ChromaDB is accessible
- Ensure documents are processed

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [LangChain Documentation](https://python.langchain.com/)
- [GroqAI Documentation](https://console.groq.com/docs)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

---

**For deployment instructions, see [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)**
