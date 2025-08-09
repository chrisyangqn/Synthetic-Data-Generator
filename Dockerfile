# syntax=docker/dockerfile:1

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system deps
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
       curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Default envs
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434 \
    PYTHONUNBUFFERED=1

# Default entrypoint runs the client; pass arguments after image name
ENTRYPOINT ["python", "ollama_client.py"]