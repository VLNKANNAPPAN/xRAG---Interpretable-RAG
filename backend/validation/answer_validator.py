"""
Answer validation and post-processing.
Ensures answers are grounded and properly formatted.
"""

from typing import List, Optional, Dict
import re


def remove_unsupported_claims(answer: str, chunks: List[str], threshold: float = 0.5) -> str:
    """
    Remove sentences from answer that aren't supported by chunks.
    
    Args:
        answer: Generated answer
        chunks: Source chunks
        threshold: Minimum similarity to keep a sentence
    
    Returns:
        Filtered answer with only supported claims
    """
    from sentence_transformers import SentenceTransformer, util
    
    # Split into sentences
    sentences = [s.strip() for s in re.split(r'[.!?]+', answer) if s.strip()]
    
    if not sentences:
        return answer
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Embed sentences and chunks
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
    chunk_embeddings = model.encode(chunks, convert_to_tensor=True)
    
    # Keep only supported sentences
    supported_sentences = []
    for i, sent_emb in enumerate(sentence_embeddings):
        similarities = util.cos_sim(sent_emb, chunk_embeddings)[0]
        max_sim = similarities.max().item()
        
        if max_sim >= threshold:
            supported_sentences.append(sentences[i])
    
    if not supported_sentences:
        return None  # No supported content
    
    # Reconstruct answer
    return ". ".join(supported_sentences) + "."


def verify_numbers_in_answer(answer: str, chunks: List[str]) -> bool:
    """
    Verify all numbers in answer appear in chunks.
    Returns False if any number is hallucinated.
    """
    answer_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', answer)
    
    if not answer_numbers:
        return True  # No numbers to verify
    
    chunks_text = " ".join(chunks)
    chunks_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', chunks_text)
    
    # All numbers must appear in chunks
    return all(num in chunks_numbers for num in answer_numbers)


def answers_query(answer: str, query: str) -> bool:
    """
    Check if answer actually addresses the query.
    """
    if not answer or len(answer) < 10:
        return False
    
    # Extract key terms from query
    query_words = set(query.lower().split())
    stop_words = {'is', 'are', 'the', 'a', 'an', 'what', 'how', 'why', 'when', 'where', 'who'}
    query_keywords = query_words - stop_words
    
    if not query_keywords:
        return True  # Can't determine, give benefit of doubt
    
    # Check if answer mentions key query terms
    answer_lower = answer.lower()
    mentioned_keywords = sum(1 for keyword in query_keywords if keyword in answer_lower)
    
    # At least 30% of keywords should be mentioned
    coverage = mentioned_keywords / len(query_keywords)
    return coverage >= 0.3


def validate_answer(answer: str, chunks: List[str], query: str) -> Optional[Dict]:
    """
    Comprehensive answer validation.
    
    Returns:
        Dict with validated answer and validation details, or None if invalid
    """
    if not answer or not chunks:
        return None
    
    # Check 1: Does it answer the query?
    if not answers_query(answer, query):
        return {
            "valid": False,
            "reason": "Answer does not address the query",
            "answer": None
        }
    
    # Check 2: Verify numbers
    if not verify_numbers_in_answer(answer, chunks):
        return {
            "valid": False,
            "reason": "Answer contains unverified numbers",
            "answer": None
        }
    
    # Check 3: Remove unsupported claims
    filtered_answer = remove_unsupported_claims(answer, chunks, threshold=0.5)
    
    if not filtered_answer:
        return {
            "valid": False,
            "reason": "No supported claims found in answer",
            "answer": None
        }
    
    # Check 4: Minimum length
    if len(filtered_answer) < 20:
        return {
            "valid": False,
            "reason": "Answer too short after filtering",
            "answer": None
        }
    
    return {
        "valid": True,
        "reason": "Answer passed all validation checks",
        "answer": filtered_answer,
        "original_answer": answer,
        "filtered": answer != filtered_answer
    }
