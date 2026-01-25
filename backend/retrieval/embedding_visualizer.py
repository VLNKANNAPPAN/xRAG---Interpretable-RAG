"""
Embedding space visualization using dimensionality reduction.
Creates 2D/3D projections of query and chunk embeddings.
"""

from typing import List, Dict
import numpy as np
from sklearn.manifold import TSNE
import warnings

warnings.filterwarnings('ignore')


def create_embedding_visualization(
    query_embedding: np.ndarray,
    chunk_embeddings: List[np.ndarray],
    retrieved_indices: List[int],
    method: str = "tsne",
    n_components: int = 2,
    perplexity: int = 30
) -> Dict:
    """
    Create 2D or 3D visualization of embedding space.
    
    Args:
        query_embedding: Query embedding vector
        chunk_embeddings: List of chunk embedding vectors
        retrieved_indices: Indices of retrieved chunks
        method: "tsne" or "umap"
        n_components: 2 or 3 for 2D/3D visualization
        perplexity: Perplexity parameter for t-SNE
    
    Returns:
        Dictionary with visualization data
    """
    # Combine query and chunk embeddings
    all_embeddings = np.vstack([query_embedding.reshape(1, -1)] + chunk_embeddings)
    
    # Adjust perplexity if needed
    max_perplexity = (len(all_embeddings) - 1) // 3
    perplexity = min(perplexity, max(5, max_perplexity))
    
    # Apply dimensionality reduction
    if method == "tsne":
        reducer = TSNE(
            n_components=n_components,
            perplexity=perplexity,
            random_state=42
        )
        coords = reducer.fit_transform(all_embeddings)
    elif method == "umap":
        try:
            from umap import UMAP
            reducer = UMAP(
                n_components=n_components,
                random_state=42,
                n_neighbors=min(15, len(all_embeddings) - 1)
            )
            coords = reducer.fit_transform(all_embeddings)
        except ImportError:
            # Fallback to t-SNE if UMAP not installed
            reducer = TSNE(n_components=n_components, perplexity=perplexity, random_state=42)
            coords = reducer.fit_transform(all_embeddings)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Separate query and chunk coordinates
    query_coords = coords[0].tolist()
    chunk_coords = coords[1:].tolist()
    
    # Create visualization data
    points = []
    
    # Add query point
    if n_components == 2:
        points.append({
            "x": query_coords[0],
            "y": query_coords[1],
            "type": "query",
            "label": "Query",
            "retrieved": True
        })
    else:  # 3D
        points.append({
            "x": query_coords[0],
            "y": query_coords[1],
            "z": query_coords[2],
            "type": "query",
            "label": "Query",
            "retrieved": True
        })
    
    # Add chunk points
    retrieved_set = set(retrieved_indices)
    for i, coords_point in enumerate(chunk_coords):
        is_retrieved = i in retrieved_set
        
        if n_components == 2:
            points.append({
                "x": coords_point[0],
                "y": coords_point[1],
                "type": "chunk",
                "label": f"Chunk {i}",
                "retrieved": is_retrieved,
                "chunk_index": i
            })
        else:  # 3D
            points.append({
                "x": coords_point[0],
                "y": coords_point[1],
                "z": coords_point[2],
                "type": "chunk",
                "label": f"Chunk {i}",
                "retrieved": is_retrieved,
                "chunk_index": i
            })
    
    return {
        "points": points,
        "method": method,
        "n_components": n_components,
        "num_chunks": len(chunk_embeddings),
        "num_retrieved": len(retrieved_indices)
    }


def create_quick_2d_visualization(
    query_embedding: np.ndarray,
    all_chunk_embeddings: List[np.ndarray],
    retrieved_indices: List[int],
    chunk_texts: List[str] = None
) -> Dict:
    """
    Quick 2D visualization with sensible defaults.
    
    Args:
        query_embedding: Query embedding
        all_chunk_embeddings: All chunk embeddings
        retrieved_indices: Indices of retrieved chunks
        chunk_texts: Optional chunk texts for tooltips
    
    Returns:
        Visualization data ready for frontend
    """
    viz_data = create_embedding_visualization(
        query_embedding,
        all_chunk_embeddings,
        retrieved_indices,
        method="tsne",
        n_components=2,
        perplexity=min(30, len(all_chunk_embeddings) // 3)
    )
    
    # Add chunk texts if provided
    if chunk_texts:
        for point in viz_data["points"]:
            if point["type"] == "chunk":
                chunk_idx = point["chunk_index"]
                if chunk_idx < len(chunk_texts):
                    # Truncate text for tooltip
                    text = chunk_texts[chunk_idx]
                    point["text"] = text[:200] + "..." if len(text) > 200 else text
    
    return viz_data
