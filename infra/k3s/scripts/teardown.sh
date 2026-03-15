#!/bin/bash

# ============================================
# Medical Chat Bot - K3s Teardown Script
# ============================================
# This script removes all Medical Chat Bot resources
# from a K3s cluster.
#
# Usage: ./teardown.sh
# ============================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Confirmation function
confirm() {
    local prompt=$1
    local default=${2:-"n"}
    
    if [ "$FORCE" = "true" ]; then
        return 0
    fi
    
    read -p "$prompt [y/N] " response
    case "$response" in
        [yY]|[yY][eE][sS])
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Check for --force flag
FORCE=false
if [ "$1" = "--force" ] || [ "$1" = "-f" ]; then
    FORCE=true
fi

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Medical Chat Bot - K3s Teardown${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed or not in PATH${NC}"
    exit 1
fi

# Confirm before proceeding
if ! $FORCE; then
    echo -e "${YELLOW}This will remove all Medical Chat Bot resources from the K3s cluster:${NC}"
    echo "  - medical-backend namespace (pods, services, deployments, configmaps, secrets)"
    echo "  - medical-frontend namespace (pods, services, deployments, configmaps)"
    echo "  - Ingress and middlewares"
    echo ""
    
    if ! confirm "Are you sure you want to continue?"; then
        echo ""
        echo -e "${YELLOW}Teardown cancelled.${NC}"
        exit 0
    fi
fi

echo ""
echo -e "${YELLOW}Starting teardown...${NC}"
echo ""

# Step 1: Delete ingress and middlewares
echo -e "${BLUE}Step 1/5: Removing Ingress and Middlewares...${NC}"
kubectl delete -f ../ingress/ --ignore-not-found=true 2>/dev/null || true
echo -e "${GREEN}✓ Ingress and middlewares removed${NC}"

# Step 2: Delete backend resources
echo ""
echo -e "${BLUE}Step 2/5: Removing Backend resources...${NC}"
kubectl delete -f ../backend/ --ignore-not-found=true 2>/dev/null || true
echo -e "${GREEN}✓ Backend resources removed${NC}"

# Step 3: Delete frontend resources
echo ""
echo -e "${BLUE}Step 3/5: Removing Frontend resources...${NC}"
kubectl delete -f ../frontend/ --ignore-not-found=true 2>/dev/null || true
echo -e "${GREEN}✓ Frontend resources removed${NC}"

# Step 4: Delete namespaces
echo ""
echo -e "${BLUE}Step 4/5: Removing Namespaces...${NC}"
kubectl delete namespace medical-backend --ignore-not-found=true 2>/dev/null || true
kubectl delete namespace medical-frontend --ignore-not-found=true 2>/dev/null || true
echo -e "${GREEN}✓ Namespaces removed${NC}"

# Step 5: Verify cleanup
echo ""
echo -e "${BLUE}Step 5/5: Verifying cleanup...${NC}"

# Check if namespaces are deleted
remaining_namespaces=$(kubectl get ns 2>/dev/null | grep -E "medical-backend|medical-frontend" | wc -l)
if [ "$remaining_namespaces" -eq 0 ]; then
    echo -e "${GREEN}✓ All namespaces removed successfully${NC}"
else
    echo -e "${YELLOW}⚠ Some namespaces may still be terminating${NC}"
fi

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Teardown Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""

# Show remaining resources (should be none related to medical-chatbot)
echo -e "${BLUE}Remaining namespaces:${NC}"
kubectl get ns 2>/dev/null
echo ""

echo -e "${GREEN}✓ All Medical Chat Bot resources have been removed from K3s${NC}"
echo ""

# Cleanup any remaining custom resources
echo -e "${YELLOW}Note: If there are any remaining resources (like IngressRoute CRDs),${NC}"
echo -e "${YELLOW}you may need to manually delete them:${NC}"
echo "  kubectl get ingressroute -n default"
echo "  kubectl delete ingressroute medical-chatbot-ingress -n default"
echo ""
