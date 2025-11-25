#!/usr/bin/env python3
"""
Generic Tree-sitter Chunker
Allows adding support for new languages by simply providing a query
"""

from typing import List, Optional, Dict, Any
from tree_sitter import Language, Parser, Node, QueryCursor

from .base_chunker import BaseChunker, CodeChunk
from utils.logger import get_logger

class GenericTreeSitterChunker(BaseChunker):
    """
    A generic chunker that uses Tree-sitter queries to extract code blocks.
    Avoids writing a separate class for every language.
    Uses tree-sitter-language-pack for easy access to 165+ languages.
    """
    
    def __init__(self, language_name: str, query_scm: str):
        """
        Args:
            language_name: Name of the language (e.g., 'java', 'python')
            query_scm: S-expression query string for tree-sitter
        """
        super().__init__(language_name)
        self.logger = get_logger()
        self.query_scm = query_scm
        
        try:
            # Use tree-sitter-language-pack for simplified language loading
            from tree_sitter_language_pack import get_language, get_parser
            import tree_sitter
            
            self.ts_language = get_language(language_name)
            self.parser = get_parser(language_name)
            
            # Handle API changes in tree-sitter
            try:
                self.query = tree_sitter.Query(self.ts_language, query_scm)
            except AttributeError:
                # Fallback for older versions
                self.query = self.ts_language.query(query_scm)
            
        except ImportError as e:
            self.logger.error(f"Could not import tree-sitter-language-pack. Install it with: pip install tree-sitter-language-pack")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize {language_name} parser: {e}")
            raise

    def extract_chunks(self, code: str, filepath: str) -> List[CodeChunk]:
        """
        Extract chunks using tree-sitter query
        """
        if not code.strip():
            return []
            
        try:
            import tree_sitter
            tree = self.parser.parse(bytes(code, "utf8"))
            
            # Handle API changes in tree-sitter QueryCursor
            try:
                # New API: QueryCursor takes query in constructor
                cursor = tree_sitter.QueryCursor(self.query)
                captures = cursor.captures(tree.root_node)
            except TypeError:
                # Old API: QueryCursor() is empty, pass query to captures
                cursor = tree_sitter.QueryCursor()
                captures = cursor.captures(self.query, tree.root_node)
            
            chunks = []
            
            # Handle dictionary return type (new API) or list (old API)
            if isinstance(captures, dict):
                for tag, nodes in captures.items():
                    if not isinstance(nodes, list):
                        nodes = [nodes]
                    for node in nodes:
                        self._process_capture(node, tag, code, filepath, chunks)
            else:
                # Old API: list of tuples or objects
                for capture in captures:
                    if isinstance(capture, tuple):
                        node, tag = capture
                    else:
                        node = capture.node
                        tag = capture.name
                    self._process_capture(node, tag, code, filepath, chunks)
                
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error chunking {self.language}: {e}")
            return []

    def _process_capture(self, node, tag: str, code: str, filepath: str, chunks: List[CodeChunk]):
        """Process a single capture and add to chunks list"""
        # Extract text
        start_byte = node.start_byte
        end_byte = node.end_byte
        text = code.encode('utf8')[start_byte:end_byte].decode('utf8')
        
        # Map tag to chunk type
        chunk_type = self._map_tag_to_type(tag)
        
        # Extract name if possible (simple heuristic)
        name = "anonymous"
        # Try to find a name child
        name_node = node.child_by_field_name("name")
        if name_node:
            name = code.encode('utf8')[name_node.start_byte:name_node.end_byte].decode('utf8')
        
        chunks.append(CodeChunk(
            type=chunk_type,
            name=name,
            content=text,
            filepath=filepath,
            language=self.language,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1
        ))
            


    def _map_tag_to_type(self, tag: str) -> str:
        """Map tree-sitter capture tag to chunk type"""
        # Remove @ prefix if present
        if tag.startswith('@'):
            return tag[1:]
        return tag
