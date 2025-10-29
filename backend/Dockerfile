# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    ffmpeg \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy entire application
COPY . .

# Create necessary directories
RUN mkdir -p /app/storage/resumes && \
    mkdir -p /app/alembic/versions

# Create __init__.py files if missing (ensure Python recognizes directories)
RUN touch app/__init__.py \
    app/api/__init__.py \
    app/api/v1/__init__.py \
    app/api/v1/endpoints/__init__.py \
    app/models/__init__.py \
    app/schemas/__init__.py \
    app/services/__init__.py \
    app/agents/__init__.py \
    app/tools/__init__.py \
    app/core/__init__.py \
    app/utils/__init__.py

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application using run.py
CMD ["python", "run.py"]
