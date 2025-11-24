#!/usr/bin/env python3
"""
Generic Tree-sitter Chunker
Allows adding support for new languages by simply providing a query
"""

from typing import List, Optional, Dict
from tree_sitter import Language, Parser, Node
import importlib

from .base_chunker import BaseChunker, CodeChunk
from utils.logger import get_logger

class GenericTreeSitterChunker(BaseChunker):
    """
    A generic chunker that uses Tree-sitter queries to extract code blocks.
    Avoids writing a separate class for every language.
    """
    
    def __init__(self, language_name: str, package_name: str, query_scm: str):
        """
        Args:
            language_name: Name of the language (e.g., 'java')
            package_name: Python package for the language (e.g., 'tree_sitter_java')
            query_scm: S-expression query string for tree-sitter
        """
        super().__init__(language_name)
        self.logger = get_logger()
        self.query_scm = query_scm
        
        try:
            # Dynamically import the language module
            lang_module = importlib.import_module(package_name)
            
            # Find the language function
            if hasattr(lang_module, 'language'):
                lang_func = lang_module.language
            elif hasattr(lang_module, f'language_{language_name}'):
                lang_func = getattr(lang_module, f'language_{language_name}')
            else:
                # Try to find any function starting with language_
                potential_funcs = [n for n in dir(lang_module) if n.startswith('language_')]
                if potential_funcs:
                    lang_func = getattr(lang_module, potential_funcs[0])
                else:
                    raise AttributeError(f"Could not find language function in {package_name}")
            
            self.ts_language = Language(lang_func())
            self.parser = Parser(self.ts_language)
            self.query = self.ts_language.query(query_scm)
        except ImportError:
            self.logger.error(f"Could not import {package_name}. Please install it via pip.")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize {language_name} parser: {e}")
            raise

    def extract_chunks(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract chunks using the provided query"""
        try:
            tree = self.parser.parse(bytes(code, "utf8"))
            chunks = []
            
            # Execute query using matches (correct API for tree-sitter-python)
            matches = self.query.matches(tree.root_node)
            
            # matches is a list of (pattern_index, captures_dict) tuples
            # captures_dict maps capture names to lists of nodes
            for pattern_index, captures_dict in matches:
                for capture_name, nodes in captures_dict.items():
                    for node in nodes:
                        chunk = self._create_chunk_from_capture(node, capture_name, code, filepath)
                        if chunk and self._should_include_chunk(chunk):
                            chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error parsing {filepath}: {e}")
            return []

    def _create_chunk_from_capture(self, node: Node, capture_name: str, code: str, filepath: str) -> Optional[CodeChunk]:
        """Create a CodeChunk from a captured node"""
        
        # Map capture names to chunk types
        # Expected capture names: @function, @class, @method, @interface, etc.
        chunk_type = capture_name
        
        # Extract name
        name = "anonymous"
        
        # Try to find a name child
        name_node = node.child_by_field_name("name")
        if name_node:
            name = self._extract_text(code, name_node.start_byte, name_node.end_byte)
        else:
            # Fallback: look for identifier in children
            for child in node.children:
                if child.type == "identifier" or child.type == "type_identifier":
                    name = self._extract_text(code, child.start_byte, child.end_byte)
                    break
        
        # Extract content
        content = self._extract_text(code, node.start_byte, node.end_byte)
        
        return CodeChunk(
            type=chunk_type,
            name=name,
            content=content,
            filepath=filepath,
            language=self.language,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1
        )
