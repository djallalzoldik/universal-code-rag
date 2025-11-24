import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import ChromeRAGSystem
from chunkers.base_chunker import CodeChunk

def test_hybrid_search():
    print("Initializing RAG System...")
    # Use a temporary collection for testing
    rag = ChromeRAGSystem(collection_name="test_hybrid_search")
    rag.clear_collection()
    
    # Create sample chunks
    # Chunk 1: Semantically related to "login" but no exact keyword
    chunk1 = CodeChunk(
        type="function",
        name="authenticateUser",
        content="def authenticateUser(user, password): return True",
        filepath="auth.py",
        language="python",
        line_start=1,
        line_end=2
    )
    
    # Chunk 2: Contains exact keyword "kMaxRetries" but maybe less semantically relevant to "login"
    chunk2 = CodeChunk(
        type="variable",
        name="kMaxRetries",
        content="const int kMaxRetries = 5;",
        filepath="config.cc",
        language="cpp",
        line_start=1,
        line_end=1
    )
    
    print("Indexing chunks...")
    rag.add_chunks_batch([chunk1, chunk2])
    
    # Force BM25 index rebuild (since we added chunks)
    rag._build_keyword_index()
    
    # Test 1: Search for "login" (Should find chunk1 via Vector)
    print("\n--- Test 1: Search for 'login' ---")
    results = rag.retrieve_context("login")
    for r in results:
        print(f"ID: {r['id']}, Score: {r.get('rrf_score', 'N/A')}, Content: {r['content']}")
        
    # Test 2: Search for "kMaxRetries" (Should find chunk2 via BM25)
    print("\n--- Test 2: Search for 'kMaxRetries' ---")
    results = rag.retrieve_context("kMaxRetries")
    for r in results:
        print(f"ID: {r['id']}, Score: {r.get('rrf_score', 'N/A')}, Content: {r['content']}")
        
    # Verify RRF score exists
    if results and 'rrf_score' in results[0]:
        print("\n✅ Hybrid Search Verified: RRF scores present.")
    else:
        print("\n❌ Hybrid Search Failed: No RRF scores.")

if __name__ == "__main__":
    test_hybrid_search()
