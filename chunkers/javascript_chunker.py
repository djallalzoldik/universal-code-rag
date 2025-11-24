#!/usr/bin/env python3
"""
JavaScript/TypeScript code chunker using tree-sitter
Supports .js, .ts, .jsx, .tsx files
"""

from typing import List, Optional
from tree_sitter import Language, Parser, Node
import tree_sitter_javascript

from .base_chunker import BaseChunker, CodeChunk


class JavaScriptChunker(BaseChunker):
    """Extracts functions, classes, and variables from JavaScript/TypeScript code"""
    
    def __init__(self):
        super().__init__('javascript')
        JS_LANGUAGE = Language(tree_sitter_javascript.language())
        self.parser = Parser(JS_LANGUAGE)
    
    def extract_chunks(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract all JavaScript code elements"""
        tree = self.parser.parse(bytes(code, "utf8"))
        chunks = []
        
        def traverse(node: Node, parent_class: str = ''):
            # Extract function declarations
            if node.type == "function_declaration":
                chunk = self._extract_function(node, code, filepath, parent_class)
                if chunk and self._should_include_chunk(chunk):
                    chunks.append(chunk)
            
            # Extract arrow functions assigned to variables
            elif node.type == "lexical_declaration" or node.type == "variable_declaration":
                func_chunks = self._extract_arrow_functions(node, code, filepath)
                chunks.extend([c for c in func_chunks if self._should_include_chunk(c)])
            
            # Extract classes
            elif node.type == "class_declaration":
                chunk = self._extract_class(node, code, filepath)
                if chunk and self._should_include_chunk(chunk):
                    chunks.append(chunk)
                
                # Extract methods
                class_name = self._extract_class_name(node, code)
                body = node.child_by_field_name("body")
                if body:
                    for child in body.children:
                        if child.type == "method_definition":
                            method_chunk = self._extract_method(child, code, filepath, class_name)
                            if method_chunk and self._should_include_chunk(method_chunk):
                                chunks.append(method_chunk)
            
            # Continue traversing
            for child in node.children:
                traverse(child, parent_class)
        
        traverse(tree.root_node)
        return chunks
    
    def _extract_function(self, node: Node, code: str, filepath: str, parent_class: str = '') -> Optional[CodeChunk]:
        """Extract function declaration"""
        func_text = self._extract_text(code, node.start_byte, node.end_byte)
        
        # Get function name
        name_node = node.child_by_field_name("name")
        func_name = self._extract_text(code, name_node.start_byte, name_node.end_byte) if name_node else "anonymous"
        
        # Get parameters
        params_node = node.child_by_field_name("parameters")
        params = self._extract_text(code, params_node.start_byte, params_node.end_byte) if params_node else "()"
        
        signature = f"function {func_name}{params}"
        
        return CodeChunk(
            type='function',
            name=func_name,
            content=func_text,
            filepath=filepath,
            language=self.language,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            signature=signature,
            parent_class=parent_class
        )
    
    def _extract_arrow_functions(self, node: Node, code: str, filepath: str) -> List[CodeChunk]:
        """Extract arrow functions from variable declarations"""
        chunks = []
        
        for child in node.children:
            if child.type == "variable_declarator":
                name_node = child.child_by_field_name("name")
                value_node = child.child_by_field_name("value")
                
                if value_node and value_node.type == "arrow_function":
                    func_name = self._extract_text(code, name_node.start_byte, name_node.end_byte) if name_node else "anonymous"
                    func_text = self._extract_text(code, child.start_byte, child.end_byte)
                    
                    # Get parameters
                    params_node = value_node.child_by_field_name("parameters")
                    if not params_node:
                        params_node = value_node.child_by_field_name("parameter")
                    params = self._extract_text(code, params_node.start_byte, params_node.end_byte) if params_node else "()"
                    
                    signature = f"const {func_name} = {params} => ..."
                    
                    chunks.append(CodeChunk(
                        type='function',
                        name=func_name,
                        content=func_text,
                        filepath=filepath,
                        language=self.language,
                        line_start=child.start_point[0] + 1,
                        line_end=child.end_point[0] + 1,
                        signature=signature
                    ))
        
        return chunks
    
    def _extract_class(self, node: Node, code: str, filepath: str) -> Optional[CodeChunk]:
        """Extract class declaration"""
        class_text = self._extract_text(code, node.start_byte, node.end_byte)
        class_name = self._extract_class_name(node, code)
        
        # Extract base class (extends)
        heritage = node.child_by_field_name("heritage")
        base_class = None
        if heritage:
            for child in heritage.children:
                if child.type == "identifier":
                    base_class = self._extract_text(code, child.start_byte, child.end_byte)
                    break
        
        # Count methods
        method_count = 0
        body = node.child_by_field_name("body")
        if body:
            for child in body.children:
                if child.type == "method_definition":
                    method_count += 1
        
        signature = f"class {class_name}"
        if base_class:
            signature += f" extends {base_class}"
        
        metadata = {
            'base_class': base_class,
            'method_count': method_count
        }
        
        return CodeChunk(
            type='class',
            name=class_name,
            content=class_text,
            filepath=filepath,
            language=self.language,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            signature=signature,
            metadata=metadata
        )
    
    def _extract_method(self, node: Node, code: str, filepath: str, parent_class: str) -> Optional[CodeChunk]:
        """Extract class method"""
        method_text = self._extract_text(code, node.start_byte, node.end_byte)
        
        # Get method name
        name_node = node.child_by_field_name("name")
        method_name = self._extract_text(code, name_node.start_byte, name_node.end_byte) if name_node else "anonymous"
        
        # Get parameters
        params_node = node.child_by_field_name("parameters")
        params = self._extract_text(code, params_node.start_byte, params_node.end_byte) if params_node else "()"
        
        # Check if static, async, etc.
        is_static = any(child.type == "static" for child in node.children)
        is_async = any(child.type == "async" for child in node.children)
        
        signature = ""
        if is_static:
            signature += "static "
        if is_async:
            signature += "async "
        signature += f"{method_name}{params}"
        
        return CodeChunk(
            type='method',
            name=method_name,
            content=method_text,
            filepath=filepath,
            language=self.language,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            signature=signature,
            parent_class=parent_class,
            metadata={'static': is_static, 'async': is_async}
        )
    
    def _extract_class_name(self, node: Node, code: str) -> str:
        """Extract class name"""
        name_node = node.child_by_field_name("name")
        if name_node:
            return self._extract_text(code, name_node.start_byte, name_node.end_byte)
        return "anonymous"
