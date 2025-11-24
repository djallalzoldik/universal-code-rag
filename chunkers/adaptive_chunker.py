#!/usr/bin/env python3
"""
Adaptive Chunker - Intelligent chunker that adapts to file architecture
Chooses the best chunking strategy based on file structure
"""

from typing import List, Optional
from .base_chunker import BaseChunker, CodeChunk
from .tree_sitter_chunker import GenericTreeSitterChunker
from .fallback_chunker import FallbackChunker
from .file_architectures import (
    FileArchitecture,
    get_architecture,
    get_extraction_strategy
)
from utils.logger import get_logger


class AdaptiveChunker(BaseChunker):
    """
    Adaptive chunker that intelligently selects chunking strategy
    based on file architecture (function-based, section-based, etc.)
    """
    
    def __init__(self, language: str, query_scm: Optional[str] = None):
        """
        Args:
            language: Language name
            query_scm: Optional tree-sitter query (if available)
        """
        super().__init__(language)
        self.logger = get_logger()
        self.query_scm = query_scm
        self.architecture = get_architecture(language)
        
        # Try to create tree-sitter chunker if query provided
        self.ts_chunker = None
        if query_scm:
            try:
                self.ts_chunker = GenericTreeSitterChunker(language, query_scm)
            except Exception as e:
                self.logger.warning(f"Could not create tree-sitter chunker for {language}: {e}")
    
    def extract_chunks(self, code: str, filepath: str) -> List[CodeChunk]:
        """
        Extract chunks using architecture-appropriate strategy
        """
        chunks = []
        
        # Strategy 1: Try tree-sitter query first (if available)
        if self.ts_chunker:
            try:
                chunks = self.ts_chunker.extract_chunks(code, filepath)
                if chunks:
                    self.logger.debug(f"{filepath}: Used tree-sitter chunking ({len(chunks)} chunks)")
                    return chunks
            except Exception as e:
                self.logger.warning(f"{filepath}: Tree-sitter failed: {e}")
        
        # Strategy 2: Use architecture-specific fallback
        chunks = self._extract_by_architecture(code, filepath)
        if chunks:
            self.logger.debug(f"{filepath}: Used {self.architecture.value} chunking ({len(chunks)} chunks)")
            return chunks
        
        # Strategy 3: Generic paragraph fallback
        fallback = FallbackChunker(self.language, strategy="paragraph")
        chunks = fallback.extract_chunks(code, filepath)
        self.logger.debug(f"{filepath}: Used fallback chunking ({len(chunks)} chunks)")
        
        return chunks
    
    def _extract_by_architecture(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract using architecture-specific strategy"""
        
        if self.architecture == FileArchitecture.HEADING_BASED:
            # Markdown, RST, LaTeX - extract by headings
            chunker = FallbackChunker(self.language, strategy="heading")
            return chunker.extract_chunks(code, filepath)
        
        elif self.architecture == FileArchitecture.SECTION_BASED:
            # YAML, TOML, INI - extract by sections
            return self._extract_config_sections(code, filepath)
        
        elif self.architecture == FileArchitecture.RECORD_BASED:
            # CSV, JSON arrays - extract records
            return self._extract_records(code, filepath)
        
        else:
            # For other architectures, use paragraph-based as fallback
            chunker = FallbackChunker(self.language, strategy="paragraph")
            return chunker.extract_chunks(code, filepath)
    
    def _extract_config_sections(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract sections from config files (YAML, TOML, INI)"""
        import re
        chunks = []
        lines = code.split('\n')
        
        current_section = []
        current_name = "root"
        section_start = 1
        
        for i, line in enumerate(lines, 1):
            # YAML/TOML section pattern (starts at column 0, ends with :)
            # INI section pattern ([section_name])
            section_match = re.match(r'^(\[.+\]|[a-zA-Z_][\w\.]*:)\s*$', line.strip())
            
            if section_match and not line.startswith(' '):
                # Save previous section
                if current_section:
                    chunk = CodeChunk(
                        type="section",
                        name=current_name,
                        content='\n'.join(current_section),
                        filepath=filepath,
                        language=self.language,
                        line_start=section_start,
                        line_end=i - 1
                    )
                    chunks.append(chunk)
                
                # Start new section
                current_name = section_match.group(1).strip(':[]')
                current_section = [line]
                section_start = i
            else:
                current_section.append(line)
        
        # Add final section
        if current_section:
            chunk = CodeChunk(
                type="section",
                name=current_name,
                content='\n'.join(current_section),
                filepath=filepath,
                language=self.language,
                line_start=section_start,
                line_end=len(lines)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _extract_records(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract records from data files"""
        import json
        
        # Try JSON first
        try:
            data = json.loads(code)
            if isinstance(data, list):
                # JSON array of records
                chunks = []
                for i, record in enumerate(data):
                    chunk = CodeChunk(
                        type="record",
                        name=f"record_{i+1}",
                        content=json.dumps(record, indent=2),
                        filepath=filepath,
                        language=self.language,
                        line_start=i+1,
                        line_end=i+1
                    )
                    chunks.append(chunk)
                return chunks
        except:
            pass
        
        # Fallback to line-based for CSV
        lines = code.split('\n')
        if len(lines) > 1:
            chunks = []
            header = lines[0]
            for i, line in enumerate(lines[1:], 1):
                if line.strip():
                    chunk = CodeChunk(
                        type="record",
                        name=f"row_{i}",
                        content=f"{header}\n{line}",
                        filepath=filepath,
                        language=self.language,
                        line_start=i+1,
                        line_end=i+1
                    )
                    chunks.append(chunk)
            return chunks
        
        return []
