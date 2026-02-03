#!/bin/bash
set -e

echo "🚀 Deploying Frontend to K3s..."

# Set namespace
NAMESPACE="medical-frontend"

# Apply namespace
echo "📦 Creating namespace..."
kubectl apply -f ../namespaces/frontend-namespace.yaml

# Apply frontend resources
echo "⚙️  Applying ConfigMap..."
kubectl apply -f ../frontend/configmap.yaml

echo "🚢 Deploying frontend..."
kubectl apply -f ../frontend/deployment.yaml

echo "🌐 Creating service..."
kubectl apply -f ../frontend/service.yaml

echo "📈 Setting up HPA..."
kubectl apply -f ../frontend/hpa.yaml

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/frontend -n $NAMESPACE --timeout=300s

# Show status
echo "✅ Frontend deployment complete!"
echo ""
echo "📊 Deployment status:"
kubectl get pods -n $NAMESPACE
echo ""
kubectl get svc -n $NAMESPACE
echo ""
echo "🎉 Frontend is running!"
