import pytextrank
import spacy
import numpy as np
from typing import List, Dict
from core.config import settings

class Summarizer:
    def __init__(self):
        # Load spacy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Download if not available
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

        # Add pytextrank to pipeline
        self.nlp.add_pipe("textrank")

        # Import here to avoid circular dependency
        self.embedding_model = None

    def summarize(self, text: str, num_sentences: int = None) -> str:
        """Extract key sentences using TextRank"""
        if not text:
            return ""

        num_sentences = num_sentences or settings.summary_sentences

        doc = self.nlp(text)

        # Get top sentences
        sentences = []
        for sent in doc._.textrank.summary(limit_sentences=num_sentences):
            sentences.append(str(sent))

        return " ".join(sentences)

    def summarize_docs(self, docs: List[Dict], num_sentences: int = None) -> List[Dict]:
        """Summarize each document"""
        results = []
        for doc in docs:
            text = doc.get("text", "")
            summary = self.summarize(text, num_sentences)
            doc_copy = doc.copy()
            doc_copy["summary"] = summary
            results.append(doc_copy)
        return results

    def cluster_summarize(self, docs: List[Dict], num_sentences: int = None) -> str:
        """Create summary across all documents"""
        # Combine all text
        all_text = " ".join(doc.get("text", "") for doc in docs)

        # Summarize combined text
        return self.summarize(all_text, num_sentences)

    def set_embedding_model(self, model):
        """Set the embedding model for semantic passage extraction"""
        self.embedding_model = model

    def extract_key_passages(self, text: str, query: str, num_passages: int = 5, max_words: int = 8) -> List[str]:
        """Extract semantically relevant short passages from text"""
        if not text or not query or self.embedding_model is None:
            return []

        # Split text into sentences
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

        if not sentences:
            return []

        # Create sliding windows of phrases (up to max_words)
        passages = []
        for sent in sentences:
            words = sent.split()
            # Create windows of different sizes (4-8 words)
            for size in range(4, min(max_words + 1, len(words) + 1)):
                for i in range(len(words) - size + 1):
                    passage = " ".join(words[i:i+size])
                    passages.append(passage)

        if not passages:
            # Fallback: just use sentences truncated to max_words
            passages = [" ".join(sent.split()[:max_words]) for sent in sentences]

        # Deduplicate and limit
        passages = list(set(passages))[:100]  # Limit to 100 for performance

        if not passages:
            return []

        # Encode passages and query
        from sentence_transformers import util
        passage_embeddings = self.embedding_model.encode(passages, convert_to_numpy=True, show_progress_bar=False)
        query_embedding = self.embedding_model.encode(query, convert_to_numpy=True)

        # Compute similarities
        similarities = util.cos_sim(query_embedding, passage_embeddings)[0].cpu().numpy()

        # Get top N
        top_indices = np.argsort(similarities)[::-1][:num_passages]

        # Return top passages
        return [passages[idx] for idx in top_indices]

    def extract_passages_for_docs(self, docs: List[Dict], query: str, num_passages: int = 5) -> List[Dict]:
        """Extract key passages for each document"""
        results = []
        for doc in docs:
            text = doc.get("text", "")
            key_passages = self.extract_key_passages(text, query, num_passages)
            doc_copy = doc.copy()
            doc_copy["key_passages"] = key_passages
            results.append(doc_copy)
        return results
