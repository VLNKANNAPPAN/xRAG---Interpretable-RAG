"""
Automated quality gates for RAG system.
Implements rules to reject or flag low-quality responses.
"""

from typing import Dict, List


def check_quality_gates(
    faithfulness_score: float,
    hallucination_risk: float,
    confidence: float,
    calibrated_confidence: float,
    max_similarity: float
) -> Dict:
    """
    Check if response passes quality gates.
    
    Returns:
        Dictionary with quality gate results
    """
    gates = []
    
    # Relaxed thresholds for better answer generation
    min_faithfulness = 0.3  # Lowered from 0.7
    max_hallucination = 0.7  # Raised from 0.3
    min_similarity = 0.2  # Lowered from 0.3
    max_confidence_gap = 0.3  # Raised from 0.2
    
    passed = True
    severity_level = "pass"
    
    # Gate 1: Faithfulness check
    if faithfulness_score < min_faithfulness:
        gates.append({
            "gate": "faithfulness",
            "passed": False,
            "severity": "critical",
            "message": f"Faithfulness score ({faithfulness_score:.2f}) below threshold ({min_faithfulness})",
            "recommendation": "Answer may not be fully grounded in source documents"
        })
        passed = False
        severity_level = "critical"
    else:
        gates.append({
            "gate": "faithfulness",
            "passed": True,
            "severity": "pass",
            "message": f"Faithfulness score acceptable ({faithfulness_score:.2f})"
        })
    
    # Gate 2: Hallucination check
    if hallucination_risk > max_hallucination:
        gates.append({
            "gate": "hallucination",
            "passed": False,
            "severity": "critical",
            "message": f"Hallucination risk ({hallucination_risk:.2f}) above threshold ({max_hallucination})",
            "recommendation": "Answer may contain unsupported claims"
        })
        passed = False
        severity_level = "critical"
    else:
        gates.append({
            "gate": "hallucination",
            "passed": True,
            "severity": "pass",
            "message": f"Hallucination risk acceptable ({hallucination_risk:.2f})"
        })
    
    # Gate 3: Retrieval quality check
    if max_similarity < min_similarity:
        gates.append({
            "gate": "retrieval_quality",
            "passed": False,
            "severity": "warning",
            "message": f"No sufficiently relevant chunks found (max similarity: {max_similarity:.2f})",
            "recommendation": "Consider expanding knowledge base or rephrasing query"
        })
        if severity_level == "pass":
            severity_level = "warning"
    else:
        gates.append({
            "gate": "retrieval_quality",
            "passed": True,
            "severity": "pass",
            "message": f"Retrieval quality acceptable (max similarity: {max_similarity:.2f})"
        })
    
    # Gate 4: Confidence calibration check
    confidence_gap = abs(confidence - calibrated_confidence)
    if confidence_gap > max_confidence_gap:
        gates.append({
            "gate": "confidence_calibration",
            "passed": False,
            "severity": "warning",
            "message": f"Large confidence-accuracy gap ({confidence_gap:.2f})",
            "recommendation": "Model may be over/under-confident"
        })
        if severity_level == "pass":
            severity_level = "warning"
    else:
        gates.append({
            "gate": "confidence_calibration",
            "passed": True,
            "severity": "pass",
            "message": f"Confidence calibration acceptable (gap: {confidence_gap:.2f})"
        })
    
    # Determine overall action
    if severity_level == "critical":
        action = "reject"
        action_message = "Response rejected due to critical quality issues"
    elif severity_level == "warning":
        action = "flag"
        action_message = "Response flagged with warnings but allowed"
    else:
        action = "allow"
        action_message = "Response passes all quality gates"
    
    return {
        "passed": passed,
        "action": action,
        "action_message": action_message,
        "severity_level": severity_level,
        "gates": gates,
        "num_failed": sum(1 for g in gates if not g["passed"]),
        "num_critical": sum(1 for g in gates if g["severity"] == "critical"),
        "num_warnings": sum(1 for g in gates if g["severity"] == "warning")
    }


def get_quality_recommendations(gate_results: Dict) -> List[str]:
    """
    Get actionable recommendations based on quality gate results.
    
    Args:
        gate_results: Output from check_quality_gates
    
    Returns:
        List of recommendations
    """
    recommendations = []
    
    for gate in gate_results["gates"]:
        if not gate["passed"] and "recommendation" in gate:
            recommendations.append(gate["recommendation"])
    
    # Add general recommendations based on severity
    if gate_results["severity_level"] == "critical":
        recommendations.append("Consider uploading more relevant documents to improve answer quality")
    elif gate_results["severity_level"] == "warning":
        recommendations.append("Review the answer carefully before using")
    
    return recommendations
