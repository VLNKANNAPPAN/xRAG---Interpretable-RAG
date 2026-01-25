"""
Hallucination detection for RAG systems.
Identifies statements in generated answers that are not grounded in source documents.
"""

from typing import List, Dict, Tuple
import numpy as np
from backend.explainability.similarity import semantic_similarity
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


def _split_into_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    try:
        sentences = nltk.sent_tokenize(text)
        return [s.strip() for s in sentences if s.strip()]
    except:
        return [s.strip() + '.' for s in text.split('.') if s.strip()]


def _extract_claims(text: str) -> List[str]:
    """
    Extract factual claims from text.
    For now, we treat each sentence as a claim.
    Future: Use more sophisticated claim extraction.
    """
    return _split_into_sentences(text)


def _verify_claim_against_chunks(claim: str, chunks: List[str], threshold: float = 0.6) -> Dict:
    """
    Verify if a claim is supported by any chunk.
    
    Args:
        claim: The claim to verify
        chunks: List of source chunks
        threshold: Minimum similarity to consider claim supported
    
    Returns:
        Dictionary with verification results
    """
    if not chunks:
        return {
            "supported": False,
            "max_similarity": 0.0,
            "supporting_chunk_idx": None
        }
    
    # Calculate similarity with each chunk
    similarities = []
    for chunk in chunks:
        sim = semantic_similarity(claim, chunk)
        similarities.append(sim)
    
    max_sim = max(similarities)
    max_idx = similarities.index(max_sim)
    
    return {
        "supported": max_sim >= threshold,
        "max_similarity": float(max_sim),
        "supporting_chunk_idx": max_idx if max_sim >= threshold else None,
        "supporting_chunk": chunks[max_idx] if max_sim >= threshold else None
    }


def detect_hallucinations(
    answer: str,
    chunks: List[str],
    similarity_threshold: float = 0.6,
    return_details: bool = False
) -> Dict:
    """
    Detect potential hallucinations in generated answer.
    
    Args:
        answer: Generated answer text
        chunks: List of retrieved source chunks
        similarity_threshold: Minimum similarity for claim to be considered supported
        return_details: If True, return detailed per-claim analysis
    
    Returns:
        Dictionary with:
            - hallucination_risk: Overall risk score (0-1)
            - flagged_statements: List of potentially hallucinated statements
            - num_claims: Total number of claims
            - num_unsupported: Number of unsupported claims
            - claim_details: Per-claim verification (if return_details=True)
    """
    # Extract claims from answer
    claims = _extract_claims(answer)
    
    if not claims:
        return {
            "hallucination_risk": 0.0,
            "flagged_statements": [],
            "num_claims": 0,
            "num_unsupported": 0
        }
    
    # Verify each claim
    claim_details = []
    flagged_statements = []
    
    for claim in claims:
        verification = _verify_claim_against_chunks(claim, chunks, similarity_threshold)
        
        claim_info = {
            "claim": claim,
            "supported": verification["supported"],
            "max_similarity": verification["max_similarity"],
            "supporting_chunk_idx": verification["supporting_chunk_idx"]
        }
        
        claim_details.append(claim_info)
        
        if not verification["supported"]:
            flagged_statements.append(claim)
    
    # Calculate overall hallucination risk
    num_unsupported = len(flagged_statements)
    hallucination_risk = num_unsupported / len(claims) if claims else 0.0
    
    result = {
        "hallucination_risk": float(hallucination_risk),
        "flagged_statements": flagged_statements,
        "num_claims": len(claims),
        "num_unsupported": num_unsupported,
        "support_rate": 1.0 - hallucination_risk
    }
    
    if return_details:
        result["claim_details"] = claim_details
    
    return result


def self_consistency_check(
    query: str,
    chunks: List[str],
    num_samples: int = 3,
    temperature: float = 0.7
) -> Dict:
    """
    Generate answer multiple times and check consistency.
    High variance indicates potential hallucination or uncertainty.
    
    Args:
        query: User query
        chunks: Retrieved chunks
        num_samples: Number of times to generate answer
        temperature: Temperature for generation (higher = more variation)
    
    Returns:
        Dictionary with consistency metrics
    """
    from backend.generation.generator import generate_answer
    
    # Generate multiple answers
    answers = []
    for _ in range(num_samples):
        # Note: Current generator doesn't support temperature parameter
        # This is a placeholder for future enhancement
        answer = generate_answer(query, chunks)
        answers.append(answer)
    
    # Calculate pairwise similarities
    similarities = []
    for i in range(len(answers)):
        for j in range(i + 1, len(answers)):
            sim = semantic_similarity(answers[i], answers[j])
            similarities.append(sim)
    
    if similarities:
        consistency_score = np.mean(similarities)
        consistency_variance = np.var(similarities)
    else:
        consistency_score = 1.0
        consistency_variance = 0.0
    
    # Flag as unstable if consistency is low
    is_unstable = consistency_score < 0.7
    
    return {
        "consistency_score": float(consistency_score),
        "consistency_variance": float(consistency_variance),
        "is_unstable": is_unstable,
        "num_samples": num_samples,
        "answers": answers if num_samples <= 5 else answers[:5]  # Limit returned answers
    }
