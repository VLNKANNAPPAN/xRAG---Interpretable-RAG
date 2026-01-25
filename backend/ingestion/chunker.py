from typing import List, Dict, Tuple

def chunk_documents(segments: List[Dict], chunk_size: int = 400, overlap: int = 50) -> Tuple[List[str], List[Dict]]:
    """
    Chunks a list of document segments (e.g. pages) into smaller chunks while preserving metadata.
    
    Args:
        segments: List of dicts, each containing "text" and optional metadata like "page".
        chunk_size: Target number of words per chunk.
        overlap: Number of overlapping words between chunks.
        
    Returns:
        Tuple of (list of text chunks, list of metadata dicts corresponding to chunks)
    """
    all_chunks_text = []
    all_chunks_metadata = []
    
    for segment in segments:
        text = segment.get("text", "")
        # Basic space splitting (can be improved to use recursive character splitter)
        words = text.split()
        
        if not words:
            continue
            
        # If segment is smaller than chunk size, just use it as one chunk
        if len(words) <= chunk_size:
            chunk_text = " ".join(words)
            all_chunks_text.append(chunk_text)
            all_chunks_metadata.append(segment) # Inherit all segment metadata (e.g. page)
            continue
            
        # Sliding window
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i : i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            all_chunks_text.append(chunk_text)
            all_chunks_metadata.append(segment) # Inherit metadata
            
            # Stop if we reached end
            if i + chunk_size >= len(words):
                break
                
    return all_chunks_text, all_chunks_metadata