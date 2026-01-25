from typing import Dict


def should_refuse(response: Dict, confidence_threshold: float = 0.2) -> Dict:  # Lowered from 0.4
    """
    Determines whether the system should refuse to answer.
    
    NOTE: We should RARELY refuse - only when retrieval truly fails.
    Single-source answers and variance are NORMAL and VALID.
    """

    reasons = []

    # Only refuse if confidence is VERY low
    if response["confidence"] < confidence_threshold:
        reasons.append(
            f"Low confidence ({response['confidence']:.2f})"
        )

    # Only refuse on weak retrieval - other warnings are informational only
    for warning in response["warnings"]:
        if "Weak retrieval" in warning:
            reasons.append("Insufficient evidence")
        # REMOVED: Unstable explanation check - this is NORMAL!

    if reasons:
        return {
            "refuse": True,
            "reasons": reasons
        }

    return {
        "refuse": False,
        "reasons": []
    }
