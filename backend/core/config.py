from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # SearXNG
    searxng_url: str = "http://searxng:8080"

    # Models
    embedding_model: str = "all-MiniLM-L6-v2"
    cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L6-v2"

    # Retrieval
    bm25_weight: float = 0.5
    top_k: int = 10
    fetch_results: int = 20

    # Summarization
    summary_sentences: int = 3

    # Storage
    index_dir: str = "/data/indexes"
    db_path: str = "/data/vectors.db"

    class Config:
        env_file = ".env"

settings = Settings()
