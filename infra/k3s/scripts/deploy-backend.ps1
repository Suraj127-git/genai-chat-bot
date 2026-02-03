# PowerShell deployment script for backend to K3s
Write-Host "🚀 Deploying Backend to K3s..." -ForegroundColor Green

$NAMESPACE = "medical-backend"

# Apply namespace
Write-Host "📦 Creating namespace..." -ForegroundColor Cyan
kubectl apply -f ..\namespaces\backend-namespace.yaml

# Apply backend resources
Write-Host "⚙️  Applying ConfigMap..." -ForegroundColor Cyan
kubectl apply -f ..\backend\configmap.yaml

Write-Host "🔐 Applying Secrets..." -ForegroundColor Cyan
kubectl apply -f ..\backend\secret.yaml

Write-Host "🚢 Deploying backend..." -ForegroundColor Cyan
kubectl apply -f ..\backend\deployment.yaml

Write-Host "🌐 Creating service..." -ForegroundColor Cyan
kubectl apply -f ..\backend\service.yaml

Write-Host "📈 Setting up HPA..." -ForegroundColor Cyan
kubectl apply -f ..\backend\hpa.yaml

# Wait for deployment
Write-Host "⏳ Waiting for deployment to be ready..." -ForegroundColor Yellow
kubectl rollout status deployment/backend -n $NAMESPACE --timeout=300s

# Show status
Write-Host ""
Write-Host "✅ Backend deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Deployment status:" -ForegroundColor Cyan
kubectl get pods -n $NAMESPACE
Write-Host ""
kubectl get svc -n $NAMESPACE
Write-Host ""
Write-Host "🎉 Backend is running!" -ForegroundColor Green
