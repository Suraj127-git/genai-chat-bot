#!/bin/bash

# ============================================
# Medical Chat Bot - K3s Verification Script
# ============================================
# This script verifies the Medical Chat Bot deployment
# in a K3s cluster by checking all components.
#
# Usage: ./verify.sh
# ============================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Medical Chat Bot - Deployment Verification${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Function to check pod status
check_pods() {
    local namespace=$1
    local app=$2
    
    echo -e "${YELLOW}Checking $app pods in namespace '$namespace'...${NC}"
    
    # Get pods status
    pods=$(kubectl get pods -n "$namespace" -o json 2>/dev/null)
    if [ $? -ne 0 ]; then
        echo -e "  ${RED}✗ Cannot get pods from namespace '$namespace'${NC}"
        ((FAILED++))
        return 1
    fi
    
    # Check if there are any pods
    pod_count=$(echo "$pods" | jq -r '.items | length' 2>/dev/null || echo "0")
    if [ "$pod_count" -eq 0 ]; then
        echo -e "  ${RED}✗ No pods found in namespace '$namespace'${NC}"
        ((FAILED++))
        return 1
    fi
    
    # Check each pod status
    running=$(echo "$pods" | jq -r '.items[] | select(.status.phase=="Running") | .metadata.name' 2>/dev/null | wc -l)
    total=$(echo "$pods" | jq -r '.items[] | .metadata.name' 2>/dev/null | wc -l)
    
    if [ "$running" -eq "$total" ]; then
        echo -e "  ${GREEN}✓ All $total pods are running${NC}"
        ((PASSED++))
    else
        echo -e "  ${YELLOW}⚠ $running/$total pods running${NC}"
        echo "$pods" | jq -r '.items[] | "    - \(.metadata.name): \(.status.phase)"' 2>/dev/null
        ((FAILED++))
    fi
}

# Function to check service status
check_service() {
    local namespace=$1
    local service=$2
    
    echo -e "${YELLOW}Checking service '$service' in namespace '$namespace'...${NC}"
    
    if kubectl get svc "$service" -n "$namespace" &>/dev/null; then
        echo -e "  ${GREEN}✓ Service '$service' exists${NC}"
        ((PASSED++))
    else
        echo -e "  ${RED}✗ Service '$service' not found${NC}"
        ((FAILED++))
    fi
}

# Function to check deployment status
check_deployment() {
    local namespace=$1
    local deployment=$2
    
    echo -e "${YELLOW}Checking deployment '$deployment' in namespace '$namespace'...${NC}"
    
    if kubectl get deployment "$deployment" -n "$namespace" &>/dev/null; then
        ready=$(kubectl get deployment "$deployment" -n "$namespace" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        desired=$(kubectl get deployment "$deployment" -n "$namespace" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
        
        if [ "$ready" = "$desired" ] && [ "$ready" != "" ] && [ "$ready" != "0" ]; then
            echo -e "  ${GREEN}✓ Deployment '$deployment' is ready ($ready/$desired replicas)${NC}"
            ((PASSED++))
        else
            echo -e "  ${YELLOW}⚠ Deployment '$deployment' not ready (${ready:-0}/$desired replicas)${NC}"
            ((FAILED++))
        fi
    else
        echo -e "  ${RED}✗ Deployment '$deployment' not found${NC}"
        ((FAILED++))
    fi
}

# Function to check ingress status
check_ingress() {
    echo -e "${YELLOW}Checking ingress...${NC}"
    
    # Try IngressRoute (Traefik)
    if kubectl get ingressroute -n default &>/dev/null; then
        count=$(kubectl get ingressroute -n default -o json | jq -r '.items | length' 2>/dev/null || echo "0")
        if [ "$count" -gt 0 ]; then
            echo -e "  ${GREEN}✓ IngressRoute found ($count route(s))${NC}"
            ((PASSED++))
            return 0
        fi
    fi
    
    # Try standard Ingress
    if kubectl get ingress -n default &>/dev/null; then
        count=$(kubectl get ingress -n default -o json | jq -r '.items | length' 2>/dev/null || echo "0")
        if [ "$count" -gt 0 ]; then
            echo -e "  ${GREEN}✓ Ingress found ($count route(s))${NC}"
            ((PASSED++))
            return 0
        fi
    fi
    
    echo -e "  ${YELLOW}⚠ No ingress configured${NC}"
}

# Function to get endpoint information
show_endpoints() {
    echo ""
    echo -e "${BLUE}Endpoint Information:${NC}"
    echo ""
    
    # Backend service
    backend_svc=$(kubectl get svc backend-service -n medical-backend -o jsonpath='{.spec.ports[0].port}' 2>/dev/null)
    echo "  Backend: http://backend-service.medical-backend.svc.cluster.local:$backend_svc"
    
    # Frontend service
    frontend_svc=$(kubectl get svc frontend-service -n medical-frontend -o jsonpath='{.spec.ports[0].port}' 2>/dev/null)
    echo "  Frontend: http://frontend-service.medical-frontend.svc.cluster.local:$frontend_svc"
    
    echo ""
}

# ============================================
# Verification Steps
# ============================================

echo -e "${BLUE}=== Namespace Checks ===${NC}"
echo ""

# Check namespaces exist
echo -e "${YELLOW}Checking namespaces...${NC}"
for ns in medical-backend medical-frontend; do
    if kubectl get namespace "$ns" &>/dev/null; then
        echo -e "  ${GREEN}✓ Namespace '$ns' exists${NC}"
        ((PASSED++))
    else
        echo -e "  ${RED}✗ Namespace '$ns' not found${NC}"
        ((FAILED++))
    fi
done

echo ""
echo -e "${BLUE}=== Backend Checks ===${NC}"
echo ""

check_deployment "medical-backend" "backend"
check_pods "medical-backend" "backend"
check_service "medical-backend" "backend-service"

echo ""
echo -e "${BLUE}=== Frontend Checks ===${NC}"
echo ""

check_deployment "medical-frontend" "frontend"
check_pods "medical-frontend" "frontend"
check_service "medical-frontend" "frontend-service"

echo ""
echo -e "${BLUE}=== Ingress Checks ===${NC}"
echo ""

check_ingress

echo ""
echo -e "${BLUE}=== Resource Summary ===${NC}"
echo ""

echo -e "${BLUE}Backend Pods:${NC}"
kubectl get pods -n medical-backend 2>/dev/null || echo "  Cannot get pods"
echo ""

echo -e "${BLUE}Frontend Pods:${NC}"
kubectl get pods -n medical-frontend 2>/dev/null || echo "  Cannot get pods"
echo ""

echo -e "${BLUE}Services:${NC}"
kubectl get svc -n medical-backend 2>/dev/null || echo "  Cannot get services"
kubectl get svc -n medical-frontend 2>/dev/null || echo "  Cannot get services"
echo ""

show_endpoints

# ============================================
# Summary
# ============================================

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Verification Summary${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "  ${GREEN}Passed: $PASSED${NC}"
echo -e "  ${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All verification checks passed!${NC}"
    echo ""
    echo -e "The Medical Chat Bot is properly deployed in K3s."
    exit 0
else
    echo -e "${YELLOW}⚠ Some verification checks failed.${NC}"
    echo ""
    echo -e "Please review the output above for details."
    echo "You may need to wait a moment for pods to start or check the logs."
    exit 1
fi
