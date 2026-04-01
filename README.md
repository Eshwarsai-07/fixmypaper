# FixMyPaper 2.0: 100% AWS-Native Operations Guide 📄🚀

Welcome to the **FixMyPaper 2.0** production repository. This system is a staff-level, 100% serverless, and event-driven research paper analysis platform. It is engineered for zero-maintenance, high-availability, and global scale.

---

## 🏗️ 1. Architecture Overview (100% Serverless)

The platform is split into two primary layers, both managed by **Terraform**.

-   **Frontend**: Next.js 14 (App Router) hosted on **AWS Amplify Hosting**.
-   **Backend**: 
    -   **Storage**: Amazon S3 (PDF Uploads)
    -   **State**: Amazon DynamoDB (Job Metadata & Formats)
    -   **Orchestration**: AWS Step Functions (Standard & Express Hybrid)
    -   **Compute**: Grobid Parser on **Amazon EKS Fargate** (Zero-EC2)
    -   **Real-time**: AWS AppSync (WebSockets for progress updates)

---

## 🛠️ 2. Prerequisites for New Developers

Before you begin, ensure you have the following installed and configured:

1.  **AWS CLI**: Configured with an Administrator-level IAM user.
    ```bash
    aws configure
    ```
2.  **Terraform**: Version 1.5.0 or higher.
3.  **GitHub Personal Access Token (PAT)**:
    -   Required for AWS Amplify to pull the code.
    -   Create a "Classic Token" with `repo` and `admin:repo_hook` scopes at [GitHub Settings](https://github.com/settings/tokens).

---

## 🚀 3. End-to-End Deployment (One-Click)

To deploy the entire stack from scratch:

### Step A: Prepare the Environment
Ensure your GitHub PAT is available in your shell session:
```bash
export TF_VAR_github_access_token="your_ghp_token_here"
```

### Step B: Run the Infrastructure Script
We provide a unified script that handles `terraform init`, `workspace select`, and `apply`.
```bash
chmod +x scripts/infra-up.sh
./scripts/infra-up.sh
```

### Step C: What the Script Does
1.  **Provisions Storage**: Creates the unique S3 bucket for PDFs.
2.  **Sets up State**: Initializes DynamoDB tables (`fixmypaper-jobs`).
3.  **Deploys Compute**: Sets up the EKS Cluster and the Fargate Profile for the Grobid parser.
4.  **Bridges Frontend**: Connects your GitHub repo to **AWS Amplify** and injects all backend ARNs as environment variables.

---

## 🔑 4. Environment Variables & Secrets

The system is designed to be **Zero-Configuration** for the frontend. Terraform automatically injects these into AWS Amplify:

| Variable Name | Source/Location | Purpose |
| :--- | :--- | :--- |
| `APP_AWS_REGION` | Terraform `var.aws_region` | Deployment region (us-east-1) |
| `APP_AWS_ACCESS_KEY_ID` | IAM User `frontend` | Secure bridge to backend |
| `APP_AWS_SECRET_ACCESS_KEY` | IAM User `frontend` | Secure bridge to backend |
| `S3_BUCKET_NAME` | S3 Module Output | Where PDFs are stored |
| `DYNAMODB_TABLE_JOBS` | DynamoDB Module Output | Where analysis results live |
| `STEP_FUNCTION_ARN` | Step Function Output | The "Brain" of the analysis |

> [!WARNING]
> **Reserved Prefixes**: AWS Amplify restricts variables starting with `AWS_`. We use the **`APP_AWS_`** prefix to bypass this and ensure the Next.js SDK can still authenticate.

---

## 📡 5. Verification & Monitoring

Once deployment is complete (`infra-up.sh` finishes):

1.  **Amplify URL**: The script will output a URL like `https://main.d123z.amplifyapp.com`.
2.  **Dashboard**: Visit the **AWS Console > Amplify > fixmypaper-gui** to watch the build logs.
3.  **Grobid Status**: Run `kubectl get pods` to ensure the Grobid parser is running on Fargate.
4.  **Logs**: All logs are centralized in **AWS CloudWatch** under the `/aws/vendedlogs/states/` and `/aws/lambda/` namespaces.

---

## 🧹 6. Decommissioning (Tear Down)
To completely delete all AWS resources and stop billing:
```bash
./scripts/infra-down.sh
```

---
**Maintained by**: FixMyPaper DevOps Team
**Stack Version**: 2.0 (Amplify + Serverless EKS)
