"""
Enhanced hallucination detection with multi-signal approach.
Detects unsupported claims through multiple verification methods.
Now includes sentence-level reasoning for user transparency.
"""

from typing import List, Dict
import re
from sentence_transformers import SentenceTransformer, util

# Initialize embedding model (cached)
embedding_model = None

def get_embedding_model():
    global embedding_model
    if embedding_model is None:
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return embedding_model


def verify_named_entities(answer: str, chunks: List[str]) -> Dict:
    """
    Verify that named entities in answer appear in source chunks.
    Returns details about verified and unverified entities.
    """
    answer_entities = re.findall(r'\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\b', answer)
    
    if not answer_entities:
        return {"risk": 0.0, "verified": [], "unverified": []}
    
    chunks_text = " ".join(chunks)
    
    verified = []
    unverified = []
    for entity in answer_entities:
        if entity in chunks_text:
            verified.append(entity)
        else:
            unverified.append(entity)
    
    risk = len(unverified) / len(answer_entities) if answer_entities else 0.0
    return {"risk": risk, "verified": verified, "unverified": unverified}


def verify_numbers(answer: str, chunks: List[str]) -> Dict:
    """
    Verify that numbers in answer appear in source chunks.
    Returns details about verified and unverified numbers.
    """
    answer_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', answer)
    
    if not answer_numbers:
        return {"risk": 0.0, "verified": [], "unverified": []}
    
    chunks_text = " ".join(chunks)
    chunks_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', chunks_text)
    
    verified = []
    unverified = []
    for num in answer_numbers:
        if num in chunks_numbers:
            verified.append(num)
        else:
            unverified.append(num)
    
    risk = len(unverified) / len(answer_numbers) if answer_numbers else 0.0
    return {"risk": risk, "verified": verified, "unverified": unverified}


def analyze_sentence_hallucination(answer: str, chunks: List[str]) -> List[Dict]:
    """
    Analyze each sentence for potential hallucination.
    Returns list of sentences with their hallucination risk and reasoning.
    """
    sentences = [s.strip() for s in re.split(r'[.!?]+', answer) if s.strip() and len(s.strip()) > 10]
    
    if not sentences or not chunks:
        return []
    
    model = get_embedding_model()
    
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
    chunk_embeddings = model.encode(chunks, convert_to_tensor=True)
    
    sentence_analysis = []
    
    for i, (sentence, sent_emb) in enumerate(zip(sentences, sentence_embeddings)):
        # Find best matching chunk
        similarities = util.cos_sim(sent_emb, chunk_embeddings)[0]
        best_chunk_idx = similarities.argmax().item()
        max_sim = similarities[best_chunk_idx].item()
        
        # Check for specific issues
        issues = []
        
        # Check numbers in this sentence
        sent_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', sentence)
        chunk_text = chunks[best_chunk_idx]
        chunk_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', chunk_text)
        
        for num in sent_numbers:
            if num not in chunk_numbers:
                issues.append(f"Number '{num}' not found in best matching source")
        
        # Check entities
        sent_entities = re.findall(r'\b[A-Z][A-Za-z]+\b', sentence)
        for entity in sent_entities[:3]:  # Check first 3 entities
            if entity not in chunk_text and entity.lower() not in chunk_text.lower():
                issues.append(f"Entity '{entity}' may not be in sources")
        
        # Determine risk level
        if max_sim >= 0.75 and not issues:
            risk_level = "low"
            risk_label = "✅ Low risk"
            explanation = "This sentence is well-supported by the sources"
        elif max_sim >= 0.55:
            risk_level = "moderate"
            risk_label = "⚠️ Moderate risk"
            explanation = "This sentence has partial support but may contain inferences"
        else:
            risk_level = "high"
            risk_label = "❌ High risk"
            explanation = "This sentence may contain hallucinated content"
        
        # Get snippet of best matching chunk
        chunk_snippet = chunk_text[:150] + "..." if len(chunk_text) > 150 else chunk_text
        
        sentence_analysis.append({
            "sentence": sentence,
            "risk_level": risk_level,
            "risk_label": risk_label,
            "explanation": explanation,
            "similarity": float(max_sim),
            "specific_issues": issues,
            "best_matching_chunk_idx": best_chunk_idx,
            "best_matching_chunk_snippet": chunk_snippet
        })
    
    return sentence_analysis


