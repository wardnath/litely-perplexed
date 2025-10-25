from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from core.config import settings
from services.searxng_client import SearXNGClient
from services.extractor import ContentExtractor
from services.hybrid_search import HybridSearch
from services.summarizer import Summarizer

router = APIRouter()

# Initialize services
searxng = SearXNGClient()
extractor = ContentExtractor()
search_engine = HybridSearch()
summarizer = Summarizer()

# Share embedding model with summarizer for key passages
summarizer.set_embedding_model(search_engine.model)

class SearchResponse(BaseModel):
    query: str
    cluster_summary: Optional[str] = None
    results: List[dict]
    total: int

@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Search query"),
    top_k: int = Query(10, description="Number of results"),
):
    """
    Simplified search endpoint:
    1. Query SearXNG
    2. Extract content from top results
    3. BM25 + semantic hybrid ranking
    4. Return with original_rank and final_rank
    """
    try:
        # Step 1: SearXNG search
        search_results = await searxng.search(q, num_results=settings.fetch_results)

        if not search_results:
            return SearchResponse(query=q, results=[], total=0)

        # Step 2: Extract content in parallel
        extract_tasks = [extractor.extract(r["url"]) for r in search_results]
        extracted = await asyncio.gather(*extract_tasks)

        # Filter successful extractions and track original rank
        docs = []
        for idx, (orig, ext) in enumerate(zip(search_results, extracted)):
            if ext and ext.get("text"):
                docs.append({
                    "url": ext["url"],
                    "title": ext.get("title") or orig.get("title", ""),
                    "text": ext["text"],
                    "author": ext.get("author"),
                    "date": ext.get("date"),
                    "original_rank": idx + 1,  # Track original SearXNG ranking
                })

        if not docs:
            return SearchResponse(query=q, results=[], total=0)

        # Step 3: BM25 + semantic hybrid ranking
        ranked = search_engine.hybrid_rank(q, docs, top_k=top_k)

        # Step 4: Add extractive summaries (TextRank TLDR - shorter)
        ranked = summarizer.summarize_docs(ranked, num_sentences=2)

        # Step 5: Extract key passages (top 5 semantically relevant segments)
        ranked = summarizer.extract_passages_for_docs(ranked, q, num_passages=5)

        # Add final rank
        for idx, doc in enumerate(ranked):
            doc["final_rank"] = idx + 1

        return SearchResponse(
            query=q,
            results=ranked,
            total=len(ranked)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def shutdown():
    """Cleanup on shutdown"""
    await searxng.close()
    await extractor.close()
