#!/usr/bin/env python3
"""
Test script for adaptive chunking system
Tests various file types to ensure appropriate chunking strategies are used
"""

import sys
sys.path.insert(0, '.')

from chunkers import AdaptiveChunker, get_architecture

# Test files from different architectures
TEST_CASES = [
    # Markdown (HEADING_BASED)
    ("markdown", """# Introduction

This is the introduction section.

## Setup

Follow these steps to set up the system.

## Configuration

Edit the config file.
"""),
    
    # YAML (SECTION_BASED)
    ("yaml", """database:
  host: localhost
  port: 5432
  username: admin

cache:
  ttl: 3600
  size: 1000

logging:
  level: INFO
  file: app.log
"""),
    
    # Python (FUNCTION_BASED with fallback)
    ("python", """# Simple Python script without functions
# This should fall back to paragraph chunking

import os
import sys

# Global variable
DEBUG = True

# Another paragraph
if __name__ == "__main__":
    print("Hello World")
"""),
]

def test_chunking():
    print("=" * 70)
    print("ADAPTIVE CHUNKING TEST")
    print("=" * 70)
    
    for language, code in TEST_CASES:
        print(f"\n{'='*70}")
        print(f"Testing: {language.upper()}")
        print(f"Architecture: {get_architecture(language).value}")
        print(f"{'='*70}")
        
        try:
            chunker = AdaptiveChunker(language)
            chunks = chunker.extract_chunks(code, f"test.{language}")
            
            print(f"\n✅ Extracted {len(chunks)} chunks:")
            for i, chunk in enumerate(chunks, 1):
                print(f"\n  Chunk {i}:")
                print(f"    Type: {chunk.type}")
                print(f"    Name: {chunk.name}")
                print(f"    Lines: {chunk.line_start}-{chunk.line_end}")
                print(f"    Content (first 50 chars): {chunk.content[:50]}...")
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    test_chunking()
