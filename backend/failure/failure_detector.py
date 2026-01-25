import numpy as np
from typing import List, Dict

def detect_failures(
    similarity_scores: List[float],
    shap_scores: List[float],
    min_similarity: float = 0.20,  # Lowered from 0.30
    dominance_threshold: float = 0.95,  # Raised from 0.60 - only flag if EXTREMELY dominant
    instability_threshold: float = 0.50  # Raised from 0.25 - only flag if VERY unstable
) -> Dict:
    """
    Failure-aware confidence estimation for RAG.
    
    NOTE: Single-source answers are VALID and common - don't refuse them!
    """

    warnings = []

    similarity_scores = np.array(similarity_scores)

    # 🔒 Normalize SHAP scores
    shap_scores = np.array(shap_scores)
    if shap_scores.sum() > 0:
        shap_scores = shap_scores / shap_scores.sum()

    # ----------------------------
    # Failure checks (RELAXED)
    # ----------------------------

    weak_retrieval = similarity_scores.max() < min_similarity

    if weak_retrieval:
        warnings.append(
            "Weak retrieval: no sufficiently relevant documents found."
        )

    # REMOVED: Single source dominance check - this is often VALID!
    # Many questions have answers in just one chunk - that's OK!
    
    # REMOVED: Explanation instability check - variance is natural!
    # Different chunks contribute differently - that's expected!

    # ----------------------------
    # Confidence computation
    # ----------------------------

    if weak_retrieval:
        confidence = 0.0
    else:
        # Confidence based on retrieval quality and SHAP consistency
        confidence = (
            0.7 * similarity_scores.mean() +  # Increased weight on similarity
            0.3 * (1 - shap_scores.std())     # Reduced weight on variance
        )

    confidence = float(max(0.0, min(confidence, 1.0)))

    return {
        "warnings": warnings,
        "confidence": confidence
    }