def detect_contradictions(answer: str, chunks: List[str]) -> float:
    """
    Detect if answer contradicts any source chunks.
    """
    negation_patterns = [
        r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bneither\b',
        r'\bnor\b', r'\bwithout\b', r'\blacks\b'
    ]
    
    answer_lower = answer.lower()
    chunks_lower = " ".join(chunks).lower()
    
    answer_negations = sum(1 for pattern in negation_patterns if re.search(pattern, answer_lower))
    chunk_negations = sum(1 for pattern in negation_patterns if re.search(pattern, chunks_lower))
    
    if answer_negations > chunk_negations + 2:
        return 0.5
    
    return 0.0


def enhanced_hallucination_detection(answer: str, chunks: List[str]) -> Dict:
    """
    Multi-signal hallucination detection with detailed reasoning.
    
    Returns:
        Dict with overall risk, component risks, and sentence-level analysis
    """
    if not answer or not chunks:
        return {
            "overall_risk": 1.0,
            "entity_risk": 1.0,
            "number_risk": 1.0,
            "claim_risk": 1.0,
            "contradiction_risk": 0.0,
            "sentence_analysis": [],
            "entity_details": {},
            "number_details": {}
        }
    
    # Signal 1: Named entity verification with details
    entity_result = verify_named_entities(answer, chunks)
    entity_risk = entity_result["risk"]
    
    # Signal 2: Numerical fact checking with details
    number_result = verify_numbers(answer, chunks)
    number_risk = number_result["risk"]
    
    # Signal 3: Sentence-level analysis (NEW)
    sentence_analysis = analyze_sentence_hallucination(answer, chunks)
    
    # Calculate claim risk from sentence analysis
    high_risk_count = sum(1 for s in sentence_analysis if s["risk_level"] == "high")
    claim_risk = high_risk_count / len(sentence_analysis) if sentence_analysis else 0.5
    
    # Signal 4: Contradiction detection
    contradiction_risk = detect_contradictions(answer, chunks)
    
    # Overall risk = weighted average
    overall_risk = (
        0.25 * entity_risk +
        0.25 * number_risk +
        0.35 * claim_risk +  # Sentence analysis is most important
        0.15 * contradiction_risk
    )
    
    return {
        "overall_risk": float(overall_risk),
        "entity_risk": float(entity_risk),
        "number_risk": float(number_risk),
        "claim_risk": float(claim_risk),
        "contradiction_risk": float(contradiction_risk),
        "interpretation": get_hallucination_interpretation(overall_risk),
        "sentence_analysis": sentence_analysis,  # NEW: Per-sentence breakdown
        "entity_details": {  # NEW: Which entities are verified/unverified
            "verified": entity_result["verified"],
            "unverified": entity_result["unverified"]
        },
        "number_details": {  # NEW: Which numbers are verified/unverified
            "verified": number_result["verified"],
            "unverified": number_result["unverified"]
        },
        "high_risk_sentences": high_risk_count,
        "total_sentences": len(sentence_analysis)
    }


def get_hallucination_interpretation(risk: float) -> str:
    """Human-readable interpretation of hallucination risk."""
    if risk < 0.2:
        return "Very low risk - answer well supported by sources"
    elif risk < 0.4:
        return "Low risk - minor unsupported details"
    elif risk < 0.6:
        return "Moderate risk - some claims may be unsupported"
    elif risk < 0.8:
        return "High risk - significant unsupported content"
    else:
        return "Very high risk - answer largely unsupported"
