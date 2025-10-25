# Embedding-Only Search

Self-hosted research tool using **SearXNG + BM25 + embeddings + TextRank**. No LLMs, no GPU required.

## Stack
- **Search**: SearXNG (metasearch)
- **Extraction**: Trafilatura (content extraction)
- **Retrieval**: BM25 (term frequency) + Sentence-Transformers (semantic)
- **Summarization**: TextRank (extractive, no hallucinations)
- **API**: FastAPI (async Python)

## Quick Start

1. **Start services**:
```bash
docker-compose up -d
```

2. **Wait for models to download** (~1 minute on first run)

3. **Access the UI**:
```
Frontend: http://localhost:23156
API Docs: http://localhost:27341/docs
SearXNG:  http://localhost:19482
```

4. **Test the API**:
```bash
# Simple search
curl "http://localhost:27341/search?q=quantum%20computing&top_k=5"

# With cluster summary
curl "http://localhost:27341/search?q=climate%20change&top_k=10&cluster_summary=true"

# With MMR diversity
curl "http://localhost:27341/search?q=machine%20learning&use_mmr=true"
```

5. **Or use the test script**:
```bash
cd backend
python test_api.py
```

## API Endpoints

### `GET /search`
Main search endpoint with hybrid ranking and summarization.

**Parameters**:
- `q` (required): Search query
- `top_k` (default: 10): Number of results
- `summarize` (default: true): Generate per-doc summaries
- `cluster_summary` (default: false): Generate overall summary
- `use_mmr` (default: false): Use MMR for diversity

**Example Response**:
```json
{
  "query": "quantum computing",
  "cluster_summary": "Quantum computing leverages quantum mechanics...",
  "results": [
    {
      "url": "https://example.com/article",
      "title": "Introduction to Quantum Computing",
      "text": "Full article text...",
      "summary": "Extractive summary of key points...",
      "bm25_score": 0.85,
      "semantic_score": 0.92,
      "hybrid_score": 0.885
    }
  ],
  "total": 10
}
```

### `GET /health`
Service health check.

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

Edit `.env` or `docker-compose.yml` environment variables:

```bash
# Model selection
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Fast, 384 dims, CPU-friendly

# Ranking weights
BM25_WEIGHT=0.5  # 0.0 = pure semantic, 1.0 = pure BM25

# Result counts
FETCH_RESULTS=20  # Fetch from SearXNG
TOP_K=10          # Return to user

# Summarization
SUMMARY_SENTENCES=3  # Per-document summary length
```

## Features

✅ **No LLM required** - Uses classical IR + embeddings
✅ **No GPU required** - Runs on any CPU
✅ **No hallucinations** - Extractive summaries only
✅ **Fast** - Sub-second response times
✅ **Private** - Fully self-hosted
✅ **Deterministic** - Same query → same results
✅ **Transparent** - Scores are interpretable (BM25 + cosine)

## Development

Run locally without Docker:

```bash
# Install dependencies
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Start SearXNG separately
docker run -d -p 8080:8080 searxng/searxng

# Run API
python main.py
```

## Limitations

- **No synthesis**: Cannot combine info across sources (extractive only)
- **No reasoning**: Cannot answer "why" or multi-hop questions
- **Source-dependent**: Quality limited to what's in search results
- **No conversational memory**: Each query is independent

## Future Enhancements

- [ ] Add ColBERT token-level matching
- [ ] Implement query expansion with WordNet
- [ ] Add Redis caching for repeated queries
- [ ] Build simple web UI
- [ ] Add cross-encoder reranking option
- [ ] Persistent vector store (pgvector/Qdrant)

## License

MIT
