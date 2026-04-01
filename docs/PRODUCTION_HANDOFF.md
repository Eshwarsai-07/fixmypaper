# 🚀 Production Handoff: FixMyPaper 2.0

This document summarizes the final state of the **FixMyPaper 2.0** ecosystem and provides the instructions required to activate the production environment.

## 🏛️ Architecture Snapshot
FixMyPaper 2.0 is an event-driven, serverless-first platform:
- **API**: FastAPI (EKS) handles uploads and job metadata.
- **Orchestration**: AWS Step Functions (Standard + Express) manages the PDF parsing lifecycle.
- **State**: DynamoDB (Global Table) stores job status and results.
- **Parsing**: Grobid (EKS) with Serverless Fallback (Lambda).
- **Messaging**: SQS with Visibility Heartbeats for reliable processing.

---

## 🔐 Action Required: GitHub Secrets
Before pushing to the repository, you **must** add the following secrets to your GitHub repository settings (`Settings -> Secrets and variables -> Actions`):

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `AWS_GITHUB_OIDC_ROLE_ARN` | IAM Role ARN for OIDC (Staging) | `arn:aws:iam::123456789012:role/GitHubOIDC` |
| `AWS_GITHUB_OIDC_ROLE_ARN_PROD` | IAM Role ARN for OIDC (Production) | `arn:aws:iam::123456789012:role/GitHubOIDCProd` |
| `AWS_REGION` | The region where infra is deployed | `us-east-1` |
| `ECR_REPOSITORY_API` | Name of the ECR repo for API | `fixmypaper-api` |
| `ECR_REPOSITORY_WORKER` | Name of the ECR repo for Worker | `fixmypaper-worker` |

---

## 🛠️ Step 1: Bootstrap Infrastructure
Run the following commands from your Mac terminal to provision the 2.0 stack:

```bash
chmod +x infra/terraform/scripts/bootstrap.sh
./infra/terraform/scripts/bootstrap.sh
```

> [!WARNING]
> This command will initiate a `terraform plan`. Review the output carefully before running `terraform apply`.

---

## 🌪️ Step 2: Code Deployment
Once the infrastructure is ready, push your code to the `main` branch. The **GitHub Actions OIDC Pipeline** will:
1. Validate code (Flake8 + Pytest).
2. Build and push Docker images to Amazon ECR.
3. Deploy to Amazon EKS using a rolling-update strategy.
4. Update the Fallback Lambda function.

---

## ✅ Step 3: Verification
1. **Health Check**: `curl https://<api-url>/api/health`
2. **Chaos Test**: Run `./scripts/chaos_suite.sh` to verify circuit breakers.
3. **Logs**: View real-time logs in CloudWatch under the `/aws/vendedlogs/states/` prefix.

---

## 📜 Maintenance
- **RDS**: Currently maintained for "Historical Analytics". All job state is in DynamoDB.
- **Scaling**: EKS HPA will automatically scale pods based on CPU/Memory pressure.
- **Cost**: Express Step Functions are used for high-frequency parsing to minimize state transition costs.

*FixMyPaper 2.0: Engineered for scale, built for resilience.*
