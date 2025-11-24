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
            'csharp': """(class_declaration) @class (interface_declaration) @interface (enum_declaration) @enum (method_declaration) @method (namespace_declaration) @namespace""",
            
            # Web/JS ecosystem
            'html': """(script_element) @script (style_element) @style (element) @element""",
            'css': """(rule_set) @rule (declaration) @declaration""",
            'typescript': """(class_declaration) @class (interface_declaration) @interface (function_declaration) @function (method_definition) @method""",
            'tsx': """(class_declaration) @class (function_declaration) @function (jsx_element) @component""",
            
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
            'perl': """(subroutine_declaration_statement) @function (package_statement) @package""",
            
            # JVM
            'kotlin': """(class_declaration) @class (function_declaration) @function""",
            'scala': """(class_definition) @class (function_definition) @function (object_definition) @object""",
            
            # Functional/Dynamic
            'lua': """(function_definition) @function (assignment_statement) @assignment""",
            'haskell': """(function) @function (type_signature) @signature""",
            'ocaml': """(value_definition) @function (type_definition) @type""",
            'swift': """(class_declaration) @class (function_declaration) @function (protocol_declaration) @protocol""",
            'elixir': """(call) @function (defmodule) @module""",
            'erlang': """(function_clause) @function (module_attribute) @module""",
            
            # Systems/New languages
            'zig': """(FnProto) @function (VarDecl) @variable""",
            'dart': """(class_definition) @class (function_signature) @function""",
            'nim': """(proc_declaration) @function (type_section) @type""",
            
            # Documentation
            'markdown': """(atx_heading) @heading (fenced_code_block) @code (link_definition) @link""",
            
            # Scientific/Data
            'r': """(function_definition) @function (binary_operator) @operator""",
            'julia': """(function_definition) @function (struct_definition) @struct""",
            
            # Other
            'protobuf': """(message) @message (service) @service (rpc) @rpc""",
            'solidity': """(contract_declaration) @contract (function_definition) @function""",
            'terraform': """(block) @resource (attribute) @attribute"""
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
            'zig': FileTypeConfig(['.zig'], 'zig', 'treesitter', 'Zig source', query_scm=self.QUERIES.get('zig')),
            'nim': FileTypeConfig(['.nim'], 'nim', 'treesitter', 'Nim source', query_scm=self.QUERIES.get('nim')),
            
            # Dynamic Languages
            'ruby': FileTypeConfig(['.rb'], 'ruby', 'treesitter', 'Ruby source', query_scm=self.QUERIES['ruby']),
            'php': FileTypeConfig(['.php'], 'php', 'treesitter', 'PHP source', query_scm=self.QUERIES['php']),
            'lua': FileTypeConfig(['.lua'], 'lua', 'treesitter', 'Lua source', query_scm=self.QUERIES.get('lua')),
            'perl': FileTypeConfig(['.pl', '.pm'], 'perl', 'treesitter', 'Perl source', query_scm=self.QUERIES.get('perl')),
            'elixir': FileTypeConfig(['.ex', '.exs'], 'elixir', 'treesitter', 'Elixir source', query_scm=self.QUERIES.get('elixir')),
            'erlang': FileTypeConfig(['.erl', '.hrl'], 'erlang', 'treesitter', 'Erlang source', query_scm=self.QUERIES.get('erlang')),
            'dart': FileTypeConfig(['.dart'], 'dart', 'treesitter', 'Dart source', query_scm=self.QUERIES.get('dart')),
            
            # .NET (FIXED: c_sharp -> csharp)
            'csharp': FileTypeConfig(['.cs'], 'csharp', 'treesitter', 'C# source', query_scm=self.QUERIES['csharp']),
            
            # Web/JS Languages
            'html': FileTypeConfig(['.html', '.htm'], 'html', 'treesitter', 'HTML files', query_scm=self.QUERIES.get('html')),
            'css': FileTypeConfig(['.css', '.scss', '.sass', '.less'], 'css', 'treesitter', 'CSS files', query_scm=self.QUERIES.get('css')),
            'typescript': FileTypeConfig(['.ts'], 'typescript', 'treesitter', 'TypeScript files', query_scm=self.QUERIES.get('typescript')),
            'tsx': FileTypeConfig(['.tsx'], 'tsx', 'treesitter', 'TSX files', query_scm=self.QUERIES.get('tsx')),
            
            # Data/Config
            'json': FileTypeConfig(['.json'], 'json', 'treesitter', 'JSON files', query_scm=self.QUERIES.get('json')),
            'yaml': FileTypeConfig(['.yaml', '.yml'], 'yaml', 'treesitter', 'YAML files', query_scm=self.QUERIES.get('yaml')),
            'toml': FileTypeConfig(['.toml'], 'toml', 'treesitter', 'TOML files', query_scm=self.QUERIES.get('toml')),
            'xml': FileTypeConfig(['.xml'], 'xml', 'treesitter', 'XML files', query_scm=self.QUERIES.get('xml')),
            
            # Query/Protocols
            'sql': FileTypeConfig(['.sql'], 'sql', 'treesitter', 'SQL files', query_scm=self.QUERIES.get('sql')),
            'protobuf': FileTypeConfig(['.proto'], 'protobuf', 'treesitter', 'Protocol Buffer files', query_scm=self.QUERIES.get('protobuf')),
            
            # Scripts/Configs
            'bash': FileTypeConfig(['.sh', '.bash'], 'bash', 'treesitter', 'Shell scripts', query_scm=self.QUERIES.get('bash')),
            'dockerfile': FileTypeConfig(['Dockerfile','.dockerfile'], 'dockerfile', 'treesitter', 'Docker files', query_scm=self.QUERIES.get('dockerfile')),
            'terraform': FileTypeConfig(['.tf', '.tfvars'], 'terraform', 'treesitter', 'Terraform files', query_scm=self.QUERIES.get('terraform')),
            
            # Functional
            'haskell': FileTypeConfig(['.hs'], 'haskell', 'treesitter', 'Haskell source', query_scm=self.QUERIES.get('haskell')),
            'ocaml': FileTypeConfig(['.ml', '.mli'], 'ocaml', 'treesitter', 'OCaml source', query_scm=self.QUERIES.get('ocaml')),
            'swift': FileTypeConfig(['.swift'], 'swift', 'treesitter', 'Swift source', query_scm=self.QUERIES.get('swift')),
            
            # Documentation
            'markdown': FileTypeConfig(['.md', '.markdown'], 'markdown', 'treesitter', 'Markdown files', query_scm=self.QUERIES.get('markdown')),
            
            # Scientific/Data
            'r': FileTypeConfig(['.r', '.R'], 'r', 'treesitter', 'R source', query_scm=self.QUERIES.get('r')),
            'julia': FileTypeConfig(['.jl'], 'julia', 'treesitter', 'Julia source', query_scm=self.QUERIES.get('julia')),
            
            # Blockchain/Smart Contracts
            'solidity': FileTypeConfig(['.sol'], 'solidity', 'treesitter', 'Solidity files', query_scm=self.QUERIES.get('solidity')),
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
