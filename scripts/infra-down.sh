#!/bin/bash
# fixmypaper - Infrastructure Termination Script (100% Serverless)
set -e

# Configuration
WORKSPACE="production"
TERRAFORM_DIR="infra/terraform"

echo "⚠️  Deleting FixMyPaper 2.0 Infrastructure..."

# 1. Cleanup Kubernetes first
echo "🗑️  Deleting Kubernetes Pods and Services..."
kubectl delete -f infra/k8s/grobid.yaml || true

# 2. Terraform Destroy
echo "🔥 Running Terraform Destroy..."
cd $TERRAFORM_DIR
terraform init
terraform workspace select $WORKSPACE || terraform workspace new $WORKSPACE
terraform destroy -auto-approve

echo "✅ Infrastructure Terminated!"
