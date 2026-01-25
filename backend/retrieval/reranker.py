"""
Cross-encoder reranking for improved retrieval quality.
Reranks retrieved chunks using a more sophisticated model.
"""

from typing import List, Dict, Tuple
import numpy as np


class Reranker:
    """
    Reranks retrieved chunks using cross-encoder or other reranking strategies.
    """
    
    def __init__(self, strategy: str = "similarity"):
        """
        Initialize reranker.
        
        Args:
            strategy: "similarity" (use existing scores) or "cross-encoder" (future)
        """
        self.strategy = strategy
        self.model = None
        
        if strategy == "cross-encoder":
            # Future: Load cross-encoder model
            # from sentence_transformers import CrossEncoder
            # self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            pass
    
    def rerank(
        self,
        query: str,
        chunks: List[str],
        initial_scores: List[float],
        top_k: int = None
    ) -> Dict:
        """
        Rerank chunks based on query relevance.
        
        Args:
            query: User query
            chunks: List of chunk texts
            initial_scores: Initial similarity scores
            top_k: Number of top results to return (None = all)
        
        Returns:
            Dictionary with reranking results
        """
        if self.strategy == "similarity":
            # Just use existing scores (no reranking)
            reranked_scores = initial_scores
        elif self.strategy == "cross-encoder":
            # Future: Use cross-encoder for reranking
            # pairs = [[query, chunk] for chunk in chunks]
            # reranked_scores = self.model.predict(pairs)
            reranked_scores = initial_scores
        else:
            reranked_scores = initial_scores
        
        # Create ranking data
        ranking_data = [
            {
                "chunk": chunk,
                "initial_score": float(initial_scores[i]),
                "reranked_score": float(reranked_scores[i]),
                "initial_rank": i,
                "reranked_rank": None  # Will be filled after sorting
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Sort by reranked scores
        ranking_data.sort(key=lambda x: x["reranked_score"], reverse=True)
        
        # Update reranked ranks
        for new_rank, item in enumerate(ranking_data):
            item["reranked_rank"] = new_rank
        
        # Calculate reranking impact
        rank_changes = [abs(item["initial_rank"] - item["reranked_rank"]) for item in ranking_data]
        avg_rank_change = np.mean(rank_changes)
        max_rank_change = max(rank_changes)
        
        # Apply top_k filter if specified
        if top_k is not None:
            ranking_data = ranking_data[:top_k]
        
        return {
            "reranked_chunks": [item["chunk"] for item in ranking_data],
            "reranked_scores": [item["reranked_score"] for item in ranking_data],
            "ranking_details": ranking_data,
            "avg_rank_change": float(avg_rank_change),
            "max_rank_change": int(max_rank_change),
            "strategy": self.strategy
        }


def rerank_chunks(
    query: str,
    chunks: List[str],
    scores: List[float],
    strategy: str = "similarity",
    top_k: int = None
) -> Dict:
    """
    Convenience function to rerank chunks.
    
    Args:
        query: User query
        chunks: List of chunk texts
        scores: Initial similarity scores
        strategy: Reranking strategy
        top_k: Number of top results
    
    Returns:
        Reranking results
    """
    reranker = Reranker(strategy=strategy)
    return reranker.rerank(query, chunks, scores, top_k)
