#!/bin/bash

# Local deployment script for k3s
echo "Deploying to local k3s environment..."

# Apply namespaces
kubectl apply -f namespaces/

# Apply backend configurations
kubectl apply -f backend/

# Apply frontend configurations
kubectl apply -f frontend/

# Apply ingress configurations
kubectl apply -f ingress/

echo "Local deployment completed!"
echo "Access the application at: http://localhost"
