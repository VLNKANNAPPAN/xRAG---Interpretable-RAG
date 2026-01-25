from typing import List, Tuple
from backend.explainability.similarity import semantic_similarity
from backend.generation.generator import generate_answer


def shap_attribution(
    query: str,
    chunks: List[str],
    similarities: List[float]
) -> Tuple[str, List[Tuple[str, float]]]:

    base_answer = generate_answer(query, chunks)
    raw_scores = []

    for i, chunk in enumerate(chunks):
        reduced_chunks = chunks[:i] + chunks[i + 1:]

        if not reduced_chunks:
            impact = 1.0
        else:
            new_answer = generate_answer(query, reduced_chunks)
            impact = 1.0 - semantic_similarity(base_answer, new_answer)

        weighted = impact * float(similarities[i])
        raw_scores.append((chunk, weighted))

    total = sum(score for _, score in raw_scores)
    if total > 0:
        normalized = [(c, s / total) for c, s in raw_scores]
    else:
        normalized = raw_scores

    return base_answer, normalized
