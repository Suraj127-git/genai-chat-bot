# Medical Chat Bot - Deployment Guide

## 📋 Table of Contents
1. [Deployment Options](#deployment-options)
2. [Prerequisites](#prerequisites)
3. [VPS Deployment (AWS, Hostinger, DigitalOcean)](#vps-deployment)
4. [Docker Deployment](#docker-deployment)
5. [K3s/Kubernetes Deployment](#k3s-deployment)
6. [Environment Configuration](#environment-configuration)
7. [SSL/TLS Setup](#ssltls-setup)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

---

## 🚀 Deployment Options

This guide covers three deployment methods:

1. **VPS Deployment** - Deploy to any VPS (AWS EC2, Hostinger VPS, DigitalOcean, etc.)
2. **Docker Deployment** - Containerized deployment with Docker Compose
3. **K3s Deployment** - Production Kubernetes deployment with auto-scaling

Choose based on your needs:
- **Small scale (< 100 users)**: VPS or Docker
- **Medium scale (100-1000 users)**: Docker with load balancer
- **Large scale (1000+ users)**: K3s with auto-scaling

---

## 📋 Prerequisites

### For All Deployments
- Domain name (e.g., `medical-chatbot.com`)
- GroqAI API key ([Get it here](https://console.groq.com/))
- MongoDB instance (Atlas free tier or self-hosted)
- SSL certificate (Let's Encrypt recommended)

### For VPS Deployment
- Ubuntu 22.04 LTS server (2GB RAM minimum, 4GB recommended)
- Root or sudo access
- Public IP address

### For Docker Deployment
- Docker 24+ and Docker Compose 2+
- 4GB RAM minimum

### For K3s Deployment
- K3s cluster or managed Kubernetes
- kubectl configured
- 8GB RAM minimum

---

## 🖥️ VPS Deployment

This method works for **AWS EC2, Hostinger VPS, DigitalOcean, Linode, Vultr**, or any Ubuntu VPS.

### Step 1: Server Setup

```bash
# SSH into your server
ssh root@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm nginx certbot python3-certbot-nginx git mongodb

# Install PM2 for process management
sudo npm install -g pm2
```

### Step 2: Clone and Setup Application

```bash
# Create application directory
sudo mkdir -p /var/www/medical-chatbot
cd /var/www/medical-chatbot

# Clone repository
git clone <your-repo-url> .

# Set permissions
sudo chown -R $USER:$USER /var/www/medical-chatbot
```

### Step 3: Backend Setup

```bash
# Navigate to backend
cd /var/www/medical-chatbot/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
nano .env
```

**Edit `.env` file:**
```env
# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=medical_chatbot

# ChromaDB
CHROMA_PERSIST_DIR=/var/www/medical-chatbot/chroma_data

# AI API
GROQ_API_KEY=your_groq_api_key_here

# Security - CHANGE THESE!
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=False

# CORS - Update with your domain
ALLOWED_ORIGINS=https://your-domain.com

# File Upload
MAX_UPLOAD_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,txt,doc,docx
```

**Start backend with PM2:**
```bash
# Create PM2 ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'medical-backend',
    script: 'venv/bin/uvicorn',
    args: 'app.main:app --host 0.0.0.0 --port 8000',
    cwd: '/var/www/medical-chatbot/backend',
    instances: 2,
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production'
    }
  }]
}
EOF

# Start application
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### Step 4: Frontend Setup

```bash
# Navigate to frontend
cd /var/www/medical-chatbot/frontend

# Install dependencies
npm install

# Update API URL in src/services/api.ts
# Change baseURL to your domain

# Build for production
npm run build

# Copy build to nginx directory
sudo cp -r dist/* /var/www/html/
```

### Step 5: Nginx Configuration

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/medical-chatbot
```

**Add this configuration:**
```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration (will be added by certbot)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts for AI processing
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # File upload size
    client_max_body_size 50M;
}
```

**Enable site and restart Nginx:**
```bash
sudo ln -s /etc/nginx/sites-available/medical-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: SSL Certificate (Let's Encrypt)

```bash
# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### Step 7: Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Step 8: MongoDB Security

```bash
# Secure MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Create admin user
mongosh
```

In MongoDB shell:
```javascript
use admin
db.createUser({
  user: "admin",
  pwd: "your_secure_password",
  roles: ["userAdminAnyDatabase", "dbAdminAnyDatabase", "readWriteAnyDatabase"]
})

use medical_chatbot
db.createUser({
  user: "medical_app",
  pwd: "your_app_password",
  roles: ["readWrite"]
})
exit
```

**Update backend .env:**
```env
MONGODB_URL=mongodb://medical_app:your_app_password@localhost:27017/medical_chatbot
```

**Restart backend:**
```bash
pm2 restart medical-backend
```

---

## 🐳 Docker Deployment

### Step 1: Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Step 2: Create Docker Compose File

```bash
cd /var/www/medical-chatbot
nano docker-compose.yml
```

**Add this configuration:**
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    container_name: medical-mongodb
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    volumes:
      - mongodb_data:/data/db
    networks:
      - medical-network

  backend:
    build:
      context: ./backend
      dockerfile: ../infra/docker/backend.Dockerfile
    container_name: medical-backend
    restart: always
    ports:
      - "8000:8000"
    environment:
      MONGODB_URL: mongodb://admin:${MONGO_PASSWORD}@mongodb:27017
      GROQ_API_KEY: ${GROQ_API_KEY}
      SECRET_KEY: ${SECRET_KEY}
      ALLOWED_ORIGINS: https://your-domain.com
    volumes:
      - chroma_data:/app/chroma_data
    depends_on:
      - mongodb
    networks:
      - medical-network

  frontend:
    build:
      context: ./frontend
      dockerfile: ../infra/docker/frontend.Dockerfile
    container_name: medical-frontend
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    networks:
      - medical-network

volumes:
  mongodb_data:
  chroma_data:

networks:
  medical-network:
    driver: bridge
```

### Step 3: Create Environment File

```bash
nano .env
```

```env
MONGO_PASSWORD=your_secure_mongo_password
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=$(openssl rand -hex 32)
```

### Step 4: Deploy

```bash
# Build and start services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

---

## ☸️ K3s Deployment

### Step 1: Install K3s

```bash
# Install K3s
curl -sfL https://get.k3s.io | sh -

# Check status
sudo systemctl status k3s

# Get kubeconfig
sudo cat /etc/rancher/k3s/k3s.yaml > ~/.kube/config
chmod 600 ~/.kube/config
```

### Step 2: Configure External Databases

**Option A: MongoDB Atlas (Recommended)**
1. Create free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Get connection string
3. Update `infra/k3s/backend/configmap.yaml`

**Option B: Self-hosted MongoDB**
```bash
# Deploy MongoDB outside K3s
docker run -d \
  --name mongodb \
  --restart always \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=your_password \
  -v /data/mongodb:/data/db \
  mongo:latest
```

### Step 3: Update K3s Configurations

**Edit backend ConfigMap:**
```bash
nano infra/k3s/backend/configmap.yaml
```

Update MongoDB URL and other settings.

**Edit backend Secret:**
```bash
nano infra/k3s/backend/secret.yaml
```

Add your GROQ_API_KEY and SECRET_KEY (base64 encoded):
```bash
echo -n "your_groq_api_key" | base64
echo -n "your_secret_key" | base64
```

**Edit Ingress:**
```bash
nano infra/k3s/ingress/traefik-ingress.yaml
```

Update domain name.

### Step 4: Deploy to K3s

**Linux/Mac:**
```bash
cd infra/k3s/scripts
chmod +x deploy-all.sh
./deploy-all.sh
```

**Windows:**
```powershell
cd infra\k3s\scripts
.\deploy-all.ps1
```

### Step 5: Verify Deployment

```bash
# Check pods
kubectl get pods -n medical-backend
kubectl get pods -n medical-frontend

# Check services
kubectl get svc -n medical-backend
kubectl get svc -n medical-frontend

# Check ingress
kubectl get ingressroute -n default

# View logs
kubectl logs -f deployment/backend -n medical-backend
```

---

## ⚙️ Environment Configuration

### Production Environment Variables

**Backend (.env):**
```env
# Database
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/medical_chatbot
MONGODB_DB_NAME=medical_chatbot

# ChromaDB
CHROMA_HOST=chromadb.example.com
CHROMA_PORT=8000

# AI API
GROQ_API_KEY=gsk_xxxxxxxxxxxxx

# Security
SECRET_KEY=<64-char-random-hex>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
ENVIRONMENT=production
LOG_LEVEL=WARNING
DEBUG=False

# CORS
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# File Upload
MAX_UPLOAD_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,txt,doc,docx
```

### Generate Secure Keys

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate MongoDB password
openssl rand -base64 32
```

---

## 🔒 SSL/TLS Setup

### Let's Encrypt (Free)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal (already configured)
sudo certbot renew --dry-run
```

### Custom SSL Certificate

If you have a custom certificate:

```bash
# Copy certificates
sudo cp your-cert.crt /etc/ssl/certs/
sudo cp your-key.key /etc/ssl/private/

# Update Nginx configuration
sudo nano /etc/nginx/sites-available/medical-chatbot
```

Update SSL paths in Nginx config.

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl https://your-domain.com/api/v1/health

# Check logs
pm2 logs medical-backend

# Or for Docker
docker-compose logs -f backend

# Or for K3s
kubectl logs -f deployment/backend -n medical-backend
```

### Backup Strategy

**MongoDB Backup:**
```bash
# Create backup script
cat > /usr/local/bin/backup-mongodb.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mongodb"
mkdir -p $BACKUP_DIR

mongodump --uri="mongodb://user:pass@localhost:27017/medical_chatbot" \
  --out="$BACKUP_DIR/backup_$DATE"

# Keep only last 7 days
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;
EOF

chmod +x /usr/local/bin/backup-mongodb.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-mongodb.sh") | crontab -
```

**Application Backup:**
```bash
# Backup application files
tar -czf /backups/app_$(date +%Y%m%d).tar.gz /var/www/medical-chatbot
```

### Updates

```bash
# Update application
cd /var/www/medical-chatbot
git pull

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
pm2 restart medical-backend

# Update frontend
cd ../frontend
npm install
npm run build
sudo cp -r dist/* /var/www/html/
```

---

## 🐛 Troubleshooting

### Backend Issues

**Backend won't start:**
```bash
# Check logs
pm2 logs medical-backend

# Check MongoDB connection
mongosh --eval "db.adminCommand('ping')"

# Verify environment variables
cat backend/.env
```

**High memory usage:**
```bash
# Restart backend
pm2 restart medical-backend

# Check memory
free -h
pm2 monit
```

### Frontend Issues

**404 errors:**
```bash
# Check Nginx configuration
sudo nginx -t

# Verify files exist
ls -la /var/www/html/

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Database Issues

**MongoDB connection failed:**
```bash
# Check MongoDB status
sudo systemctl status mongod

# Restart MongoDB
sudo systemctl restart mongod

# Check MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log
```

### SSL Issues

**Certificate expired:**
```bash
# Renew certificate
sudo certbot renew

# Restart Nginx
sudo systemctl restart nginx
```

---

## 📈 Performance Optimization

### Nginx Caching

Add to Nginx config:
```nginx
# Cache static files
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Database Indexing

```javascript
// In MongoDB shell
use medical_chatbot

// Create indexes
db.users.createIndex({ "email": 1 }, { unique: true })
db.documents.createIndex({ "user_id": 1 })
db.clinical_decisions.createIndex({ "user_id": 1, "created_at": -1 })
```

### PM2 Cluster Mode

Already configured in ecosystem.config.js with 2 instances.

---

## 🔐 Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable firewall (UFW)
- [ ] Configure SSL/TLS
- [ ] Secure MongoDB with authentication
- [ ] Regular backups configured
- [ ] Update system packages regularly
- [ ] Monitor logs for suspicious activity
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Configure CORS properly

---

## 📞 Support

For issues:
1. Check logs first
2. Verify all services are running
3. Check environment variables
4. Review this guide
5. Check GitHub issues

---

**Deployment complete! Your Medical Chat Bot is now live! 🎉**
