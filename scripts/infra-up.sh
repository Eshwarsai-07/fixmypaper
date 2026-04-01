#!/bin/bash
# fixmypaper - Infrastructure Provisioning Script (100% Serverless)
set -e

# Configuration
WORKSPACE="production"
TERRAFORM_DIR="infra/terraform"
K8S_DIR="infra/k8s"

echo "🚀 Spinning up FixMyPaper 2.0 Infrastructure..."

# 1. Terraform Apply
echo "📦 Running Terraform..."
cd $TERRAFORM_DIR
terraform init
terraform workspace select $WORKSPACE || terraform workspace new $WORKSPACE
terraform apply -auto-approve

# 2. Update Kubeconfig
echo "☸️ Updating Kubeconfig..."
CLUSTER_NAME=$(terraform output -raw eks_cluster_name)
aws eks update-kubeconfig --name $CLUSTER_NAME --region us-east-1

# 3. Deploy Grobid to EKS Fargate
echo "🧪 Deploying Grobid Parser..."
cd ../..
kubectl apply -f $K8S_DIR/grobid.yaml

echo "✅ Infrastructure is LIVE!"
echo "--------------------------------------------------"
cd $TERRAFORM_DIR
terraform output
