#!/bin/bash
# Manual deployment script for EKS

if [ "$1" == "--help" ]; then
  echo "🚀 Usage: ./scripts/deploy.sh [environment]"
  echo "Example: ./scripts/deploy.sh prod"
  exit 0
fi

ENV=${1:-dev}

echo "🚀 Deploying FixMyPaper to $ENV environment..."

# 1. Update EKS
aws eks update-kubeconfig --name fixmypaper-$ENV

# 2. Apply Configs
kubectl apply -f infra/k8s/base/

# 3. Rollout
kubectl rollout restart deployment/fixmypaper-api -n fixmypaper
kubectl rollout restart deployment/fixmypaper-worker -n fixmypaper

echo "✅ Deployment complete!"
