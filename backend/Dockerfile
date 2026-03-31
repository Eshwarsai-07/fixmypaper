# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim as runtime

WORKDIR /app

# Install runtime system dependencies for PDF processing (Camelot/OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    ghostscript \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY . .

# Set Python path to find the backend module
ENV PYTHONPATH=/app

# Default command can be overridden for worker
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:10000", "backend.app.main:app"]
