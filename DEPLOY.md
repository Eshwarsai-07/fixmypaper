# 🚀 DEPLOY.md: FixMyPaper 2.0 Lifecycle Runbook

This guide covers the **End-to-End lifecycle** of the FixMyPaper 2.0 platform. Use this for a clean reinstall from scratch or for routine maintenance.

---

## 🔥 1. Infrastructure Termination (Tear Down)
To completely delete the entire AWS environment and **stop all billing**, run:

```bash
# Set execution permission if not already set
chmod +x scripts/infra-down.sh

# Run the decommissioning script
./scripts/infra-down.sh
```

### What this does:
1.  **K8s Cleanup**: Deletes the Grobid parser pods and services from EKS Fargate.
2.  **Terraform Destroy**: Securely removes the S3 bucket, DynamoDB tables, Step Functions, AppSync API, Cognito User Pool, and the Amplify Frontend.

---

## 🏗️ 2. Infrastructure Deployment (Bootstrap)
To provision a **fresh, 100% serverless** environment on AWS:

### Step A: Prerequisites
1.  **AWS CLI**: Configured with admin Access/Secret keys.
2.  **GitHub PAT**: Generate a Personal Access Token (Classic) with `repo` and `admin:repo_hook` scopes.

### Step B: Provision
```bash
# Set your GitHub Token (MANDATORY)
export TF_VAR_github_access_token="your_ghp_token_here"

# Set script permission
chmod +x scripts/infra-up.sh

# Run the bootstrap script
./scripts/infra-up.sh
```

### What this does:
1.  **Terraform Init & Apply**: Builds the entire 100% serverless AWS backend.
2.  **Amplify Activation**: Connects your GitHub repo to AWS Amplify for the Next.js frontend.
3.  **Variable Injection**: Securely maps all Backend ARNs and IAM keys into the Frontend environment.
4.  **K8s Deployment**: Re-provisions Grobid on EKS Fargate nodes.

---

## ⚡ 3. Automated Deployment (CI/CD)

After the initial **Infrastructure Bootstrap** is complete, you no longer need to run Terraform scripts for code changes.

### Frontend Updates (AWS Amplify)
- Each time you **`git push`** to the `main` branch, AWS Amplify will automatically:
    - Detect the change.
    - Provision a temporary build container.
    - Run `npm run build`.
    - Deploy the updated Next.js SSR app globally.
    - **No manual action required.**

### Backend Updates (GitHub Actions)
- The repository includes a `.github/workflows/deploy.yml` that monitors the `main` and `production` branches.
- Use this to automate updates to your **Grobid Parser** configuration or Lambda functions.

---

## 📝 4. Post-Deployment Verification
Once the `infra-up.sh` finishes, verify your deployment:

1.  **Frontend**: Open the `amplify_url` provided in the output.
2.  **Data**: Log into the AWS Console -> DynamoDB and ensure `fixmypaper-formats` has the IEEE/APA/CV records. (If empty, run the `aws dynamodb put-item` seeds again).
3.  **Parser**: Run `kubectl get pods` to see your Grobid engine running on Fargate.

---
**Maintained by**: FixMyPaper DevOps 
**Version**: 2.0 (100% Serverless & AWS-Native)
