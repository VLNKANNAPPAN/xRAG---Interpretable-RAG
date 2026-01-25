import os
from typing import List, Dict, Any
import pypdf

def load_text_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def load_pdf_file(file_path: str) -> List[Dict[str, Any]]:
    segments = []
    try:
        reader = pypdf.PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            content = page.extract_text()
            if content:
                segments.append({
                    "text": content,
                    "page": i + 1
                })
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return []
    return segments

def load_document(file_path: str) -> Dict[str, Any]:
    """
    Loads a document and returns a dictionary with metadata and segmented content.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    segments = [] # List[Dict] with 'text' and 'page' (optional)
    full_content = ""
    
    if ext == ".txt":
        text = load_text_file(file_path)
        full_content = text
        segments = [{"text": text, "page": 1}]
    elif ext == ".pdf":
        segments = load_pdf_file(file_path)
        full_content = "\n".join([s["text"] for s in segments])
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
        
    return {
        "filename": os.path.basename(file_path),
        "content": full_content,
        "segments": segments,
        "type": ext
    }
