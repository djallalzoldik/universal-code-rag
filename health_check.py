#!/usr/bin/env python3
"""
Health check script for Docker container
Verifies critical files and module imports
"""
import sys
from pathlib import Path

def main():
    try:
        # Check if critical files exist
        required_files = ['cli.py', 'rag.py', 'indexer.py', 'config.py']
        for file in required_files:
            if not Path(file).exists():
                print(f"✗ Missing required file: {file}")
                sys.exit(1)
        
        # Check if we can import core modules
        try:
            from rag import ChromeRAGSystem
            from indexer import ChromeIndexer
            from config import CONFIG
        except ImportError as e:
            print(f"✗ Module import failed: {e}")
            sys.exit(1)
        
        # Check if config is valid
        if not hasattr(CONFIG, 'db_path'):
            print("✗ Invalid configuration")
            sys.exit(1)
        
        print("✓ Health check passed - all systems operational")
        sys.exit(0)
        
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
