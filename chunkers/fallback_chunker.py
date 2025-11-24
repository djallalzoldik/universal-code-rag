#!/usr/bin/env python3
"""
Fallback Chunker - Simple paragraph/line-based chunking
Used when tree-sitter queries return no results
"""

from typing import List
from .base_chunker import BaseChunker, CodeChunk
import re


class FallbackChunker(BaseChunker):
    """
    Fallback chunker that uses simple text-based strategies
    when tree-sitter queries return no chunks
    """
    
    def __init__(self, language: str, strategy: str = "paragraph"):
        """
        Args:
            language: Language name for metadata
            strategy: Chunking strategy (paragraph, fixed_size, heading)
        """
        super().__init__(language)
        self.strategy = strategy
    
    def extract_chunks(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract chunks using fallback strategy"""
        
        if self.strategy == "paragraph":
            return self._extract_by_paragraphs(code, filepath)
        elif self.strategy == "fixed_size":
            return self._extract_fixed_size(code, filepath)
        elif self.strategy == "heading":
            return self._extract_by_headings(code, filepath)
        else:
            return self._extract_by_paragraphs(code, filepath)
    
    def _extract_by_paragraphs(self, code: str, filepath: str) -> List[CodeChunk]:
        """Split by blank lines (paragraphs)"""
        chunks = []
        paragraphs = re.split(r'\n\s*\n', code)
        
        current_line = 1
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue
            
            # Count lines in this paragraph
            line_count = para.count('\n') + 1
            
            # Extract a name from first line (truncated)
            first_line = para.split('\n')[0][:50]
            name = f"paragraph_{i+1}"
            
            chunk = CodeChunk(
                type="paragraph",
                name=name,
                content=para,
                filepath=filepath,
                language=self.language,
                line_start=current_line,
                line_end=current_line + line_count - 1
            )
            chunks.append(chunk)
            current_line += line_count + 1  # +1 for blank line
        
        return chunks
    
    def _extract_fixed_size(self, code: str, filepath: str, 
                           chunk_size: int = 50, overlap: int = 10) -> List[CodeChunk]:
        """Split into fixed-size chunks with overlap"""
        chunks = []
        lines = code.split('\n')
        
        i = 0
        chunk_num = 1
        while i < len(lines):
            chunk_lines = lines[i:i + chunk_size]
            content = '\n'.join(chunk_lines)
            
            chunk = CodeChunk(
                type="block",
                name=f"block_{chunk_num}",
                content=content,
                filepath=filepath,
                language=self.language,
                line_start=i + 1,
                line_end=min(i + chunk_size, len(lines))
            )
            chunks.append(chunk)
            
            i += chunk_size - overlap
            chunk_num += 1
        
        return chunks
    
    def _extract_by_headings(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract by markdown-style headings"""
        chunks = []
        lines = code.split('\n')
        
        current_section = []
        current_heading = "Introduction"
        section_start = 1
        
        for i, line in enumerate(lines, 1):
            # Check if line is a heading (starts with #, ##, etc.)
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if heading_match:
                # Save previous section if it exists
                if current_section:
                    chunk = CodeChunk(
                        type="section",
                        name=current_heading,
                        content='\n'.join(current_section),
                        filepath=filepath,
                        language=self.language,
                        line_start=section_start,
                        line_end=i - 1
                    )
                    chunks.append(chunk)
                
                # Start new section
                current_heading = heading_match.group(2).strip()
                current_section = [line]
                section_start = i
            else:
                current_section.append(line)
        
        # Add final section
        if current_section:
            chunk = CodeChunk(
                type="section",
                name=current_heading,
                content='\n'.join(current_section),
                filepath=filepath,
                language=self.language,
                line_start=section_start,
                line_end=len(lines)
            )
            chunks.append(chunk)
        
        return chunks
