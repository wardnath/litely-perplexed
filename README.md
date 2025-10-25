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

Pull and run pre-built images from GitHub Container Registry:

```bash
# Download docker-compose.yml
wget https://raw.githubusercontent.com/yourusername/litely-perplexed/main/docker-compose.yml

# Set your GitHub username
export GITHUB_REPOSITORY_OWNER=yourusername

# Start services
docker compose up -d
```

Wait ~30 seconds for SearXNG to initialize, then access:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000/docs
- **SearXNG**: http://localhost:8080

**Test the API**:
```bash
curl "http://localhost:8000/search?q=machine+learning&top_k=5"
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

### Building Custom Images

```bash
# Build backend (includes SearXNG)
docker build -f backend/Dockerfile.prod -t my-backend:latest ./backend

# Build frontend
docker build -f frontend/Dockerfile.prod -t my-frontend:latest ./frontend
```

### GitHub Container Registry

Images are automatically built and published on push to `main`:
- `ghcr.io/yourusername/litely-perplexed-backend:latest`
- `ghcr.io/yourusername/litely-perplexed-frontend:latest`

Multi-arch support: `linux/amd64`, `linux/arm64`

## Limitations

- **No synthesis**: Cannot combine info across sources (extractive only)
- **No reasoning**: Cannot answer "why" or multi-hop questions
- **Source-dependent**: Quality limited to what's in search results
- **No conversational memory**: Each query is independent

## Architecture

**All-in-One Backend Container:**
- SearXNG and FastAPI backend run in single container
- SearXNG starts in background, backend in foreground
- Health checks ensure proper startup order
- Simplified deployment (one pull, one run)

**Multi-Stage Frontend Build:**
- React app built to static files
- Served via nginx for performance
- Optimized caching headers

## Acknowledgments

Inspired by [Perplexica](https://github.com/ItzCrazyKns/Perplexica) - check them out for LLM-powered search with conversational AI!

## License

MIT
