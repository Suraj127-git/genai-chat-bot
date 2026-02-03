# PowerShell deployment script for frontend to K3s
Write-Host "🚀 Deploying Frontend to K3s..." -ForegroundColor Green

$NAMESPACE = "medical-frontend"

# Apply namespace
Write-Host "📦 Creating namespace..." -ForegroundColor Cyan
kubectl apply -f ..\namespaces\frontend-namespace.yaml

# Apply frontend resources
Write-Host "⚙️  Applying ConfigMap..." -ForegroundColor Cyan
kubectl apply -f ..\frontend\configmap.yaml

Write-Host "🚢 Deploying frontend..." -ForegroundColor Cyan
kubectl apply -f ..\frontend\deployment.yaml

Write-Host "🌐 Creating service..." -ForegroundColor Cyan
kubectl apply -f ..\frontend\service.yaml

Write-Host "📈 Setting up HPA..." -ForegroundColor Cyan
kubectl apply -f ..\frontend\hpa.yaml

# Wait for deployment
Write-Host "⏳ Waiting for deployment to be ready..." -ForegroundColor Yellow
kubectl rollout status deployment/frontend -n $NAMESPACE --timeout=300s

# Show status
Write-Host ""
Write-Host "✅ Frontend deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Deployment status:" -ForegroundColor Cyan
kubectl get pods -n $NAMESPACE
Write-Host ""
kubectl get svc -n $NAMESPACE
Write-Host ""
Write-Host "🎉 Frontend is running!" -ForegroundColor Green
