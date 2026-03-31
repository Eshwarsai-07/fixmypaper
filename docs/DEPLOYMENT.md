# PRODUCTION DEPLOYMENT GUIDE (FixMyPaper)

This guide details the steps to deploy the refactored, production-grade **FixMyPaper** environment using Terraform and Kubernetes.

## 🚀 1. Infrastructure Provisioning (Terraform)

### Prerequisites
- AWS CLI configured with administrator access
- Terraform installed

### Deployment Steps
1. Navigate to the terraform directory:
   ```bash
   cd infra/terraform
   ```
2. Initialize Terraform:
   ```bash
   terraform init
   ```
3. Create a workspace for your environment:
   ```bash
   terraform workspace new prod
   ```
4. Preview the changes:
   ```bash
   terraform plan -var-file=environments/prod/terraform.tfvars
   ```
5. Apply the changes:
   ```bash
   terraform apply -var-file=environments/prod/terraform.tfvars
   ```

---

## 🏗️ 2. Application Deployment (Kubernetes)

### Prerequisites
- `kubectl` configured to your new EKS cluster
- AWS Load Balancer Controller installed in your cluster

### Deployment Steps
1. Create the fixed namespace and secrets:
   ```bash
   kubectl create namespace fixmypaper
   kubectl create secret generic fixmypaper-secrets \
     --from-literal=DATABASE_URL="postgresql://user:pass@host:5432/db" \
     --from-literal=SECRET_KEY="your-secret-key" \
     -n fixmypaper
   ```
2. Apply the base configurations:
   ```bash
   kubectl apply -f infra/k8s/base/
   ```
3. Monitor the deployment:
   ```bash
   kubectl get pods -n fixmypaper
   ```

---

## 🛠️ 3. Environment Variables

| Variable | Description | Source |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string | RDS Output |
| `REDIS_URL` | Redis connection for Celery | Redis Service IP |
| `S3_BUCKET_NAME` | AWS S3 Bucket for uploads | S3 Output |
| `GROBID_URL` | GROBID AI Service Endpoint | GROBID Service IP |
