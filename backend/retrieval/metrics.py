"""
Enhanced retrieval metrics for RAG systems.
Calculates Precision@k, Recall@k, MRR, NDCG, coverage, and diversity scores.
"""

from typing import List, Dict, Set
import numpy as np
from collections import Counter


def calculate_precision_at_k(
    retrieved_ids: List[int],
    relevant_ids: List[int],
    k: int = None
) -> float:
    """
    Calculate Precision@k.
    
    Args:
        retrieved_ids: List of retrieved document IDs (in order)
        relevant_ids: List of ground truth relevant document IDs
        k: Number of top results to consider (None = all)
    
    Returns:
        Precision@k score
    """
    if k is not None:
        retrieved_ids = retrieved_ids[:k]
    
    if not retrieved_ids:
        return 0.0
    
    relevant_set = set(relevant_ids)
    num_relevant_retrieved = sum(1 for doc_id in retrieved_ids if doc_id in relevant_set)
    
    return num_relevant_retrieved / len(retrieved_ids)


def calculate_recall_at_k(
    retrieved_ids: List[int],
    relevant_ids: List[int],
    k: int = None
) -> float:
    """
    Calculate Recall@k.
    
    Args:
        retrieved_ids: List of retrieved document IDs
        relevant_ids: List of ground truth relevant document IDs
        k: Number of top results to consider (None = all)
    
    Returns:
        Recall@k score
    """
    if not relevant_ids:
        return 0.0
    
    if k is not None:
        retrieved_ids = retrieved_ids[:k]
    
    relevant_set = set(relevant_ids)
    num_relevant_retrieved = sum(1 for doc_id in retrieved_ids if doc_id in relevant_set)
    
    return num_relevant_retrieved / len(relevant_ids)


def calculate_mrr(
    retrieved_ids: List[int],
    relevant_ids: List[int]
) -> float:
    """
    Calculate Mean Reciprocal Rank (MRR).
    
    Args:
        retrieved_ids: List of retrieved document IDs
        relevant_ids: List of ground truth relevant document IDs
    
    Returns:
        MRR score
    """
    relevant_set = set(relevant_ids)
    
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant_set:
            return 1.0 / rank
    
    return 0.0


