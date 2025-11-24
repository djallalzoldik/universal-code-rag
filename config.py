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
            # Existing languages
            'java': """(class_declaration) @class (interface_declaration) @interface (enum_declaration) @enum (method_declaration) @method""",
            'go': """(function_declaration) @function (method_declaration) @method (type_declaration) @struct""",
            'rust': """(function_item) @function (impl_item) @impl (struct_item) @struct (enum_item) @enum (trait_item) @trait""",
            'ruby': """(class) @class (module) @module (method) @method""",
            'php': """(class_declaration) @class (function_definition) @function (method_declaration) @method (trait_declaration) @trait""",
            'c_sharp': """(class_declaration) @class (interface_declaration) @interface (enum_declaration) @enum (method_declaration) @method (namespace_declaration) @namespace""",
            
            # Web languages
            'html': """(script_element) @script (style_element) @style (element) @element""",
            'css': """(rule_set) @rule (declaration) @declaration""",
            
            # Data languages
            'json': """(pair) @pair (object) @object (array) @array""",
            'yaml': """(block_mapping_pair) @pair (block_sequence) @sequence""",
            'toml': """(table) @table (pair) @pair""",
            'xml': """(element) @element (attribute) @attribute""",
            
            # Query languages
            'sql': """(select_statement) @select (create_statement) @create (function_definition) @function""",
            
            # Config/Scripts
            'bash': """(function_definition) @function (command) @command""",
            'dockerfile': """(from_instruction) @from (run_instruction) @run""",
            
            # JVM
            'kotlin': """(class_declaration) @class (function_declaration) @function""",
            'scala': """(class_definition) @class (function_definition) @function (object_definition) @object""",
            
            # Other popular
            'lua': """(function_definition) @function (assignment_statement) @assignment""",
            'haskell': """(function) @function (type_signature) @signature""",
            'ocaml': """(value_definition) @function (type_definition) @type""",
            'swift': """(class_declaration) @class (function_declaration) @function (protocol_declaration) @protocol"""
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
            
            # JVM Languages
            'java': FileTypeConfig(['.java'], 'java', 'treesitter', 'Java source', query_scm=self.QUERIES['java']),
            'kotlin': FileTypeConfig(['.kt', '.kts'], 'kotlin', 'treesitter', 'Kotlin source', query_scm=self.QUERIES.get('kotlin')),
            'scala': FileTypeConfig(['.scala'], 'scala', 'treesitter', 'Scala source', query_scm=self.QUERIES.get('scala')),
            
            # Systems Programming
            'go': FileTypeConfig(['.go'], 'go', 'treesitter', 'Go source', query_scm=self.QUERIES['go']),
            'rust': FileTypeConfig(['.rs'], 'rust', 'treesitter', 'Rust source', query_scm=self.QUERIES['rust']),
            
            # Dynamic Languages
            'ruby': FileTypeConfig(['.rb'], 'ruby', 'treesitter', 'Ruby source', query_scm=self.QUERIES['ruby']),
            'php': FileTypeConfig(['.php'], 'php', 'treesitter', 'PHP source', query_scm=self.QUERIES['php']),
            'lua': FileTypeConfig(['.lua'], 'lua', 'treesitter', 'Lua source', query_scm=self.QUERIES.get('lua')),
            
            # .NET
            'c_sharp': FileTypeConfig(['.cs'], 'c_sharp', 'treesitter', 'C# source', query_scm=self.QUERIES['c_sharp']),
            
            # Web Languages
            'html': FileTypeConfig(['.html', '.htm'], 'html', 'treesitter', 'HTML files', query_scm=self.QUERIES.get('html')),
            'css': FileTypeConfig(['.css', '.scss', '.sass', '.less'], 'css', 'treesitter', 'CSS files', query_scm=self.QUERIES.get('css')),
            
            # Data/Config
            'json': FileTypeConfig(['.json'], 'json', 'treesitter', 'JSON files', query_scm=self.QUERIES.get('json')),
            'yaml': FileTypeConfig(['.yaml', '.yml'], 'yaml', 'treesitter', 'YAML files', query_scm=self.QUERIES.get('yaml')),
            'toml': FileTypeConfig(['.toml'], 'toml', 'treesitter', 'TOML files', query_scm=self.QUERIES.get('toml')),
            'xml': FileTypeConfig(['.xml'], 'xml', 'treesitter', 'XML files', query_scm=self.QUERIES.get('xml')),
            
            # Query Languages
            'sql': FileTypeConfig(['.sql'], 'sql', 'treesitter', 'SQL files', query_scm=self.QUERIES.get('sql')),
            
            # Scripts/Configs
            'bash': FileTypeConfig(['.sh', '.bash'], 'bash', 'treesitter', 'Shell scripts', query_scm=self.QUERIES.get('bash')),
            'dockerfile': FileTypeConfig(['Dockerfile','.dockerfile'], 'dockerfile', 'treesitter', 'Docker files', query_scm=self.QUERIES.get('dockerfile')),
            
            # Functional
            'haskell': FileTypeConfig(['.hs'], 'haskell', 'treesitter', 'Haskell source', query_scm=self.QUERIES.get('haskell')),
            'ocaml': FileTypeConfig(['.ml', '.mli'], 'ocaml', 'treesitter', 'OCaml source', query_scm=self.QUERIES.get('ocaml')),
            'swift': FileTypeConfig(['.swift'], 'swift', 'treesitter', 'Swift source', query_scm=self.QUERIES.get('swift')),
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
