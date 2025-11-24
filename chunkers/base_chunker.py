#!/usr/bin/env python3
"""
Base chunker class defining the interface for all language-specific chunkers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class CodeChunk:
    """Standardized representation of a code chunk"""
    type: str  # function, class, method, variable, interface, etc.
    name: str
    content: str
    filepath: str
    language: str
    line_start: int
    line_end: int
    signature: Optional[str] = None
    namespace: Optional[str] = None
    parent_class: Optional[str] = None
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage"""
        return {
            'type': self.type,
            'name': self.name,
            'content': self.content,
            'filepath': self.filepath,
            'language': self.language,
            'line_start': self.line_start,
            'line_end': self.line_end,
            'signature': self.signature or '',
            'namespace': self.namespace or '',
            'parent_class': self.parent_class or '',
            'metadata': str(self.metadata) if self.metadata else ''
        }


class BaseChunker(ABC):
    """Abstract base class for all code chunkers"""
    
    def __init__(self, language: str):
        self.language = language
    
    @abstractmethod
    def extract_chunks(self, code: str, filepath: str) -> List[CodeChunk]:
        """
        Extract code chunks from source code
        
        Args:
            code: Source code content
            filepath: Relative path to the file
            
        Returns:
            List of CodeChunk objects
        """
        pass
    
    def _get_line_number(self, code: str, byte_offset: int) -> int:
        """Convert byte offset to line number"""
        return code[:byte_offset].count('\n') + 1
    
    def _extract_text(self, code: str, start_byte: int, end_byte: int) -> str:
        """Extract text from code using byte offsets"""
        return code[start_byte:end_byte]
    
    def _should_include_chunk(self, chunk: CodeChunk, min_size: int = 10, max_size: int = 10000) -> bool:
        """Filter chunks based on size and quality"""
        content_len = len(chunk.content)
        
        # Size filters
        if content_len < min_size or content_len > max_size:
            return False
        
        # Quality filters
        if chunk.name == 'unknown' or chunk.name == 'anonymous':
            return False
            
        return True
