import sqlite3
import json
import os
from typing import List, Dict, Any

DB_PATH = "rag_metadata.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT,
            content TEXT,
            num_chunks INTEGER
        )
    ''')
    # Added metadata column
    c.execute('''
        CREATE TABLE IF NOT EXISTS chunks (
            id TEXT PRIMARY KEY,
            doc_id TEXT,
            chunk_index INTEGER,
            text TEXT,
            metadata TEXT,
            FOREIGN KEY(doc_id) REFERENCES documents(id)
        )
    ''')
    conn.commit()
    conn.close()

def save_document_metadata(doc_id: str, filename: str, content: str, chunks: List[str], metadatas: List[Dict] = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Save document info
    c.execute('INSERT OR REPLACE INTO documents VALUES (?, ?, ?, ?)', 
              (doc_id, filename, content, len(chunks)))
    
    # Save chunks
    for i, chunk_text in enumerate(chunks):
        chunk_id = f"{doc_id}_{i}"
        meta_json = json.dumps(metadatas[i]) if metadatas and i < len(metadatas) else "{}"
        c.execute('INSERT OR REPLACE INTO chunks VALUES (?, ?, ?, ?, ?)',
                  (chunk_id, doc_id, i, chunk_text, meta_json))
                  
    conn.commit()
    conn.close()

def get_all_documents():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, filename, num_chunks FROM documents')
    docs = [{"id": r[0], "filename": r[1], "num_chunks": r[2]} for r in c.fetchall()]
    conn.close()
    return docs

def get_chunk_text(doc_id: str, chunk_index: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT text FROM chunks WHERE doc_id = ? AND chunk_index = ?', (doc_id, chunk_index))
    result = c.fetchone()
    conn.close()
    return result[0] if result else ""

def get_all_chunks() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, text, doc_id, metadata FROM chunks')
    
    results = []
    for r in c.fetchall():
        try:
            meta = json.loads(r[3]) if r[3] else {}
        except:
            meta = {}
            
        results.append({
            "id": r[0], 
            "text": r[1], 
            "doc_id": r[2],
            "metadata": meta
        })
        
    conn.close()
    return results

def clear_db():
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except OSError:
            pass
    init_db()
