#!/bin/bash
set -e

echo "🚀 Deploying Backend to K3s..."

# Set namespace
NAMESPACE="medical-backend"

# Apply namespace
echo "📦 Creating namespace..."
kubectl apply -f ../namespaces/backend-namespace.yaml

# Apply backend resources
echo "⚙️  Applying ConfigMap..."
kubectl apply -f ../backend/configmap.yaml

echo "🔐 Applying Secrets..."
kubectl apply -f ../backend/secret.yaml

echo "🚢 Deploying backend..."
kubectl apply -f ../backend/deployment.yaml

echo "🌐 Creating service..."
kubectl apply -f ../backend/service.yaml

echo "📈 Setting up HPA..."
kubectl apply -f ../backend/hpa.yaml

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/backend -n $NAMESPACE --timeout=300s

# Show status
echo "✅ Backend deployment complete!"
echo ""
echo "📊 Deployment status:"
kubectl get pods -n $NAMESPACE
echo ""
kubectl get svc -n $NAMESPACE
echo ""
echo "🎉 Backend is running!"
