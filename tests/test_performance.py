import sys
import os
import time
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import ChromeRAGSystem
from indexer import ChromeIndexer
from utils.state_manager import StateManager
from utils.logger import setup_logger

def test_performance():
    setup_logger(level="INFO")
    
    db_path = "./test_db"
    state_db = "index_state.db"
    test_samples = "./test_samples"
    
    # Clean up
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
    if os.path.exists(state_db):
        os.remove(state_db)
        
    print("\n=== Starting Performance Test ===")
    
    rag = ChromeRAGSystem(db_path=db_path)
    indexer = ChromeIndexer(rag)
    
    # 1. First Indexing (Cold Start)
    print("\n[1] Cold Indexing (Parallel)...")
    start_time = time.time()
    stats = indexer.index_directory(test_samples, parallel=True)
    duration = time.time() - start_time
    
    print(f"Duration: {duration:.2f}s")
    print(f"Processed: {stats['files_processed']}, Skipped: {stats['files_skipped']}")
    
    assert stats['files_processed'] > 0
    assert stats['files_skipped'] == 0
    
    # 2. Second Indexing (Incremental - Should skip all)
    print("\n[2] Incremental Indexing (Should skip all)...")
    start_time = time.time()
    stats = indexer.index_directory(test_samples, parallel=True)
    duration = time.time() - start_time
    
    print(f"Duration: {duration:.2f}s")
    print(f"Processed: {stats['files_processed']}, Skipped: {stats['files_skipped']}")
    
    assert stats['files_processed'] == 0
    assert stats['files_skipped'] > 0
    
    # 3. Modify one file
    print("\n[3] Modifying one file...")
    target_file = Path(test_samples) / "security_manager.py"
    original_mtime = target_file.stat().st_mtime
    
    # Touch the file to update mtime
    os.utime(target_file, (time.time(), time.time()))
    
    start_time = time.time()
    stats = indexer.index_directory(test_samples, parallel=True)
    duration = time.time() - start_time
    
    print(f"Duration: {duration:.2f}s")
    print(f"Processed: {stats['files_processed']}, Skipped: {stats['files_skipped']}")
    
    assert stats['files_processed'] == 1
    
    print("\n=== Test Passed! ===")

if __name__ == "__main__":
    test_performance()
