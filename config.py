#!/usr/bin/env python3
"""
Configuration management for Chrome RAG System
Centralizes all settings for file types, parsers, and processing parameters
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from pathlib import Path


@dataclass
class FileTypeConfig:
    """Configuration for each supported file type"""
    extensions: List[str]
    language: str
    parser_type: str  # 'treesitter' or 'regex'
    description: str = ""
    package_name: Optional[str] = None
    query_scm: Optional[str] = None


class Config:
    """Main configuration for Chrome RAG System"""
    
    def __init__(self):
        # Database settings
        self.db_path = "./chrome_rag_db"
        self.collection_name = "chrome_code"
        self.batch_size = 100
        
        # Logging settings
        self.log_dir = "./logs"
        self.log_level = "INFO"
        
        # Tree-sitter Queries
        self.QUERIES = {
            'java': """
                (class_declaration) @class
                (interface_declaration) @interface
                (enum_declaration) @enum
                (method_declaration) @method
            """,
            'go': """
                (function_declaration) @function
                (method_declaration) @method
                (type_declaration) @struct
            """,
            'rust': """
                (function_item) @function
                (impl_item) @impl
                (struct_item) @struct
                (enum_item) @enum
                (trait_item) @trait
            """,
            'ruby': """
                (class) @class
                (module) @module
                (method) @method
            """,
            'php': """
                (class_declaration) @class
                (function_definition) @function
                (method_declaration) @method
                (trait_declaration) @trait
            """,
            'c_sharp': """
                (class_declaration) @class
                (interface_declaration) @interface
                (enum_declaration) @enum
                (method_declaration) @method
                (namespace_declaration) @namespace
            """
        }
        
        # File type configurations
        self.file_types = {
            'cpp': FileTypeConfig(
                extensions=['.cc', '.cpp', '.h', '.hpp', '.c', '.cxx'],
                language='cpp',
                parser_type='treesitter',
                description='C++ source and header files'
            ),
            'python': FileTypeConfig(
                extensions=['.py'],
                language='python',
                parser_type='treesitter',
                description='Python source files'
            ),
            'javascript': FileTypeConfig(
                extensions=['.js', '.ts', '.jsx', '.tsx'],
                language='javascript',
                parser_type='treesitter',
                description='JavaScript/TypeScript files'
            ),
            'mojom': FileTypeConfig(
                extensions=['.mojom', '.mojo'],
                language='mojom',
                parser_type='regex',
                description='Mojo interface definition files'
            ),
            'gn': FileTypeConfig(
                extensions=['.gn', '.gni'],
                language='gn',
                parser_type='regex',
                description='GN build system files'
            ),
            
            # New Languages
            'java': FileTypeConfig(
                extensions=['.java'], 
                language='java', 
                parser_type='treesitter',
                description='Java source files',
                package_name='tree_sitter_java', 
                query_scm=self.QUERIES['java']
            ),
            'go': FileTypeConfig(
                extensions=['.go'], 
                language='go', 
                parser_type='treesitter',
                description='Go source files',
                package_name='tree_sitter_go', 
                query_scm=self.QUERIES['go']
            ),
            'rust': FileTypeConfig(
                extensions=['.rs'], 
                language='rust', 
                parser_type='treesitter',
                description='Rust source files',
                package_name='tree_sitter_rust', 
                query_scm=self.QUERIES['rust']
            ),
            'ruby': FileTypeConfig(
                extensions=['.rb'], 
                language='ruby', 
                parser_type='treesitter',
                description='Ruby source files',
                package_name='tree_sitter_ruby', 
                query_scm=self.QUERIES['ruby']
            ),
            'php': FileTypeConfig(
                extensions=['.php'], 
                language='php', 
                parser_type='treesitter',
                description='PHP source files',
                package_name='tree_sitter_php', 
                query_scm=self.QUERIES['php']
            ),
            'c_sharp': FileTypeConfig(
                extensions=['.cs'], 
                language='c_sharp', 
                parser_type='treesitter',
                description='C# source files',
                package_name='tree_sitter_c_sharp', 
                query_scm=self.QUERIES['c_sharp']
            ),
        }
        
        # Indexing settings
        self.max_chunk_size = 8000
        self.min_chunk_size = 50
        
        # Directories to exclude
        self.exclude_dirs = {
            'third_party', 'out', 'build', '.git', '.svn', '.hg',
            '__pycache__', 'node_modules', 'venv', 'env',
            'test', 'tests', 'testing'
        }
        
        # Progress tracking
        self.progress_update_interval = 10
    
    def get_all_extensions(self) -> Set[str]:
        """Get all supported file extensions"""
        extensions = set()
        for ft_config in self.file_types.values():
            extensions.update(ft_config.extensions)
        return extensions
    
    def get_language_for_extension(self, extension: str) -> str:
        """Get language name for a file extension"""
        for lang, ft_config in self.file_types.items():
            if extension in ft_config.extensions:
                return lang
        return 'unknown'
    
    def get_parser_type(self, language: str) -> str:
        """Get parser type for a language"""
        if language in self.file_types:
            return self.file_types[language].parser_type
        return 'regex'
    
    def should_exclude_dir(self, dir_name: str) -> bool:
        """Check if directory should be excluded from indexing"""
        return dir_name in self.exclude_dirs


# Global configuration instance
CONFIG = Config()
