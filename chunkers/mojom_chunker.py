#!/usr/bin/env python3
"""
Mojom/Mojo interface definition chunker using regex patterns
Supports .mojom and .mojo files
"""

import re
from typing import List, Optional
from .base_chunker import BaseChunker, CodeChunk


class MojomChunker(BaseChunker):
    """Extracts interfaces, structs, unions, and enums from Mojom files"""
    
    def __init__(self):
        super().__init__('mojom')
    
    def extract_chunks(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract all Mojom interface elements"""
        chunks = []
        
        # Extract module declaration
        module_chunk = self._extract_module(code, filepath)
        if module_chunk:
            chunks.append(module_chunk)
        
        # Extract interfaces
        chunks.extend(self._extract_interfaces(code, filepath))
        
        # Extract structs
        chunks.extend(self._extract_structs(code, filepath))
        
        # Extract unions
        chunks.extend(self._extract_unions(code, filepath))
        
        # Extract enums
        chunks.extend(self._extract_enums(code, filepath))
        
        # Extract constants
        chunks.extend(self._extract_constants(code, filepath))
        
        return [c for c in chunks if self._should_include_chunk(c)]
    
    def _extract_module(self, code: str, filepath: str) -> Optional[CodeChunk]:
        """Extract module declaration"""
        pattern = r'module\s+([\w.]+)\s*;'
        match = re.search(pattern, code)
        if match:
            module_name = match.group(1)
            return CodeChunk(
                type='module',
                name=module_name,
                content=match.group(0),
                filepath=filepath,
                language=self.language,
                line_start=self._get_line_number(code, match.start()),
                line_end=self._get_line_number(code, match.end())
            )
        return None
    
    def _extract_interfaces(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract interface definitions"""
        chunks = []
        
        # Pattern: interface Name { ... };
        pattern = r'interface\s+(\w+)\s*\{([^}]*)\}\s*;'
        
        for match in re.finditer(pattern, code, re.DOTALL):
            interface_name = match.group(1)
            interface_body = match.group(2)
            full_text = match.group(0)
            
            # Extract methods from the interface
            methods = self._extract_interface_methods(interface_body)
            
            chunks.append(CodeChunk(
                type='interface',
                name=interface_name,
                content=full_text,
                filepath=filepath,
                language=self.language,
                line_start=self._get_line_number(code, match.start()),
                line_end=self._get_line_number(code, match.end()),
                signature=f"interface {interface_name}",
                metadata={'methods': methods}
            ))
        
        return chunks
    
    def _extract_interface_methods(self, interface_body: str) -> List[str]:
        """Extract method signatures from interface body"""
        methods = []
        # Pattern: MethodName(params) => (response);
        pattern = r'(\w+)\s*\([^)]*\)(?:\s*=>\s*\([^)]*\))?\s*;'
        
        for match in re.finditer(pattern, interface_body):
            methods.append(match.group(0).strip())
        
        return methods
    
    def _extract_structs(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract struct definitions"""
        chunks = []
        
        # Pattern: struct Name { ... };
        pattern = r'struct\s+(\w+)\s*\{([^}]*)\}\s*;'
        
        for match in re.finditer(pattern, code, re.DOTALL):
            struct_name = match.group(1)
            full_text = match.group(0)
            
            chunks.append(CodeChunk(
                type='struct',
                name=struct_name,
                content=full_text,
                filepath=filepath,
                language=self.language,
                line_start=self._get_line_number(code, match.start()),
                line_end=self._get_line_number(code, match.end()),
                signature=f"struct {struct_name}"
            ))
        
        return chunks
    
    def _extract_unions(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract union definitions"""
        chunks = []
        
        # Pattern: union Name { ... };
        pattern = r'union\s+(\w+)\s*\{([^}]*)\}\s*;'
        
        for match in re.finditer(pattern, code, re.DOTALL):
            union_name = match.group(1)
            full_text = match.group(0)
            
            chunks.append(CodeChunk(
                type='union',
                name=union_name,
                content=full_text,
                filepath=filepath,
                language=self.language,
                line_start=self._get_line_number(code, match.start()),
                line_end=self._get_line_number(code, match.end()),
                signature=f"union {union_name}"
            ))
        
        return chunks
    
    def _extract_enums(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract enum definitions"""
        chunks = []
        
        # Pattern: enum Name { ... };
        pattern = r'enum\s+(\w+)\s*\{([^}]*)\}\s*;'
        
        for match in re.finditer(pattern, code, re.DOTALL):
            enum_name = match.group(1)
            full_text = match.group(0)
            
            chunks.append(CodeChunk(
                type='enum',
                name=enum_name,
                content=full_text,
                filepath=filepath,
                language=self.language,
                line_start=self._get_line_number(code, match.start()),
                line_end=self._get_line_number(code, match.end()),
                signature=f"enum {enum_name}"
            ))
        
        return chunks
    
    def _extract_constants(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract constant definitions"""
        chunks = []
        
        # Pattern: const type NAME = value;
        pattern = r'const\s+(\w+)\s+(\w+)\s*=\s*([^;]+);'
        
        for match in re.finditer(pattern, code):
            const_name = match.group(2)
            full_text = match.group(0)
            
            chunks.append(CodeChunk(
                type='constant',
                name=const_name,
                content=full_text,
                filepath=filepath,
                language=self.language,
                line_start=self._get_line_number(code, match.start()),
                line_end=self._get_line_number(code, match.end())
            ))
        
        return chunks
