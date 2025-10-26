# Multi-stage build: Frontend build stage
FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Backend + SearXNG stage
FROM python:3.11-slim

# Install all dependencies
RUN apt-get update && apt-get install -y \
    # Python build dependencies
    build-essential \
    curl \
    git \
    # SearXNG dependencies
    python3-dev python3-babel python3-venv \
    uwsgi uwsgi-plugin-python3 \
    libxslt-dev zlib1g-dev libffi-dev libssl-dev \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python backend dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy backend code
COPY backend/ ./

# Copy built frontend from frontend-builder
COPY --from=frontend-builder /app/frontend/dist ./public

# Create SearXNG user
RUN useradd --shell /bin/bash --system \
    --home-dir "/usr/local/searxng" \
    --comment 'Privacy-respecting metasearch engine' \
    searxng

# Create SearXNG directories
RUN mkdir -p "/usr/local/searxng" /etc/searxng
RUN chown -R "searxng:searxng" "/usr/local/searxng" /etc/searxng

# Copy SearXNG configuration
COPY backend/searxng-config/settings.yml /etc/searxng/settings.yml
COPY backend/searxng-config/limiter.toml /etc/searxng/limiter.toml
COPY backend/searxng-config/uwsgi.ini /etc/searxng/uwsgi.ini
RUN chown -R searxng:searxng /etc/searxng

# Switch to searxng user to install SearXNG
USER searxng

# Clone and install SearXNG
RUN git clone "https://github.com/searxng/searxng" \
    "/usr/local/searxng/searxng-src"

RUN python3 -m venv "/usr/local/searxng/searx-pyenv"
RUN "/usr/local/searxng/searx-pyenv/bin/pip" install --upgrade pip setuptools wheel pyyaml msgspec
RUN cd "/usr/local/searxng/searxng-src" && \
    "/usr/local/searxng/searx-pyenv/bin/pip" install --use-pep517 --no-build-isolation -e .

# Switch back to root
USER root

# Copy unified entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh || true

# Allow searxng user sudo
RUN echo "searxng ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Create data directory
RUN mkdir -p /data/indexes

# Expose ports
EXPOSE 3000 8080

# Environment
ENV SEARXNG_URL=http://localhost:8080
ENV PYTHONUNBUFFERED=1

# Run unified entrypoint
CMD ["/app/entrypoint.sh"]
