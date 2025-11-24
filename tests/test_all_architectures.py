#!/usr/bin/env python3
"""
Comprehensive test of adaptive chunking across all architecture types
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from chunkers import AdaptiveChunker, get_architecture, FileArchitecture

# Test files for each architecture type
TEST_FILES = {
    FileArchitecture.HEADING_BASED: "test_samples/adaptive_test/sample.md",
    FileArchitecture.SECTION_BASED: "test_samples/adaptive_test/config.yaml",
    FileArchitecture.ELEMENT_BASED: "test_samples/adaptive_test/page.html",
    FileArchitecture.RULE_BASED: "test_samples/adaptive_test/Makefile",
    FileArchitecture.RECORD_BASED: "test_samples/adaptive_test/data.csv",
    FileArchitecture.QUERY_BASED: "test_samples/adaptive_test/schema.sql",
    FileArchitecture.TEMPLATE_BASED: "test_samples/adaptive_test/template.jinja",
    FileArchitecture.SCHEMA_BASED: "test_samples/adaptive_test/api.proto",
}

# Language mappings
ARCH_TO_LANGUAGE = {
    FileArchitecture.HEADING_BASED: "markdown",
    FileArchitecture.SECTION_BASED: "yaml",
    FileArchitecture.ELEMENT_BASED: "html",
    FileArchitecture.RULE_BASED: "make",
    FileArchitecture.RECORD_BASED: "csv",
    FileArchitecture.QUERY_BASED: "sql",
    FileArchitecture.TEMPLATE_BASED: "jinja",
    FileArchitecture.SCHEMA_BASED: "protobuf",
}

def test_architecture(arch: FileArchitecture, filepath: str, language: str):
    """Test chunking for a specific architecture"""
    print(f"\n{'='*70}")
    print(f"Testing: {arch.value.upper()}")
    print(f"File: {filepath}")
    print(f"Language: {language}")
    print(f"{'='*70}")
    
    # Check if file exists
    if not Path(filepath).exists():
        print(f"❌ File not found: {filepath}")
        return False
    
    # Read file content
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print(f"File size: {len(content)} bytes")
    
    # Create chunker
    try:
        chunker = AdaptiveChunker(language)
        detected_arch = get_architecture(language)
        print(f"Detected architecture: {detected_arch.value}")
        
        # Extract chunks
        chunks = chunker.extract_chunks(content, filepath)
        
        if not chunks:
            print(f"⚠️  No chunks extracted (fallback may have failed)")
            return False
        
        print(f"\n✅ Successfully extracted {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks, 1):
            print(f"\n  Chunk {i}:")
            print(f"    Type: {chunk.type}")
            print(f"    Name: {chunk.name}")
            print(f"    Lines: {chunk.line_start}-{chunk.line_end}")
            print(f"    Size: {len(chunk.content)} bytes")
            # Show first line of content
            first_line = chunk.content.split('\n')[0][:60]
            print(f"    Preview: {first_line}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*70)
    print("COMPREHENSIVE ADAPTIVE CHUNKING TEST")
    print("Testing all 9 architecture types")
    print("="*70)
    
    results = {}
    
    for arch, filepath in TEST_FILES.items():
        language = ARCH_TO_LANGUAGE[arch]
        success = test_architecture(arch, filepath, language)
        results[arch] = success
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for arch, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{arch.value:20s}: {status}")
    
    print(f"\n{passed}/{total} tests passed ({100*passed//total}%)")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
