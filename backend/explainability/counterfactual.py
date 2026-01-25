"""
Counterfactual explanation generation for RAG systems.
Shows how answer changes when chunks are removed (leave-one-out analysis).
"""

from typing import List, Dict
import numpy as np
from backend.generation.generator import generate_answer
from backend.explainability.similarity import semantic_similarity


def generate_counterfactual_explanations(
    query: str,
    chunks: List[str],
    base_answer: str = None,
    max_chunks_to_test: int = None
) -> Dict:
    """
    Generate counterfactual explanations by removing chunks one at a time.
    
    Args:
        query: User query
        chunks: List of retrieved chunks
        base_answer: Original answer (if None, will generate)
        max_chunks_to_test: Maximum number of chunks to test (None = all)
    
    Returns:
        Dictionary with counterfactual analysis
    """
    # Generate base answer if not provided
    if base_answer is None:
        base_answer = generate_answer(query, chunks)
    
    # Limit number of chunks to test for performance
    if max_chunks_to_test is not None:
        chunks_to_test = min(len(chunks), max_chunks_to_test)
    else:
        chunks_to_test = len(chunks)
    
    counterfactuals = []
    
    for i in range(chunks_to_test):
        # Create reduced chunk list (remove chunk i)
        reduced_chunks = chunks[:i] + chunks[i + 1:]
        
        if not reduced_chunks:
            # If no chunks left, answer would be empty/refused
            counterfactual_answer = "[No chunks available]"
            similarity_to_base = 0.0
            impact = 1.0
        else:
            # Generate answer without this chunk
            counterfactual_answer = generate_answer(query, reduced_chunks)
            
            # Calculate similarity to base answer
            similarity_to_base = semantic_similarity(base_answer, counterfactual_answer)
            
            # Impact = how much answer changed (1 - similarity)
            impact = 1.0 - similarity_to_base
        
        counterfactuals.append({
            "removed_chunk_index": i,
            "removed_chunk": chunks[i],
            "counterfactual_answer": counterfactual_answer,
            "similarity_to_base": float(similarity_to_base),
            "impact_score": float(impact),
            "answer_changed": impact > 0.1  # Threshold for significant change
        })
    
    # Sort by impact (highest impact first)
    counterfactuals.sort(key=lambda x: x["impact_score"], reverse=True)
    
    # Identify critical chunks (high impact when removed)
    critical_chunks = [cf for cf in counterfactuals if cf["impact_score"] > 0.3]
    
    # Calculate statistics
    impact_scores = [cf["impact_score"] for cf in counterfactuals]
    
    return {
        "base_answer": base_answer,
        "counterfactuals": counterfactuals,
        "critical_chunks": critical_chunks,
        "num_critical_chunks": len(critical_chunks),
        "avg_impact": float(np.mean(impact_scores)) if impact_scores else 0.0,
        "max_impact": float(np.max(impact_scores)) if impact_scores else 0.0,
        "num_chunks_tested": chunks_to_test
    }


def identify_critical_chunks(
    query: str,
    chunks: List[str],
    base_answer: str = None,
    impact_threshold: float = 0.3
) -> List[Dict]:
    """
    Identify chunks that are critical to the answer.
    
    Args:
        query: User query
        chunks: List of chunks
        base_answer: Original answer
        impact_threshold: Minimum impact to be considered critical
    
    Returns:
        List of critical chunk information
    """
    cf_results = generate_counterfactual_explanations(query, chunks, base_answer)
    
    critical = []
    for cf in cf_results["counterfactuals"]:
        if cf["impact_score"] >= impact_threshold:
            critical.append({
                "chunk_index": cf["removed_chunk_index"],
                "chunk_text": cf["removed_chunk"],
                "impact_score": cf["impact_score"],
                "interpretation": _interpret_impact(cf["impact_score"])
            })
    
    return critical


def _interpret_impact(impact: float) -> str:
    """Provide human-readable interpretation of impact score."""
    if impact > 0.7:
        return "Critical - answer changes significantly without this chunk"
    elif impact > 0.4:
        return "Important - answer changes moderately without this chunk"
    elif impact > 0.2:
        return "Relevant - answer changes slightly without this chunk"
    else:
        return "Minor - answer remains largely unchanged without this chunk"
