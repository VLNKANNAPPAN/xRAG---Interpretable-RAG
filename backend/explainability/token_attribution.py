"""
Token-level attribution for answer generation.
Maps answer sentences back to source chunks with contribution scores.
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


def calculate_token_attribution(
    answer: str,
    chunks: List[str],
    shap_scores: List[float] = None
) -> Dict:
    """
    Calculate token/sentence-level attribution for the answer.
    
    Args:
        answer: Generated answer text
        chunks: Source chunks
        shap_scores: Optional SHAP scores for chunks
    
    Returns:
        Dictionary with token-level attribution data
    """
    # Split answer into sentences
    answer_sentences = _split_into_sentences(answer)
    
    if not answer_sentences:
        return {
            "sentence_attributions": [],
            "chunk_to_sentences": {},
            "citations": []
        }
    
    # For each answer sentence, find most similar chunk
    sentence_attributions = []
    
    for sent_idx, sentence in enumerate(answer_sentences):
        # Calculate similarity to each chunk
        similarities = []
        for chunk in chunks:
            sim = semantic_similarity(sentence, chunk)
            similarities.append(sim)
        
        # Find best matching chunk
        if similarities:
            best_chunk_idx = int(np.argmax(similarities))
            best_similarity = float(similarities[best_chunk_idx])
            
            # Calculate contribution intensity (0-1)
            # Combine similarity with SHAP score if available
            if shap_scores and best_chunk_idx < len(shap_scores):
                contribution = (best_similarity + shap_scores[best_chunk_idx]) / 2
            else:
                contribution = best_similarity
        else:
            best_chunk_idx = None
            best_similarity = 0.0
            contribution = 0.0
        
        sentence_attributions.append({
            "sentence": sentence,
            "sentence_index": sent_idx,
            "source_chunk_index": best_chunk_idx,
            "similarity": best_similarity,
            "contribution_intensity": float(contribution),
            "color_intensity": _get_color_intensity(contribution)
        })
    
    # Create reverse mapping: chunk -> sentences
    chunk_to_sentences = {}
    for sent_attr in sentence_attributions:
        chunk_idx = sent_attr["source_chunk_index"]
        if chunk_idx is not None:
            if chunk_idx not in chunk_to_sentences:
                chunk_to_sentences[chunk_idx] = []
            chunk_to_sentences[chunk_idx].append({
                "sentence": sent_attr["sentence"],
                "sentence_index": sent_attr["sentence_index"],
                "contribution": sent_attr["contribution_intensity"]
            })
    
    # Generate citation markers
    citations = []
    for sent_attr in sentence_attributions:
        if sent_attr["source_chunk_index"] is not None:
            citations.append({
                "sentence_index": sent_attr["sentence_index"],
                "chunk_index": sent_attr["source_chunk_index"],
                "citation_marker": f"[{sent_attr['source_chunk_index'] + 1}]"
            })
    
    return {
        "sentence_attributions": sentence_attributions,
        "chunk_to_sentences": chunk_to_sentences,
        "citations": citations,
        "num_sentences": len(answer_sentences)
    }


def _get_color_intensity(contribution: float) -> str:
    """
    Get color intensity category for visualization.
    
    Args:
        contribution: Contribution score (0-1)
    
    Returns:
        Color intensity category
    """
    if contribution > 0.7:
        return "very-high"
    elif contribution > 0.5:
        return "high"
    elif contribution > 0.3:
        return "medium"
    elif contribution > 0.1:
        return "low"
    else:
        return "very-low"


def create_highlighted_answer(
    answer: str,
    attribution_data: Dict
) -> str:
    """
    Create HTML-formatted answer with color-coded highlighting.
    
    Args:
        answer: Original answer text
        attribution_data: Output from calculate_token_attribution
    
    Returns:
        HTML string with highlighted answer
    """
    sentence_attrs = attribution_data["sentence_attributions"]
    citations = attribution_data["citations"]
    
    # Create citation map
    citation_map = {c["sentence_index"]: c["citation_marker"] for c in citations}
    
    # Build highlighted HTML
    html_parts = []
    for sent_attr in sentence_attrs:
        sentence = sent_attr["sentence"]
        intensity = sent_attr["color_intensity"]
        sent_idx = sent_attr["sentence_index"]
        
        # Add citation marker if available
        citation = citation_map.get(sent_idx, "")
        
        # Create span with color intensity class
        html_parts.append(
            f'<span class="highlight-{intensity}" data-chunk="{sent_attr["source_chunk_index"]}">'
            f'{sentence} {citation}'
            f'</span>'
        )
    
    return " ".join(html_parts)
