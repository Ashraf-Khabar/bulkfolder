# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Avoid .pyc, make logs immediate
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (matplotlib needs some libs even if you don't render)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (better layer cache)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src /app/src
COPY pyproject.toml /app/pyproject.toml
COPY README.md /app/README.md

# Make package importable
ENV PYTHONPATH=/app/src

# Default: show help for CLI
CMD ["python", "-m", "bulkfolder.cli", "--help"]