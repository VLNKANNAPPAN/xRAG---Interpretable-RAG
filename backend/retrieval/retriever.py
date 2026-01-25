from backend.embeddings.embedder import embed_texts
import numpy as np

def retrieve(query, index, docs, k=10):  # Increased from 5 to 10
    """
    Retrieve top-k documents with similarity scores and diversity filtering.
    Compatible with docs as list[str].
    """

    k = min(k, len(docs))
    q_emb = embed_texts([query])
    
    # Retrieve more candidates for diversity filtering
    k_candidates = min(k * 3, len(docs))  # Get 3x more candidates
    scores, indices = index.search(q_emb, k_candidates)

    # Filter for diversity - remove very similar chunks
    results = []
    seen_texts = []
    diversity_threshold = 0.85  # Chunks must be <85% similar to each other
    
    for idx, score in zip(indices[0], scores[0]):
        chunk_text = docs[idx]
        
        # Check diversity against already selected chunks
        is_diverse = True
        for seen_text in seen_texts:
            # Simple diversity check: avoid exact duplicates or very similar chunks
            if chunk_text == seen_text:
                is_diverse = False
                break
            # Check text overlap
            words_chunk = set(chunk_text.lower().split())
            words_seen = set(seen_text.lower().split())
            if len(words_chunk) > 0 and len(words_seen) > 0:
                overlap = len(words_chunk & words_seen) / len(words_chunk | words_seen)
                if overlap > diversity_threshold:
                    is_diverse = False
                    break
        
        if is_diverse:
            results.append({
                "text": chunk_text,
                "similarity": float(score)
            })
            seen_texts.append(chunk_text)
            
            if len(results) >= k:
                break
    
    return results
