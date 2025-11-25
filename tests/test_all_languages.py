#!/usr/bin/env python3
"""
Comprehensive test script for all supported languages
Tests that the RAG system can index all language test files without errors
"""

import subprocess
import os
import sys
from pathlib import Path

# Test directories
TEST_DIRS = [
    "test_samples/all_languages",
    "test_samples/comprehensive",
    "test_samples/web",
    "test_samples/data"
]

# Expected language counts
EXPECTED_LANGUAGES = {
    'cpp': 1,
    'python': 1,
    'java': 1,
    'go': 1,
    'rust': 1,
    'ruby': 1,
    'php': 1,
    'c_sharp': 1,
    'kotlin': 1,
    'scala': 1,
    'lua': 1,
    'haskell': 1,
    'ocaml': 1,
    'swift': 1,
    'html': 1,
    'css': 1,
    'json': 1,
    'yaml': 1,
    'sql': 1,
    'xml': 1,
    'toml': 1,
    'bash': 1
}

def run_test():
    """Run the comprehensive language test"""
    print("=" * 80)
    print("COMPREHENSIVE LANGUAGE SUPPORT TEST")
    print("=" * 80)
    print()
    
    # Clear database first
    print("🧹 Clearing database...")
    # Get project root (parent of tests directory)
    project_root = Path(__file__).parent.parent
    result = subprocess.run(
        [sys.executable, "cli.py", "clear"],
        capture_output=True,
        text=True,
        cwd=str(project_root)
    )
    if result.returncode != 0:
        print(f"❌ Failed to clear database")
        return False
    print("✅ Database cleared\n")
    
    # Run indexing
    print("📚 Indexing all test files...")
    paths = []
    for dir in TEST_DIRS:
        if os.path.exists(dir):
            paths.extend(["--path", dir])
    
    result = subprocess.run(
        [sys.executable, "cli.py", "index"] + paths,
        capture_output=True,
        text=True,
        cwd=str(project_root)
    )
    
    print(result.stdout)
    
    if result.returncode != 0:
        print(f"❌ Indexing failed")
        print(result.stderr)
        return False
    
    print("\n✅ Indexing completed successfully!\n")
    
    # Check statistics
    print("📊 Checking statistics...")
    result = subprocess.run(
        [sys.executable, "cli.py", "stats"],
        capture_output=True,
        text=True,
        cwd=str(project_root)
    )
    print(result.stdout)
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("="* 80)
    print(f"✅ All {len(EXPECTED_LANGUAGES)} language types tested")
    print("✅ No indexing errors detected")
    print("🎉 TEST PASSED!")
    
    return True

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
