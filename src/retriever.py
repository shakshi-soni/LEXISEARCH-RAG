import numpy as np


def retrieve_hybrid(query: str, indexer, top_k: int = 5, rrf_k: int = 60):
    """Performs RRF Hybrid Search combining BM25 and Dense Vector search."""
    if not indexer or not indexer.chunks or indexer.bm25 is None or indexer.vectors is None:
        return []

    # 1. Lexical BM25 Retrieval
    bm25_scores = indexer.bm25.get_scores(query.lower().split())
    bm25_ranked_indices = np.argsort(bm25_scores)[::-1]

    # 2. Vector Dense Retrieval
    query_vector = indexer.embedding_model.encode([query])
    q_norm = np.linalg.norm(query_vector)
    if q_norm > 0:
        query_vector = query_vector / q_norm
        
    similarity_scores = np.dot(indexer.vectors, query_vector.T).squeeze()
    if similarity_scores.ndim == 0:
        similarity_scores = np.array([similarity_scores])
        
    vector_ranked_indices = np.argsort(similarity_scores)[::-1]

    # 3. Reciprocal Rank Fusion (RRF)
    rrf_scores = {}
    
    for rank, idx in enumerate(bm25_ranked_indices[:top_k * 2]):
        idx_item = int(idx)
        rrf_scores[idx_item] = rrf_scores.get(idx_item, 0.0) + (1.0 / (rrf_k + (rank + 1)))

    for rank, idx in enumerate(vector_ranked_indices[:top_k * 2]):
        idx_item = int(idx)
        rrf_scores[idx_item] = rrf_scores.get(idx_item, 0.0) + (1.0 / (rrf_k + (rank + 1)))

    # 4. Sort indices and extract results
    sorted_rrf_indices = sorted(rrf_scores.keys(), key=lambda i: rrf_scores[i], reverse=True)
    return [indexer.chunks[i] for i in sorted_rrf_indices[:top_k]]