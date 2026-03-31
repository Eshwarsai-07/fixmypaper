# FixMyPaper 📄✨

FixMyPaper is a production-grade research paper analysis tool. It automates the detection of common errors in academic papers using AI-powered PDF processing.

---

## 🚀 Quick Start (Docker)

The easiest way to run the entire stack (API, Frontend, Worker, DB, and AI services) is via Docker Compose.

1.  **Clone the repository** (if you haven't already).
2.  **Start all services**:
    ```bash
    docker compose up --build
    ```
3.  **Access the applications**:
    -   **Frontend**: [http://localhost:3000](http://localhost:3000)
    -   **API Documentation**: [http://localhost:5001/docs](http://localhost:5001/docs)

---

## 🏗️ Architecture

-   **Frontend**: Next.js (React)
-   **Backend**: FastAPI (Python 3.11)
-   **Background Processing**: Celery + Redis
-   **Database**: PostgreSQL (Structured data & Job tracking)
-   **AI Services**: GROBID (PDF parsing)
-   **Storage**: AWS S3 (Scalable file storage)

---

## 🛠️ Local Development (Manual)

If you prefer to run services manually for debugging:

### 1. Prerequisites
-   Python 3.9+
-   Node.js 18+
-   PostgreSQL & Redis running locally

### 2. Backend Setup
```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Configure environment
cp backend/.env.example backend/.env
# Update backend/.env with your local DB/Redis strings

# Run migrations
cd backend
alembic upgrade head

# Start API
python main.py
```

### 3. Worker Setup
```bash
source venv/bin/activate
cd backend
celery -A app.workers.tasks worker --loglevel=info
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🗄️ Database Migrations

We use **Alembic** to manage database schema changes.

-   **Apply migrations**: `alembic upgrade head`
-   **Create new migration**: `alembic revision --autogenerate -m "description"`
-   **Check status**: `alembic current`

---

## 🔍 Observability & Tracing

FixMyPaper is built with production-grade monitoring in mind:

-   **Correlation IDs**: Every request is assigned a unique `X-Correlation-ID`. This ID is tracked through the API and into background Celery workers, allowing for end-to-end tracing of a single user action.
-   **Structured Logging**: All logs are emitted in JSON format (`structlog`), including metadata like `job_id`, `correlation_id`, and `processing_time`.
-   **Latency Metrics**: Background jobs log their exact `processing_time` upon completion to help identify performance bottlenecks.

---

## 📄 License

MIT
