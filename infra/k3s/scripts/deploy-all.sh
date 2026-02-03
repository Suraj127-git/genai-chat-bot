#!/bin/bash
set -e

echo "🚀 Deploying Medical Chat Bot to K3s..."

# Deploy namespaces
echo "📦 Creating namespaces..."
kubectl apply -f ../namespaces/

# Deploy backend
echo ""
echo "🔧 Deploying Backend..."
./deploy-backend.sh

# Deploy frontend
echo ""
echo "🎨 Deploying Frontend..."
./deploy-frontend.sh

# Deploy ingress
echo ""
echo "🌐 Deploying Ingress and Middlewares..."
kubectl apply -f ../ingress/

echo ""
echo "⏳ Waiting for ingress to be ready..."
sleep 5

# Show overall status
echo ""
echo "✅ Full deployment complete!"
echo ""
echo "📊 Overall Status:"
echo ""
echo "Backend Pods:"
kubectl get pods -n medical-backend
echo ""
echo "Frontend Pods:"
kubectl get pods -n medical-frontend
echo ""
echo "Services:"
kubectl get svc -n medical-backend
kubectl get svc -n medical-frontend
echo ""
echo "Ingress:"
kubectl get ingressroute -n default
echo ""
echo "🎉 Medical Chat Bot is fully deployed!"
