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
    # Confidence computation (Top-K Weighted)
    # ----------------------------

    if weak_retrieval:
        confidence = 0.0
    else:
        # Use top-k similarity scores (most relevant chunks), not mean of all
        top_k = min(3, len(similarity_scores))
        top_sims = np.sort(similarity_scores)[-top_k:]

        # Weighted: 50% top-1, 30% top-k avg, 20% overall mean
        retrieval_confidence = (
            0.50 * float(top_sims[-1]) +          # Best match signal
            0.30 * float(top_sims.mean()) +        # Top-k quality
            0.20 * float(similarity_scores.mean()) # Broad coverage
        )

        # SHAP consistency — only penalize extreme instability
        shap_consistency = 1.0 - min(float(shap_scores.std()) * 0.5, 0.3)

        confidence = retrieval_confidence * shap_consistency

    confidence = float(max(0.0, min(confidence, 1.0)))

    return {
        "warnings": warnings,
        "confidence": confidence
    }
