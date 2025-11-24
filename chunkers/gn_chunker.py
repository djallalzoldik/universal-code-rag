#!/usr/bin/env python3
"""
GN build system chunker using regex patterns
Supports .gn and .gni files
"""

import re
from typing import List, Optional
from .base_chunker import BaseChunker, CodeChunk


class GnChunker(BaseChunker):
    """Extracts build targets, templates, and variables from GN files"""
    
    def __init__(self):
        super().__init__('gn')
    
    def extract_chunks(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract all GN build elements"""
        chunks = []
        
        # Extract build targets
        chunks.extend(self._extract_targets(code, filepath))
        
        # Extract templates
        chunks.extend(self._extract_templates(code, filepath))
        
        # Extract variable assignments (only top-level ones)
        chunks.extend(self._extract_variables(code, filepath))
        
        return [c for c in chunks if self._should_include_chunk(c)]
    
    def _extract_targets(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract build targets (executable, shared_library, static_library, etc.)"""
        chunks = []
        
        # Common GN target types
        target_types = [
            'executable', 'shared_library', 'static_library', 'source_set',
            'component', 'action', 'action_foreach', 'group', 'copy',
            'bundle_data', 'create_bundle', 'test'
        ]
        
        for target_type in target_types:
            # Pattern: target_type("name") { ... }
            pattern = rf'{target_type}\s*\(\s*"([^"]+)"\s*\)\s*\{{([^}}]*(?:\{{[^}}]*\}}[^}}]*)*)\}}'
            
            for match in re.finditer(pattern, code, re.DOTALL):
                target_name = match.group(1)
                target_body = match.group(2)
                full_text = match.group(0)
                
                # Extract sources if present
                sources = self._extract_sources_from_target(target_body)
                
                # Extract deps if present
                deps = self._extract_deps_from_target(target_body)
                
                chunks.append(CodeChunk(
                    type='target',
                    name=f"{target_type}:{target_name}",
                    content=full_text,
                    filepath=filepath,
                    language=self.language,
                    line_start=self._get_line_number(code, match.start()),
                    line_end=self._get_line_number(code, match.end()),
                    signature=f'{target_type}("{target_name}")',
                    metadata={
                        'target_type': target_type,
                        'sources_count': len(sources),
                        'deps_count': len(deps)
                    }
                ))
        
        return chunks
    
    def _extract_sources_from_target(self, target_body: str) -> List[str]:
        """Extract source file list from target body"""
        sources = []
        # Pattern: sources = [ ... ]
        pattern = r'sources\s*=\s*\[\s*([^\]]*)\s*\]'
        match = re.search(pattern, target_body, re.DOTALL)
        if match:
            sources_text = match.group(1)
            # Extract quoted strings
            file_pattern = r'"([^"]+)"'
            sources = re.findall(file_pattern, sources_text)
        return sources
    
    def _extract_deps_from_target(self, target_body: str) -> List[str]:
        """Extract dependency list from target body"""
        deps = []
        # Pattern: deps = [ ... ] or public_deps = [ ... ]
        for dep_type in ['deps', 'public_deps']:
            pattern = rf'{dep_type}\s*=\s*\[\s*([^\]]*)\s*\]'
            match = re.search(pattern, target_body, re.DOTALL)
            if match:
                deps_text = match.group(1)
                # Extract quoted strings
                dep_pattern = r'"([^"]+)"'
                deps.extend(re.findall(dep_pattern, deps_text))
        return deps
    
    def _extract_templates(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract template definitions"""
        chunks = []
        
        # Pattern: template("name") { ... }
        pattern = r'template\s*\(\s*"([^"]+)"\s*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
        
        for match in re.finditer(pattern, code, re.DOTALL):
            template_name = match.group(1)
            full_text = match.group(0)
            
            chunks.append(CodeChunk(
                type='template',
                name=template_name,
                content=full_text,
                filepath=filepath,
                language=self.language,
                line_start=self._get_line_number(code, match.start()),
                line_end=self._get_line_number(code, match.end()),
                signature=f'template("{template_name}")'
            ))
        
        return chunks
    
    def _extract_variables(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract top-level variable assignments"""
        chunks = []
        
        # Pattern: variable_name = value
        # Only match simple assignments (avoid nested ones)
        pattern = r'^(\w+)\s*=\s*([^=\n]+)$'
        
        for i, line in enumerate(code.split('\n'), 1):
            match = re.match(pattern, line.strip())
            if match:
                var_name = match.group(1)
                var_value = match.group(2).strip()
                
                # Skip if it looks like a comparison
                if not var_value.startswith('='):
                    chunks.append(CodeChunk(
                        type='variable',
                        name=var_name,
                        content=line.strip(),
                        filepath=filepath,
                        language=self.language,
                        line_start=i,
                        line_end=i
                    ))
        
        return chunks
