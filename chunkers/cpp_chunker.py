#!/usr/bin/env python3
"""
C++ code chunker using tree-sitter for accurate parsing
Supports .cc, .cpp, .h, .hpp files
"""

from typing import List, Optional
from tree_sitter import Language, Parser, Node
import tree_sitter_cpp

from .base_chunker import BaseChunker, CodeChunk


class CppChunker(BaseChunker):
    """Extracts functions, classes, namespaces, and declarations from C++ code"""
    
    def __init__(self):
        super().__init__('cpp')
        CPP_LANGUAGE = Language(tree_sitter_cpp.language())
        self.parser = Parser(CPP_LANGUAGE)
    
    def extract_chunks(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract all C++ code elements"""
        tree = self.parser.parse(bytes(code, "utf8"))
        chunks = []
        
        # Track current namespace context
        namespace_stack = []
        
        def traverse(node: Node, current_namespace: str = ''):
            nonlocal chunks
            
            # Extract namespaces
            if node.type == "namespace_definition":
                namespace_name = self._extract_namespace_name(node, code)
                new_namespace = f"{current_namespace}::{namespace_name}" if current_namespace else namespace_name
                namespace_stack.append(namespace_name)
                
                # Traverse children with updated namespace
                for child in node.children:
                    traverse(child, new_namespace)
                
                namespace_stack.pop()
                return
            
            # Extract functions
            elif node.type == "function_definition":
                chunk = self._extract_function(node, code, filepath, current_namespace)
                if chunk and self._should_include_chunk(chunk):
                    chunks.append(chunk)
            
            # Extract classes and structs
            elif node.type in ["class_specifier", "struct_specifier"]:
                chunk = self._extract_class(node, code, filepath, current_namespace)
                if chunk and self._should_include_chunk(chunk):
                    chunks.append(chunk)
                    
                # Also extract methods within the class
                class_name = self._extract_class_name(node, code)
                body = node.child_by_field_name("body")
                if body:
                    for child in body.children:
                        if child.type == "function_definition":
                            method_chunk = self._extract_function(
                                child, code, filepath, current_namespace, parent_class=class_name
                            )
                            if method_chunk and self._should_include_chunk(method_chunk):
                                chunks.append(method_chunk)
            
            # Extract enums
            elif node.type == "enum_specifier":
                chunk = self._extract_enum(node, code, filepath, current_namespace)
                if chunk and self._should_include_chunk(chunk):
                    chunks.append(chunk)
            
            # Continue traversing
            for child in node.children:
                if child.type not in ["namespace_definition"]:  # Avoid double-processing namespaces
                    traverse(child, current_namespace)
        
        traverse(tree.root_node)
        
        # Extract preprocessor macros (not in AST, use regex)
        macro_chunks = self._extract_macros(code, filepath)
        chunks.extend(macro_chunks)
        
        return chunks
    
    def _extract_function(self, node: Node, code: str, filepath: str, 
                         namespace: str = '', parent_class: str = '') -> Optional[CodeChunk]:
        """Extract function definition"""
        func_text = self._extract_text(code, node.start_byte, node.end_byte)
        
        # Get function name
        declarator = node.child_by_field_name("declarator")
        func_name = self._extract_function_name(declarator, code)
        
        # Get signature
        signature = self._extract_signature(node, code)
        
        return CodeChunk(
            type='method' if parent_class else 'function',
            name=func_name,
            content=func_text,
            filepath=filepath,
            language=self.language,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            signature=signature,
            namespace=namespace,
            parent_class=parent_class
        )
    
    def _extract_class(self, node: Node, code: str, filepath: str, namespace: str = '') -> Optional[CodeChunk]:
        """Extract class or struct definition"""
        class_text = self._extract_text(code, node.start_byte, node.end_byte)
        class_name = self._extract_class_name(node, code)
        
        # Extract base classes
        bases = []
        for child in node.children:
            if child.type == "base_class_clause":
                base_text = self._extract_text(code, child.start_byte, child.end_byte)
                bases.append(base_text)
        
        # Extract member count
        methods = []
        members = []
        body = node.child_by_field_name("body")
        if body:
            for child in body.children:
                if child.type == "function_definition":
                    method_name = self._extract_function_name(child, code)
                    methods.append(method_name)
                elif child.type == "field_declaration":
                    member_text = self._extract_text(code, child.start_byte, child.end_byte).strip()
                    members.append(member_text)
        
        metadata = {
            'base_classes': bases,
            'methods': methods,
            'members_count': len(members)
        }
        
        return CodeChunk(
            type='class' if node.type == "class_specifier" else 'struct',
            name=class_name,
            content=class_text,
            filepath=filepath,
            language=self.language,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            signature=f"{'class' if node.type == 'class_specifier' else 'struct'} {class_name}",
            namespace=namespace,
            metadata=metadata
        )
    
    def _extract_enum(self, node: Node, code: str, filepath: str, namespace: str = '') -> Optional[CodeChunk]:
        """Extract enum definition"""
        enum_text = self._extract_text(code, node.start_byte, node.end_byte)
        
        name_node = node.child_by_field_name("name")
        enum_name = self._extract_text(code, name_node.start_byte, name_node.end_byte) if name_node else "anonymous_enum"
        
        return CodeChunk(
            type='enum',
            name=enum_name,
            content=enum_text,
            filepath=filepath,
            language=self.language,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            namespace=namespace
        )
    
    def _extract_macros(self, code: str, filepath: str) -> List[CodeChunk]:
        """Extract #define macros using regex"""
        import re
        chunks = []
        
        macro_pattern = r'^#define\s+(\w+)(?:\([^)]*\))?\s+(.*)$'
        for i, line in enumerate(code.split('\n'), 1):
            match = re.match(macro_pattern, line.strip())
            if match:
                macro_name = match.group(1)
                full_line = line.strip()
                
                chunks.append(CodeChunk(
                    type='macro',
                    name=macro_name,
                    content=full_line,
                    filepath=filepath,
                    language=self.language,
                    line_start=i,
                    line_end=i
                ))
        
        return chunks
    
    def _extract_function_name(self, declarator_node: Optional[Node], code: str) -> str:
        """Extract function name from declarator node"""
        if not declarator_node:
            return "unknown"
        
        # Handle different declarator types
        if declarator_node.type == "function_declarator":
            inner = declarator_node.child_by_field_name("declarator")
            if inner:
                if inner.type == "identifier":
                    return self._extract_text(code, inner.start_byte, inner.end_byte)
                elif inner.type == "field_identifier":
                    return self._extract_text(code, inner.start_byte, inner.end_byte)
                elif inner.type == "qualified_identifier":
                    # Get the last part of qualified name
                    name_node = inner.child_by_field_name("name")
                    if name_node:
                        return self._extract_text(code, name_node.start_byte, name_node.end_byte)
                return self._extract_function_name(inner, code)
        elif declarator_node.type == "identifier":
            return self._extract_text(code, declarator_node.start_byte, declarator_node.end_byte)
        
        return self._extract_text(code, declarator_node.start_byte, declarator_node.end_byte)
    
    def _extract_class_name(self, node: Node, code: str) -> str:
        """Extract class name"""
        name_node = node.child_by_field_name("name")
        if name_node:
            return self._extract_text(code, name_node.start_byte, name_node.end_byte)
        return "anonymous"
    
    def _extract_namespace_name(self, node: Node, code: str) -> str:
        """Extract namespace name"""
        name_node = node.child_by_field_name("name")
        if name_node:
            return self._extract_text(code, name_node.start_byte, name_node.end_byte)
        return "anonymous"
    
    def _extract_signature(self, func_node: Node, code: str) -> str:
        """Extract function signature"""
        return_type = func_node.child_by_field_name("type")
        declarator = func_node.child_by_field_name("declarator")
        
        if return_type and declarator:
            ret_text = self._extract_text(code, return_type.start_byte, return_type.end_byte)
            decl_text = self._extract_text(code, declarator.start_byte, declarator.end_byte)
            return f"{ret_text} {decl_text}"
        
        return "unknown signature"
