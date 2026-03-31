# FixMyPaper: Production Deployment Guide

This document provides step-by-step instructions to deploy the **FixMyPaper** system to a production-grade AWS EKS environment.

---

## Prerequisites

1.  **AWS CLI**: Configured with appropriate permissions.
2.  **Terraform**: Installed (>= 1.5.0).
3.  **kubectl**: Installed and configured.
4.  **Docker**: Installed and running.
5.  **GitHub Secrets**: 
    - `AWS_ACCESS_KEY_ID`
    - `AWS_SECRET_ACCESS_KEY`

---

## 1. Infrastructure Deployment (Terraform)

Create the underlying AWS resources.

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

**What this creates**:
- VPC with Public/Private subnets.
- EKS Cluster with separate Node Groups (API and Workers).
- RDS PostgreSQL database.
- ElastiCache Redis replication group.
- S3 Buckets (Uploads and Results).
- IAM Roles for EKS Pods (IRSA).

---

## 2. Containerization (Docker)

Manually build and push images (or let GitHub Actions handle it).

### Backend (API & Worker)
```bash
docker build -t fixmypaper-backend:latest -f backend/Dockerfile .
# Authenticate ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
# Push
docker tag fixmypaper-backend:latest <YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fixmypaper-backend:latest
docker push <YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fixmypaper-backend:latest
```

### Frontend
```bash
docker build -t fixmypaper-frontend:latest -f frontend/Dockerfile .
docker tag fixmypaper-frontend:latest <YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fixmypaper-frontend:latest
docker push <YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fixmypaper-frontend:latest
```

---

## 3. Orchestration (Kubernetes)

Deploy the services to the EKS cluster.

```bash
# Update kubeconfig
aws eks update-kubeconfig --name fixmypaper-eks --region us-east-1

# Create namespace
kubectl create namespace fixmypaper

# Apply manifests
kubectl apply -f infra/k8s/
```

**Important Notes**:
- Update `infra/k8s/ingress.yaml` with your ACM Certificate ARN.
- Update `infra/k8s/ingress.yaml` with your domain names (e.g., `api.fixmypaper.com`).
- Ensure the ConfigMap and Secrets are populated with your RDS/Redis endpoints.

---

## 4. CI/CD Pipeline

The `.github/workflows/deploy.yml` will automatically:
1.  Build new images on every push to `main`.
2.  Push them to Amazon ECR.
3.  Update the EKS Deployments via `kubectl`.
4.  Run database migrations automatically.

---

## 5. Security & Scaling

- **S3**: Access is restricted to the EKS worker pods via IAM IRSA roles.
- **ALB**: Handles HTTPS termination via AWS Certificate Manager.
- **HPA**: Both API and Worker pods scale horizontally based on CPU usage. API pods scale up to 10, Workers up to 20.
- **Secrets**: Use AWS Secrets Manager or K8s Secrets (provided in the pipeline).