def calculate_ndcg(
    retrieved_ids: List[int],
    relevance_scores: Dict[int, float],
    k: int = None
) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain (NDCG@k).
    
    Args:
        retrieved_ids: List of retrieved document IDs
        relevance_scores: Dictionary mapping doc_id to relevance score
        k: Number of top results to consider (None = all)
    
    Returns:
        NDCG@k score
    """
    if k is not None:
        retrieved_ids = retrieved_ids[:k]
    
    if not retrieved_ids:
        return 0.0
    
    # Calculate DCG
    dcg = 0.0
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        relevance = relevance_scores.get(doc_id, 0.0)
        dcg += relevance / np.log2(rank + 1)
    
    # Calculate IDCG (ideal DCG)
    ideal_scores = sorted(relevance_scores.values(), reverse=True)
    if k is not None:
        ideal_scores = ideal_scores[:k]
    
    idcg = 0.0
    for rank, relevance in enumerate(ideal_scores, start=1):
        idcg += relevance / np.log2(rank + 1)
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg


def calculate_coverage_score(
    query: str,
    retrieved_chunks: List[str]
) -> Dict:
    """
    Calculate how well retrieved chunks cover different aspects of the query.
    
    Args:
        query: User query
        retrieved_chunks: List of retrieved chunk texts
    
    Returns:
        Dictionary with coverage metrics
    """
    # Extract key terms from query (simple word-based approach)
    query_words = set(query.lower().split())
    
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'what', 'how',
                  'when', 'where', 'why', 'who', 'which'}
    query_terms = query_words - stop_words
    
    if not query_terms:
        return {
            "coverage_score": 1.0,
            "covered_terms": [],
            "uncovered_terms": [],
            "coverage_percentage": 100.0
        }
    
    # Check which query terms appear in retrieved chunks
    all_chunk_text = " ".join(retrieved_chunks).lower()
    covered_terms = [term for term in query_terms if term in all_chunk_text]
    uncovered_terms = list(query_terms - set(covered_terms))
    
    coverage_score = len(covered_terms) / len(query_terms)
    
    return {
        "coverage_score": float(coverage_score),
        "covered_terms": covered_terms,
        "uncovered_terms": uncovered_terms,
        "coverage_percentage": coverage_score * 100,
        "num_query_terms": len(query_terms)
    }


def calculate_diversity_score(chunks: List[str]) -> Dict:
    """
    Calculate diversity of retrieved chunks.
    Higher diversity = less redundancy.
    
    Args:
        chunks: List of chunk texts
    
    Returns:
        Dictionary with diversity metrics
    """
    if len(chunks) <= 1:
        return {
            "diversity_score": 1.0,
            "avg_pairwise_distance": 1.0,
            "interpretation": "Single or no chunks"
        }
    
    # Calculate pairwise semantic distances
    from backend.explainability.similarity import semantic_similarity
    
    distances = []
    for i in range(len(chunks)):
        for j in range(i + 1, len(chunks)):
            sim = semantic_similarity(chunks[i], chunks[j])
            distance = 1.0 - sim
            distances.append(distance)
    
    avg_distance = np.mean(distances)
    
    # Interpret diversity
    if avg_distance > 0.7:
        interpretation = "High diversity - chunks cover different topics"
    elif avg_distance > 0.4:
        interpretation = "Moderate diversity - some overlap between chunks"
    else:
        interpretation = "Low diversity - chunks are very similar (potential redundancy)"
    
    return {
        "diversity_score": float(avg_distance),
        "avg_pairwise_distance": float(avg_distance),
        "num_pairs": len(distances),
        "interpretation": interpretation
    }


def calculate_retrieval_metrics(
    query: str,
    retrieved_chunks: List[str],
    similarities: List[float],
    ground_truth_ids: List[int] = None,
    retrieved_ids: List[int] = None
) -> Dict:
    """
    Calculate comprehensive retrieval quality metrics.
    
    Args:
        query: User query
        retrieved_chunks: List of retrieved chunk texts
        similarities: Similarity scores for retrieved chunks
        ground_truth_ids: Optional ground truth relevant doc IDs
        retrieved_ids: Optional retrieved doc IDs
    
    Returns:
        Dictionary with all retrieval metrics
    """
    metrics = {}
    
    # Coverage score
    coverage = calculate_coverage_score(query, retrieved_chunks)
    metrics["coverage"] = coverage
    
    # Diversity score
    diversity = calculate_diversity_score(retrieved_chunks)
    metrics["diversity"] = diversity
    
    # Similarity statistics
    if similarities:
        metrics["similarity_stats"] = {
            "mean": float(np.mean(similarities)),
            "std": float(np.std(similarities)),
            "min": float(np.min(similarities)),
            "max": float(np.max(similarities)),
            "median": float(np.median(similarities))
        }
    
    # If ground truth available, calculate precision/recall/MRR/NDCG
    if ground_truth_ids and retrieved_ids:
        for k in [1, 3, 5, 10]:
            if len(retrieved_ids) >= k:
                metrics[f"precision@{k}"] = calculate_precision_at_k(retrieved_ids, ground_truth_ids, k)
                metrics[f"recall@{k}"] = calculate_recall_at_k(retrieved_ids, ground_truth_ids, k)
        
        metrics["mrr"] = calculate_mrr(retrieved_ids, ground_truth_ids)
        
        # For NDCG, use similarities as relevance scores
        if similarities and retrieved_ids:
            relevance_scores = {doc_id: sim for doc_id, sim in zip(retrieved_ids, similarities)}
            metrics["ndcg@5"] = calculate_ndcg(retrieved_ids, relevance_scores, k=5)
            metrics["ndcg@10"] = calculate_ndcg(retrieved_ids, relevance_scores, k=10)
    
    return metrics
