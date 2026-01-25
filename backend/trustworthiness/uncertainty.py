"""
Uncertainty quantification for RAG systems.
Separates epistemic (model) and aleatoric (data) uncertainty.
"""

from typing import List, Dict
import numpy as np
from backend.generation.generator import generate_answer


def calculate_entropy(probabilities: List[float]) -> float:
    """
    Calculate Shannon entropy of probability distribution.
    
    Args:
        probabilities: List of probabilities (should sum to 1)
    
    Returns:
        Entropy value (higher = more uncertain)
    """
    probs = np.array(probabilities)
    probs = probs[probs > 0]  # Remove zeros to avoid log(0)
    
    if len(probs) == 0:
        return 0.0
    
    entropy = -np.sum(probs * np.log2(probs))
    return float(entropy)


def quantify_uncertainty(
    query: str,
    chunks: List[str],
    num_samples: int = 5,
    shap_scores: List[float] = None
) -> Dict:
    """
    Quantify uncertainty in RAG answer generation.
    
    Args:
        query: User query
        chunks: Retrieved chunks
        num_samples: Number of samples for ensemble
        shap_scores: SHAP attribution scores (optional)
    
    Returns:
        Dictionary with uncertainty metrics
    """
    # Epistemic uncertainty: Generate multiple answers
    answers = []
    for _ in range(num_samples):
        answer = generate_answer(query, chunks)
        answers.append(answer)
    
    # Calculate answer diversity (epistemic uncertainty)
    from backend.explainability.similarity import semantic_similarity
    
    similarities = []
    for i in range(len(answers)):
        for j in range(i + 1, len(answers)):
            sim = semantic_similarity(answers[i], answers[j])
            similarities.append(sim)
    
    if similarities:
        avg_similarity = np.mean(similarities)
        epistemic_uncertainty = 1.0 - avg_similarity  # High diversity = high uncertainty
    else:
        epistemic_uncertainty = 0.0
    
    # Aleatoric uncertainty: Based on retrieval quality
    # If chunks have low similarity to query, data uncertainty is high
    if shap_scores:
        # Use SHAP score distribution as proxy for data uncertainty
        shap_entropy = calculate_entropy(shap_scores)
        # Normalize by max possible entropy
        max_entropy = np.log2(len(shap_scores)) if len(shap_scores) > 1 else 1.0
        aleatoric_uncertainty = shap_entropy / max_entropy if max_entropy > 0 else 0.0
    else:
        aleatoric_uncertainty = 0.5  # Default moderate uncertainty
    
    # Total uncertainty
    total_uncertainty = (epistemic_uncertainty + aleatoric_uncertainty) / 2
    
    return {
        "total_uncertainty": float(total_uncertainty),
        "epistemic_uncertainty": float(epistemic_uncertainty),
        "aleatoric_uncertainty": float(aleatoric_uncertainty),
        "answer_diversity": 1.0 - avg_similarity if similarities else 0.0,
        "num_samples": num_samples,
        "interpretation": _interpret_uncertainty(total_uncertainty)
    }


def _interpret_uncertainty(uncertainty: float) -> str:
    """Provide human-readable interpretation of uncertainty."""
    if uncertainty < 0.2:
        return "Very confident - high agreement across samples"
    elif uncertainty < 0.4:
        return "Confident - moderate agreement"
    elif uncertainty < 0.6:
        return "Uncertain - significant variation in answers"
    elif uncertainty < 0.8:
        return "Very uncertain - high disagreement"
    else:
        return "Extremely uncertain - answers are highly inconsistent"


def estimate_token_uncertainty(
    answer: str,
    token_probabilities: List[float] = None
) -> Dict:
    """
    Estimate uncertainty at token level (if token probabilities available).
    
    Args:
        answer: Generated answer
        token_probabilities: Probability of each token (if available from LLM)
    
    Returns:
        Dictionary with token-level uncertainty metrics
    """
    if token_probabilities is None:
        # Fallback: estimate based on answer length and complexity
        words = answer.split()
        estimated_uncertainty = min(0.5, len(words) / 100)  # Longer = more uncertain
        
        return {
            "token_level_uncertainty": estimated_uncertainty,
            "avg_token_probability": None,
            "min_token_probability": None,
            "entropy": None,
            "note": "Token probabilities not available - using length-based estimate"
        }
    
    # Calculate metrics from token probabilities
    probs = np.array(token_probabilities)
    
    return {
        "token_level_uncertainty": float(1.0 - np.mean(probs)),
        "avg_token_probability": float(np.mean(probs)),
        "min_token_probability": float(np.min(probs)),
        "entropy": calculate_entropy(probs.tolist()),
        "low_confidence_tokens": int(np.sum(probs < 0.5))
    }
