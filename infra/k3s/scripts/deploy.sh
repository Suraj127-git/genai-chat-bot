#!/bin/bash
set -e

# ============================================
# Medical Chat Bot - K3s Deployment Script
# ============================================
# This script deploys the complete Medical Chat Bot application
# to a K3s cluster.
#
# Usage: ./deploy.sh
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAMESPACES_DIR="$(dirname "$SCRIPT_DIR")/namespaces"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")/backend"
FRONTEND_DIR="$(dirname "$SCRIPT_DIR")/frontend"
INGRESS_DIR="$(dirname "$SCRIPT_DIR")/ingress"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Medical Chat Bot - K3s Deployment${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}Error: kubectl is not installed or not in PATH${NC}"
        exit 1
    fi
}

# Function to check cluster connectivity
check_cluster() {
    echo -e "${YELLOW}Checking cluster connectivity...${NC}"
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}Error: Cannot connect to K3s cluster${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Connected to K3s cluster${NC}"
}

# Check prerequisites
check_kubectl
check_cluster

echo ""
echo -e "${YELLOW}Starting deployment...${NC}"
echo ""

# Step 1: Deploy namespaces
echo -e "${BLUE}Step 1/5: Creating namespaces...${NC}"
kubectl apply -f "$NAMESPACES_DIR/"
echo -e "${GREEN}✓ Namespaces created${NC}"

# Step 2: Deploy backend
echo ""
echo -e "${BLUE}Step 2/5: Deploying Backend...${NC}"
echo "  - Applying ConfigMap..."
kubectl apply -f "$BACKEND_DIR/configmap.yaml"
echo "  - Applying Secrets..."
kubectl apply -f "$BACKEND_DIR/secret.yaml"
echo "  - Deploying backend pods..."
kubectl apply -f "$BACKEND_DIR/deployment.yaml"
echo "  - Creating backend service..."
kubectl apply -f "$BACKEND_DIR/service.yaml"
echo "  - Setting up HPA..."
kubectl apply -f "$BACKEND_DIR/hpa.yaml"
echo -e "${GREEN}✓ Backend deployed${NC}"

# Step 3: Deploy frontend
echo ""
echo -e "${BLUE}Step 3/5: Deploying Frontend...${NC}"
echo "  - Applying ConfigMap..."
kubectl apply -f "$FRONTEND_DIR/configmap.yaml"
echo "  - Deploying frontend pods..."
kubectl apply -f "$FRONTEND_DIR/deployment.yaml"
echo "  - Creating frontend service..."
kubectl apply -f "$FRONTEND_DIR/service.yaml"
echo "  - Setting up HPA..."
kubectl apply -f "$FRONTEND_DIR/hpa.yaml"
echo -e "${GREEN}✓ Frontend deployed${NC}"

# Step 4: Deploy ingress and middlewares
echo ""
echo -e "${BLUE}Step 4/5: Deploying Ingress and Middlewares...${NC}"
kubectl apply -f "$INGRESS_DIR/"
echo -e "${GREEN}✓ Ingress deployed${NC}"

# Step 5: Wait for deployments to be ready
echo ""
echo -e "${BLUE}Step 5/5: Waiting for deployments to be ready...${NC}"
echo "  - Waiting for backend..."
kubectl rollout status deployment/backend -n medical-backend --timeout=300s || echo -e "${YELLOW}  ! Backend rollout status check failed (may still be starting)${NC}"
echo "  - Waiting for frontend..."
kubectl rollout status deployment/frontend -n medical-frontend --timeout=300s || echo -e "${YELLOW}  ! Frontend rollout status check failed (may still be starting)${NC}"

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""

# Display deployment status
echo -e "${BLUE}Backend Status:${NC}"
kubectl get pods -n medical-backend
echo ""

echo -e "${BLUE}Frontend Status:${NC}"
kubectl get pods -n medical-frontend
echo ""

echo -e "${BLUE}Services:${NC}"
kubectl get svc -n medical-backend
kubectl get svc -n medical-frontend
echo ""

echo -e "${BLUE}Ingress:${NC}"
kubectl get ingressroute -n default 2>/dev/null || kubectl get ingress -n default 2>/dev/null || echo "No ingress found"
echo ""

echo -e "${GREEN}🎉 Medical Chat Bot is deployed to K3s!${NC}"
echo ""
echo -e "${YELLOW}To verify deployment, run:${NC}  ./verify.sh"
echo -e "${YELLOW}To teardown deployment, run:${NC}  ./teardown.sh"
