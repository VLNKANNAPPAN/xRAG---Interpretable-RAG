from sentence_transformers import SentenceTransformer
import faiss
import numpy as np




model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_texts(texts):
    return model.encode(texts, normalize_embeddings=True)

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index

def retrieve(query, index, docs, k=5):
    q_emb = embed_texts([query])
    scores, indices = index.search(q_emb, k)
    
    results = []
    for i, score in zip(indices[0], scores[0]):
        results.append((docs[i], float(score)))
    
    return results
