# FixMyPaper: Local Development & Verification Guide

This guide explains how to run the entire **FixMyPaper** stack locally using Docker Compose. This is the fastest way to verify that the API, Worker, Database, Redis, and AI services are communicating correctly.

## 📋 Prerequisites

1.  **Docker & Docker Compose**: Installed and running.
2.  **AWS Account**: An S3 bucket and an IAM user with `AmazonS3FullAccess`.

---

## 🚀 Step 1: Environment Setup

1.  Copy the environment template:
    ```bash
    cp .env.local.example .env
    ```
2.  Open the `.env` file and fill in your **AWS Credentials** and **Bucket Name**. These are required because the system currently processes files directly through S3.

    ```bash
    AWS_ACCESS_KEY_ID=AKIA...
    AWS_SECRET_ACCESS_KEY=...
    S3_BUCKET_NAME=your-bucket-name
    ```

---

## 🔨 Step 2: Build & Start

1.  Build and start all services in the background:
    ```bash
    docker-compose up --build -d
    ```
2.  Wait for the containers to initialize. The first run will download the **GROBID** image (~1GB) and build the Python/Next.js environments.

---

## ✅ Step 3: Verification

### 1. Check Service Status
Ensure all containers are running:
```bash
docker-compose ps
```

### 2. Verify API Health
Open your browser or use `curl`:
```bash
curl http://localhost:5001/api/health
```
**Expected Response**: `{"status": "healthy", "timestamp": ...}`

### 3. Verify Worker Connectivity
Check the worker logs to see if Celery connected to Redis and Postgres:
```bash
docker-compose logs worker
```
Look for: `[info] celery@<hostname> ready.`

### 4. Open the Frontend
Navigate to **`http://localhost:3000`** in your browser. You should see the FixMyPaper landing page.

---

## 🛠️ Troubleshooting

-   **ImportErrors (`ModuleNotFoundError: No module named 'backend'`)**: I have updated the `docker-compose.yml` to use the root context (`.`). If you still see this, run `docker-compose down` and then `docker-compose up --build` again.
-   **S3 Credentials**: If jobs fail with "403 Forbidden" or "No Credentials", double-check your `.env` file and ensure your IAM user has permission to write to the specified bucket.
-   **Port Conflicts**: Ensure ports `3000`, `5001`, `5432`, `6379`, and `8070` are not being used by other local services.
