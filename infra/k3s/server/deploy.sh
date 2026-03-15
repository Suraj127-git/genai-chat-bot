#!/bin/bash

# Server deployment script for k3s
echo "Deploying to server k3s environment..."

# Apply namespaces
kubectl apply -f namespaces/

# Apply backend configurations
kubectl apply -f backend/

# Apply frontend configurations
kubectl apply -f frontend/

# Apply ingress configurations
kubectl apply -f ingress/

echo "Server deployment completed!"
echo "Access the application at: https://your-domain.com"
echo "Remember to update your-domain.com in the ingress configuration!"
