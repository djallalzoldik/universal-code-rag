#!/usr/bin/env python3
"""
Python code chunker using tree-sitter for accurate parsing
Supports .py files
"""

from typing import List, Optional
from tree_sitter import Language, Parser, Node
import tree_sitter_python

from .base_chunker import BaseChunker, CodeChunk


class PythonChunker(BaseChunker):
    """Extracts functions, classes, and variables from Python code"""
    
    def __init__(self):
        super().__init__('python')
        PYTHON_LANGUAGE = Language(tree_sitter_python.language())
        self.parser = Parser(PYTHON_LANGUAGE)
    
    def extract_chunks(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract all Python code elements"""
        tree = self.parser.parse(bytes(code, "utf8"))
        chunks = []
        
        def traverse(node: Node, parent_class: str = ''):
            # Extract functions
            if node.type == "function_definition":
                chunk = self._extract_function(node, code, filepath, parent_class)
                if chunk and self._should_include_chunk(chunk):
                    chunks.append(chunk)
            
            # Extract classes
            elif node.type == "class_definition":
                chunk = self._extract_class(node, code, filepath)
                if chunk and self._should_include_chunk(chunk):
                    chunks.append(chunk)
                
                # Extract methods within the class
                class_name = self._extract_class_name(node, code)
                body = node.child_by_field_name("body")
                if body:
                    for child in body.children:
                        if child.type == "function_definition":
                            method_chunk = self._extract_function(child, code, filepath, class_name)
                            if method_chunk and self._should_include_chunk(method_chunk):
                                chunks.append(method_chunk)
            
            # Continue traversing
            for child in node.children:
                traverse(child, parent_class)
        
        traverse(tree.root_node)
        
        # Extract module-level assignments
        assignment_chunks = self._extract_module_variables(tree.root_node, code, filepath)
        chunks.extend(assignment_chunks)
        
        return chunks
    
    def _extract_function(self, node: Node, code: str, filepath: str, parent_class: str = '') -> Optional[CodeChunk]:
        """Extract function or method definition"""
        func_text = self._extract_text(code, node.start_byte, node.end_byte)
        
        # Get function name
        name_node = node.child_by_field_name("name")
        func_name = self._extract_text(code, name_node.start_byte, name_node.end_byte) if name_node else "unknown"
        
        # Get parameters
        params_node = node.child_by_field_name("parameters")
        params = self._extract_text(code, params_node.start_byte, params_node.end_byte) if params_node else "()"
        
        # Check for decorators
        decorators = []
        for child in node.children:
            if child.type == "decorator":
                decorator_text = self._extract_text(code, child.start_byte, child.end_byte)
                decorators.append(decorator_text)
        
        # Build signature
        signature = f"def {func_name}{params}"
        if decorators:
            signature = '\n'.join(decorators) + '\n' + signature
        
        # Check if async
        is_async = any(child.type == "async" for child in node.children)
        if is_async:
            signature = "async " + signature
        
        return CodeChunk(
            type='method' if parent_class else 'function',
            name=func_name,
            content=func_text,
            filepath=filepath,
            language=self.language,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            signature=signature,
            parent_class=parent_class,
            metadata={'decorators': decorators, 'async': is_async}
        )
    
    def _extract_class(self, node: Node, code: str, filepath: str) -> Optional[CodeChunk]:
        """Extract class definition"""
        class_text = self._extract_text(code, node.start_byte, node.end_byte)
        class_name = self._extract_class_name(node, code)
        
        # Extract base classes
        bases = []
        argument_list = node.child_by_field_name("superclasses")
        if argument_list:
            for child in argument_list.children:
                if child.type == "identifier":
                    base_name = self._extract_text(code, child.start_byte, child.end_byte)
                    bases.append(base_name)
        
        # Extract decorators
        decorators = []
        for child in node.children:
            if child.type == "decorator":
                decorator_text = self._extract_text(code, child.start_byte, child.end_byte)
                decorators.append(decorator_text)
        
        # Count methods
        method_count = 0
        body = node.child_by_field_name("body")
        if body:
            for child in body.children:
                if child.type == "function_definition":
                    method_count += 1
        
        signature = f"class {class_name}"
        if bases:
            signature += f"({', '.join(bases)})"
        
        metadata = {
            'base_classes': bases,
            'decorators': decorators,
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
    
    def _extract_module_variables(self, root_node: Node, code: str, filepath: str) -> List[CodeChunk]:
        """Extract module-level variable assignments"""
        chunks = []
        
        for child in root_node.children:
            if child.type == "expression_statement":
                # Check if it's an assignment
                assignment = child.child(0)
                if assignment and assignment.type == "assignment":
                    left = assignment.child_by_field_name("left")
                    if left and left.type == "identifier":
                        var_name = self._extract_text(code, left.start_byte, left.end_byte)
                        var_text = self._extract_text(code, assignment.start_byte, assignment.end_byte)
                        
                        # Only include constants (uppercase variables)
                        if var_name.isupper() and len(var_text) < 500:
                            chunks.append(CodeChunk(
                                type='constant',
                                name=var_name,
                                content=var_text,
                                filepath=filepath,
                                language=self.language,
                                line_start=assignment.start_point[0] + 1,
                                line_end=assignment.end_point[0] + 1
                            ))
        
        return chunks
    
    def _extract_class_name(self, node: Node, code: str) -> str:
        """Extract class name"""
        name_node = node.child_by_field_name("name")
        if name_node:
            return self._extract_text(code, name_node.start_byte, name_node.end_byte)
        return "anonymous"
