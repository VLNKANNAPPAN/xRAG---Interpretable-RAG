import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_rag_flow():
    # 1. Reset
    requests.delete(f"{BASE_URL}/reset")
    
    # 2. Upload dummy PDF (simulated)
    # We will create a dummy PDF using reportlab or just upload a text file masquerading as PDF if logic permits, 
    # but strictly our loader uses pypdf. Let's use a text file for simplicity first to test metadata flow, 
    # as text file also goes through same pipeline but page=1.
    
    files = {'files': ('test.txt', 'This is a test document.\nIt has some important information.\nThe secret code is 12345.', 'text/plain')}
    resp = requests.post(f"{BASE_URL}/upload", files=files)
    print(f"Upload: {resp.json()}")
    
    # 3. Query
    query = {"query": "What is the secret code?"}
    resp = requests.post(f"{BASE_URL}/query", json=query)
    data = resp.json()
    
    print(f"Answer: {data.get('answer')}")
    print(f"Top Chunks keys: {data.get('top_chunks')[0].keys() if data.get('top_chunks') else 'None'}")
    if data.get('top_chunks'):
        print(f"Sample Chunk: {data['top_chunks'][0]}")

if __name__ == "__main__":
    test_rag_flow()
