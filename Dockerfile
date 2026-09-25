# Use official lightweight Python image
FROM python:3.11-slim-bookworm

# Set metadata labels
LABEL maintainer="KaayakaSetu Team"
LABEL description="KaayakaSetu Blue-Collar Workforce Microservice Platform"

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    DB_PATH=/app/data/bluecollar.db

# Set working directory
WORKDIR /app

# Install system dependencies (curl for healthchecks and debugging)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user and group
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/bash -m appuser

# Install Python dependencies first for optimal Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create data directory for persistent SQLite database and set ownership
RUN mkdir -p /app/data && chown -R appuser:appgroup /app

# Copy application source code
COPY --chown=appuser:appgroup app/ ./app/
COPY --chown=appuser:appgroup run.py ./
COPY --chown=appuser:appgroup README.md ./

# Switch to non-root user
USER appuser

# Expose microservice application port
EXPOSE 8000

# Docker health check endpoint
HEALTHCHECK --interval=20s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://127.0.0.1:${PORT:-8000}/health || exit 1

# Start the unified microservices server
CMD ["python", "run.py"]
