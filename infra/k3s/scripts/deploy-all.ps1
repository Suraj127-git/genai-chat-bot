# PowerShell deployment script for all components to K3s
Write-Host "🚀 Deploying Medical Chat Bot to K3s..." -ForegroundColor Green

# Deploy namespaces
Write-Host "📦 Creating namespaces..." -ForegroundColor Cyan
kubectl apply -f ..\namespaces\

# Deploy backend
Write-Host ""
Write-Host "🔧 Deploying Backend..." -ForegroundColor Magenta
.\deploy-backend.ps1

# Deploy frontend
Write-Host ""
Write-Host "🎨 Deploying Frontend..." -ForegroundColor Magenta
.\deploy-frontend.ps1

# Deploy ingress
Write-Host ""
Write-Host "🌐 Deploying Ingress and Middlewares..." -ForegroundColor Cyan
kubectl apply -f ..\ingress\

Write-Host ""
Write-Host "⏳ Waiting for ingress to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Show overall status
Write-Host ""
Write-Host "✅ Full deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Overall Status:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend Pods:" -ForegroundColor Yellow
kubectl get pods -n medical-backend
Write-Host ""
Write-Host "Frontend Pods:" -ForegroundColor Yellow
kubectl get pods -n medical-frontend
Write-Host ""
Write-Host "Services:" -ForegroundColor Yellow
kubectl get svc -n medical-backend
kubectl get svc -n medical-frontend
Write-Host ""
Write-Host "Ingress:" -ForegroundColor Yellow
kubectl get ingressroute -n default
Write-Host ""
Write-Host "🎉 Medical Chat Bot is fully deployed!" -ForegroundColor Green
