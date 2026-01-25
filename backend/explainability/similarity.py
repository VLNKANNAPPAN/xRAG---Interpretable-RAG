from backend.embeddings.embedder import embed_texts
from sklearn.metrics.pairwise import cosine_similarity

def semantic_similarity(text_a: str, text_b: str) -> float:
    """
    Measures semantic similarity between two texts using embeddings.
    Returns value in [0, 1].
    """
    embeddings = embed_texts([text_a, text_b])
    sim = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    return float(sim)
