# Litely Perplexed

Self-hosted AI-powered search using **SearXNG + BM25 + embeddings + TextRank**. No LLMs, no GPU required.

[![Docker Build](https://github.com/yourusername/litely-perplexed/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/yourusername/litely-perplexed/actions/workflows/docker-publish.yml)

## Features

✅ **Hybrid Search** - BM25 + semantic embeddings for best results
✅ **Key Passages** - Semantically relevant 8-word snippets extracted
✅ **Extractive Summaries** - TextRank TLDR with no hallucinations
✅ **No LLM/GPU Required** - Pure CPU, runs anywhere
✅ **Fully Self-Hosted** - Complete privacy, no external APIs
✅ **Production Ready** - Pre-built Docker images on GHCR

## Tech Stack
- **Search**: SearXNG (bundled metasearch)
- **Extraction**: Trafilatura (content extraction)
- **Retrieval**: BM25 + Sentence-Transformers (all-MiniLM-L6-v2)
- **Summarization**: TextRank (extractive, spaCy)
- **Backend**: FastAPI (async Python)
- **Frontend**: React + TypeScript + Tailwind

## Quick Start (Production)

Single unified image with frontend, backend, and SearXNG:

```bash
# Pull and run from GitHub Container Registry
docker run -d \
  -p 3000:3000 \
  -p 8080:8080 \
  -v litely-perplexed-data:/data \
  --name litely-perplexed \
  ghcr.io/yourusername/litely-perplexed:latest
```

Or use docker-compose:

```bash
# Download docker-compose.yml
wget https://raw.githubusercontent.com/yourusername/litely-perplexed/main/docker-compose.yml

# Set your GitHub username
export GITHUB_REPOSITORY_OWNER=yourusername

# Start
docker compose up -d
```

Wait ~30 seconds for SearXNG to initialize, then access:
- **Web UI**: http://localhost:3000
- **API**: http://localhost:3000/docs
- **SearXNG**: http://localhost:8080 (optional)

**Test**:
```bash
curl "http://localhost:3000/search?q=machine+learning&top_k=5"
```

## Development

For local development with hot-reload:

```bash
# Clone repository
git clone https://github.com/yourusername/litely-perplexed.git
cd litely-perplexed

# Start dev environment
docker compose -f docker-compose.dev.yml up -d

# Access dev servers
# Frontend: http://localhost:23156 (Vite HMR)
# Backend: http://localhost:27341 (auto-reload)
# SearXNG: http://localhost:19482
```

## API Endpoints

### `GET /search`
Hybrid search with BM25 + semantic ranking, extractive summarization, and key passage extraction.

**Parameters**:
- `q` (required): Search query
- `top_k` (default: 10): Number of results to return

**Response Fields**:
- `original_rank`: Position from SearXNG
- `final_rank`: Position after hybrid reranking
- `bm25_score`: Term frequency score (0-1)
- `semantic_score`: Embedding similarity (0-1)
- `hybrid_score`: Weighted combination
- `summary`: 2-sentence TextRank extractive summary
- `key_passages`: Array of 5 semantically relevant 8-word snippets

**Example**:
```bash
curl "http://localhost:8000/search?q=python+programming&top_k=3"
```

### `GET /health`
Health check endpoint (returns 200 OK).

## Pipeline

```
User Query
    ↓
SearXNG Meta-Search (top 20 results)
    ↓
Trafilatura Content Extraction (parallel)
    ↓
Hybrid Ranking:
  - BM25 (term frequency scoring)
  - Semantic (cosine similarity with embeddings)
  - Weighted combination (default: 50/50)
    ↓
Optional MMR Diversification (reduce duplicates)
    ↓
TextRank Extractive Summarization
    ↓
JSON Response with Citations
```

## Configuration

Create a `.env` file to customize settings:

```bash
# Docker Registry (for production)
GITHUB_REPOSITORY_OWNER=yourusername
VERSION=latest

# Ports
BACKEND_PORT=8000
SEARXNG_PORT=8080
FRONTEND_PORT=3000

# Model (CPU-friendly, no GPU needed)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Search Settings
BM25_WEIGHT=0.5        # 0.0 = pure semantic, 1.0 = pure BM25
TOP_K=10               # Results to return
FETCH_RESULTS=20       # Fetch from SearXNG
SUMMARY_SENTENCES=2    # TextRank summary length
```

## Deployment

### Building Custom Image

```bash
# Build unified image (frontend + backend + SearXNG)
docker build -t my-litely-perplexed:latest .
```

### GitHub Container Registry

Single unified image is automatically built and published on push to `main`:
- `ghcr.io/yourusername/litely-perplexed:latest`

Multi-arch support: `linux/amd64`, `linux/arm64`

**What's inside the image:**
- SearXNG (metasearch engine on port 8080)
- FastAPI backend (search API)
- React frontend (web UI)
- All served from a single container on port 3000

## Limitations

- **No synthesis**: Cannot combine info across sources (extractive only)
- **No reasoning**: Cannot answer "why" or multi-hop questions
- **Source-dependent**: Quality limited to what's in search results
- **No conversational memory**: Each query is independent

## Architecture

**Single Unified Container (like Perplexica):**
- Frontend, Backend, and SearXNG all in one image
- Multi-stage Docker build:
  1. Build React frontend to static files
  2. Install Python backend + dependencies
  3. Install SearXNG from source
- Entrypoint orchestration:
  1. Start SearXNG in background
  2. Wait for health check
  3. Start FastAPI (serves API + static frontend)
- Simplified deployment: one pull, one run!

## Acknowledgments

Inspired by [Perplexica](https://github.com/ItzCrazyKns/Perplexica) - check them out for LLM-powered search with conversational AI!

## License

MIT
