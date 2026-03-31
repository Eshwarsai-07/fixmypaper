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

# Fix: Backend context is already 'backend', so requirements.txt is at root
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim as runtime

WORKDIR /app

# Install runtime system dependencies for PDF processing (Camelot/OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    ghostscript \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY . .

# Set Python path to find the backend module
ENV PYTHONPATH=/app

EXPOSE 10000

# Fix: If root is backend, the module path is app.main:app
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:10000", "app.main:app"]
