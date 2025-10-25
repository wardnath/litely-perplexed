from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Dict, Tuple
from core.config import settings

class HybridSearch:
    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model)
        self.embeddings_cache = {}

    def embed_query(self, query: str) -> np.ndarray:
        """Encode query to embedding"""
        return self.model.encode(query, convert_to_numpy=True)

    def embed_documents(self, docs: List[Dict]) -> List[np.ndarray]:
        """Encode documents to embeddings"""
        texts = [f"{d.get('title', '')} {d.get('text', '')}" for d in docs]
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    def semantic_search(self, query_embedding: np.ndarray, doc_embeddings: List[np.ndarray], docs: List[Dict], top_k: int = 10) -> List[Dict]:
        """Semantic search via cosine similarity"""
        # Compute cosine similarities
        similarities = util.cos_sim(query_embedding, np.array(doc_embeddings))[0].cpu().numpy()

        # Sort by similarity
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            doc = docs[idx].copy()
            doc['semantic_score'] = float(similarities[idx])
            results.append(doc)

        return results

    def bm25_simple(self, query: str, docs: List[Dict], top_k: int = 10) -> List[Dict]:
        """Simple BM25-like scoring (term frequency)"""
        query_terms = set(query.lower().split())

        scores = []
        for doc in docs:
            text = f"{doc.get('title', '')} {doc.get('text', '')}".lower()
            score = sum(text.count(term) for term in query_terms)
            scores.append(score)

        # Normalize
        max_score = max(scores) if scores else 1
        scores = [s / max_score for s in scores]

        # Sort by score
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            doc = docs[idx].copy()
            doc['bm25_score'] = scores[idx]
            results.append(doc)

        return results

    def hybrid_rank(self, query: str, docs: List[Dict], top_k: int = 10) -> List[Dict]:
        """Hybrid BM25 + semantic ranking"""
        if not docs:
            return []

        # Get embeddings
        query_embedding = self.embed_query(query)
        doc_embeddings = self.embed_documents(docs)

        # Semantic scores
        semantic_sims = util.cos_sim(query_embedding, np.array(doc_embeddings))[0].cpu().numpy()

        # BM25-like scores
        query_terms = set(query.lower().split())
        bm25_scores = []
        for doc in docs:
            text = f"{doc.get('title', '')} {doc.get('text', '')}".lower()
            score = sum(text.count(term) for term in query_terms)
            bm25_scores.append(score)

        # Normalize
        max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
        bm25_scores = [s / max_bm25 for s in bm25_scores]

        # Hybrid score
        alpha = settings.bm25_weight
        hybrid_scores = [
            alpha * bm25 + (1 - alpha) * semantic
            for bm25, semantic in zip(bm25_scores, semantic_sims)
        ]

        # Sort by hybrid score
        top_indices = np.argsort(hybrid_scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            doc = docs[idx].copy()
            doc['bm25_score'] = float(bm25_scores[idx])
            doc['semantic_score'] = float(semantic_sims[idx])
            doc['hybrid_score'] = float(hybrid_scores[idx])
            results.append(doc)

        return results

    def mmr(self, query: str, docs: List[Dict], top_k: int = 10, lambda_param: float = 0.5) -> List[Dict]:
        """Maximal Marginal Relevance for diversity"""
        if not docs or len(docs) <= top_k:
            return docs

        query_embedding = self.embed_query(query)
        doc_embeddings = np.array(self.embed_documents(docs))

        # Relevance scores
        relevance = util.cos_sim(query_embedding, doc_embeddings)[0].cpu().numpy()

        selected = []
        remaining = list(range(len(docs)))

        # Select first (most relevant)
        first_idx = np.argmax(relevance)
        selected.append(remaining.pop(first_idx))

        # Iteratively select
        while len(selected) < top_k and remaining:
            mmr_scores = []
            for idx in remaining:
                rel = relevance[idx]
                # Max similarity to already selected
                max_sim = max(
                    util.cos_sim(doc_embeddings[idx], doc_embeddings[sel])[0][0].item()
                    for sel in selected
                )
                mmr = lambda_param * rel - (1 - lambda_param) * max_sim
                mmr_scores.append(mmr)

            best_idx = np.argmax(mmr_scores)
            selected.append(remaining.pop(best_idx))

        return [docs[i] for i in selected]
