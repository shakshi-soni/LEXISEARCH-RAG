import numpy as np
from rank_bm25 import BM25Okapi # lexical keyword matching
from sentence_transformers import SentenceTransformer


class MemoryIndexer:
    """Handles in-memory indexing using BM25 and Dense Vector embeddings."""
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.embedding_model = SentenceTransformer(model_name)
        self.chunks = []
        self.vectors = None
        self.bm25 = None

    def build_index(self, chunks: list[dict]):
        """Builds both BM25 and vector embeddings for a list of text chunks."""
        if not chunks:
            return

        self.chunks = chunks
        corpus_texts = [c["text"] for c in chunks]

        # 1. Build BM25 Index
        tokenized_corpus = [doc.lower().split() for doc in corpus_texts]
        self.bm25 = BM25Okapi(tokenized_corpus)

        # 2. Build Vector Index (Normalized for Cosine Similarity)
        embeddings = self.embedding_model.encode(corpus_texts, show_progress_bar=False)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10  # Prevent division by zero
        self.vectors = embeddings / norms
