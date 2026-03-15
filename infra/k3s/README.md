# K3s Infrastructure Configuration

This directory contains Kubernetes manifests for deploying the medical chatbot application using k3s.

## Directory Structure

```
k3s/
├── local/          # Local development configurations
├── server/         # Production server configurations
├── scripts/        # Utility scripts
└── README.md       # This file
```

## Environments

### Local Development (`local/`)
- **Purpose**: Development and testing on local machine
- **Configuration**: 
  - Uses localhost for ingress
  - Single replica for backend
  - Debug logging enabled
  - Local service connections (MongoDB, ChromaDB)
  - No TLS/SSL
- **Deployment**: `cd local && ./deploy.sh`

### Production Server (`server/`)
- **Purpose**: Production deployment on server
- **Configuration**:
  - Uses custom domain for ingress
  - Multiple replicas for backend (3)
  - Production logging
  - External service connections
  - TLS/SSL with Let's Encrypt
- **Deployment**: `cd server && ./deploy.sh`

## Key Differences

| Component | Local | Server |
|-----------|-------|--------|
| **Backend Replicas** | 1 | 3 |
| **Image Pull Policy** | Never | Always |
| **Resources** | Lower limits | Higher limits |
| **Ingress Host** | localhost | your-domain.com |
| **TLS** | Disabled | Enabled |
| **Logging** | DEBUG | INFO |
| **Environment** | development | production |

## Usage

1. **Local Development**:
   ```bash
   cd local
   ./deploy.sh
   ```

2. **Production Deployment**:
   ```bash
   cd server
   # Update your-domain.com in ingress/traefik-ingress.yaml
   ./deploy.sh
   ```

## Configuration Requirements

### Before deploying to server:
1. Update `your-domain.com` in `server/ingress/traefik-ingress.yaml`
2. Update external service URLs in `server/backend/configmap.yaml`
3. Ensure secrets are properly configured

### For local development:
1. Ensure local MongoDB and ChromaDB services are running
2. Update service hostnames if needed in `local/backend/configmap.yaml`

## Services

- **Frontend**: React application served by Nginx
- **Backend**: FastAPI Python application
- **Database**: MongoDB (external/local)
- **Vector DB**: ChromaDB (external/local)
- **Ingress**: Traefik with SSL and middleware
