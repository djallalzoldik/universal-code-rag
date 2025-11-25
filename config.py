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
            # C/C++ family
            'cpp': """(class_specifier) @class (function_definition) @function (namespace_definition) @namespace""",
            'c': """(function_definition) @function (struct_specifier) @struct""",
            
            # JVM/Object-Oriented
            'java': """(class_declaration) @class (interface_declaration) @interface (enum_declaration) @enum (method_declaration) @method""",
            'kotlin': """(class_declaration) @class (function_declaration) @function""",
            'scala': """(class_definition) @class (function_definition) @function (object_definition) @object""",
            'groovy': """(class_declaration) @class (method_declaration) @method""",
            'clojure': """(list_lit) @list (defn) @function""",
            
            # Systems Programming
            'go': """(function_declaration) @function (method_declaration) @method (type_declaration) @struct""",
            'rust': """(function_item) @function (impl_item) @impl (struct_item) @struct (enum_item) @enum (trait_item) @trait""",
            'zig': """(FnProto) @function (VarDecl) @variable""",
            'nim': """(proc_declaration) @function (type_section) @type""",
            'd': """(class_declaration) @class (function_declaration) @function""",
            'v': """(function_declaration) @function (struct_declaration) @struct""",
            'odin': """(procedure_declaration) @function (struct_declaration) @struct""",
            'cuda': """(function_definition) @function (kernel_call) @kernel""",
            'fortran': """(subroutine) @subroutine (function) @function (module) @module""",
            'asm': """(instruction) @instruction (label) @label""",
            'carbon': """(function_declaration) @function (class_declaration) @class""",
            
            # .NET
            'csharp': """(class_declaration) @class (interface_declaration) @interface (enum_declaration) @enum (method_declaration) @method (namespace_declaration) @namespace""",
            'fsharp': """(value_declaration) @function (type_definition) @type (module_defn) @module""",
            
            # Dynamic/Scripting
            'python': """(class_definition) @class (function_definition) @function""",
            'ruby': """(class) @class (module) @module (method) @method""",
            'php': """(class_declaration) @class (function_definition) @function (method_declaration) @method (trait_declaration) @trait""",
            'lua': """(function_definition) @function (assignment_statement) @assignment""",
            'perl': """(subroutine_declaration_statement) @function (package_statement) @package""",
            'elixir': """(call) @function (defmodule) @module""",
            'erlang': """(function_clause) @function (module_attribute) @module""",
            'dart': """(class_definition) @class (function_signature) @function""",
            'actionscript': """(class_definition) @class (function_definition) @function""",
            
            # Shell/Scripting
            'bash': """(function_definition) @function (command) @command""",
            'fish': """(function_definition) @function (command) @command""",
            'powershell': """(function_statement) @function (command_expression) @command""",
            'tcl': """(proc) @function (command) @command""",
            
            # Functional Languages
            'haskell': """(function) @function (type_signature) @signature""",
            'ocaml': """(value_definition) @function (type_definition) @type""",
            'swift': """(class_declaration) @class (function_declaration) @function (protocol_declaration) @protocol""",
            'elm': """(value_declaration) @function (type_declaration) @type""",
            'purescript': """(value_declaration) @function (type_declaration) @type""",
            'racket': """(definition) @function (struct_definition) @struct""",
            'scheme': """(definition) @function (lambda) @lambda""",
            'commonlisp': """(defun) @function (defclass) @class""",
            'reasonml': """(value_declaration) @function (type_declaration) @type""",
            'agda': """(function_definition) @function (data_definition) @data""",
            
            # Web/JS Ecosystem
            'javascript': """(class_declaration) @class (function_declaration) @function (method_definition) @method""",
            'typescript': """(class_declaration) @class (interface_declaration) @interface (function_declaration) @function (method_definition) @method""",
            'tsx': """(class_declaration) @class (function_declaration) @function (jsx_element) @component""",
            'html': """(script_element) @script (style_element) @style (element) @element""",
            'css': """(rule_set) @rule (declaration) @declaration""",
            'vue': """(script_element) @script (template_element) @template (style_element) @style""",
            'svelte': """(script_element) @script (style_element) @style (element) @element""",
            'astro': """(component) @component (frontmatter) @frontmatter""",
            
            # Data Formats
            'json': """(pair) @pair (object) @object (array) @array""",
            'yaml': """(block_mapping_pair) @pair (block_sequence) @sequence""",
            'toml': """(table) @table (pair) @pair""",
            'xml': """(element) @element (attribute) @attribute""",
            'csv': """(row) @row (field) @field""",
            'ini': """(section) @section (property) @property""",
            'properties': """(property) @property (comment) @comment""",
            
            # Query/API Languages
            'sql': """(select_statement) @select (create_statement) @create (function_definition) @function""",
            'graphql': """(operation_definition) @operation (field) @field (fragment_definition) @fragment""",
            
            # Protocol/IDL
            'protobuf': """(message) @message (service) @service (rpc) @rpc""",
            'thrift': """(struct) @struct (service) @service (function) @function""",
            'capnp': """(struct_def) @struct (interface_def) @interface""",
            
            # Build/Config/Infrastructure
            'dockerfile': """(from_instruction) @from (run_instruction) @run""",
            'terraform': """(block) @resource (attribute) @attribute""",
            'hcl': """(block) @block (attribute) @attribute""",
            'cmake': """(function_call) @function (macro_definition) @macro""",
            'make': """(rule) @rule (variable_assignment) @variable""",
            'ninja': """(rule) @rule (build) @build""",
            'bazel': """(call) @rule (assignment) @variable""",
            'bitbake': """(function_definition) @function (assignment) @variable""",
            
            # Documentation
            'markdown': """(atx_heading) @heading (fenced_code_block) @code (link_definition) @link""",
            'rst': """(section) @section (directive) @directive""",
            'latex': """(generic_command) @command (generic_environment) @environment""",
            'org': """(headline) @heading (block) @block""",
            'bibtex': """(entry) @entry (field) @field""",
            'pod': """(command) @command (paragraph) @paragraph""",
            
            # Scientific/Data
            'r': """(function_definition) @function (binary_operator) @operator""",
            'julia': """(function_definition) @function (struct_definition) @struct""",
            'matlab': """(function_definition) @function (assignment) @assignment""",
            'scilab': """(function_definition) @function (assignment) @assignment""",
            
            # Hardware Description
            'verilog': """(module_declaration) @module (function_declaration) @function""",
            'vhdl': """(entity_declaration) @entity (architecture_body) @architecture""",
            'systemverilog': """(module_declaration) @module (class_declaration) @class""",
            
            # Blockchain/Smart Contracts
            'solidity': """(contract_declaration) @contract (function_definition) @function""",
            'cairo': """ (function_definition) @function (struct_definition) @struct""",
            'clarity': """(define_function) @function (define_public) @public""",
            
            # Mobile/Embedded
            'apex': """(class_declaration) @class (method_declaration) @method""",
            'arduino': """(function_definition) @function (compound_statement) @block""",
            
            # Accounting/Finance
            'beancount': """(transaction) @transaction (account) @account""",
            'ledger': """(transaction) @transaction (posting) @posting""",
            
            # Other Domain-Specific
            'ada': """(subprogram_declaration) @function (package_declaration) @package""",
            'bicep': """(resource_declaration) @resource (output_declaration) @output""",
            'chatito': """(entity_definition) @entity (intent_definition) @intent""",
            'devicetree': """(node) @node (property) @property""",
            'dot': """(graph) @graph (node_stmt) @node (edge_stmt) @edge""",
            'git_config': """(section) @section (variable) @variable""",
            'git_rebase': """(command) @command (label) @label""",
            'gitattributes': """(pattern) @pattern (attribute) @attribute""",
            'gitignore': """(pattern) @pattern (comment) @comment""",
            'gpg': """(command) @command (argument) @argument""",
            'http': """(request) @request (header) @header""",
            'ini': """(section) @section (property) @property""",
            'just': """(recipe) @recipe (dependency) @dependency""",
            'kdl': """(node) @node (property) @property""",
            'meson': """(function_call) @function (assignment) @variable""",
            'nix': """(function) @function (binding) @binding""",
            'passwd': """(entry) @entry (field) @field""",
            'smithy': """(shape) @shape (trait) @trait""",
            'starlark': """(function_definition) @function (assignment) @assignment""",
            'textproto': """(message) @message (field) @field""",
            'todotxt': """(task) @task (priority) @priority""",
            'tsv': """(row) @row (field) @field""",
            'udev': """(rule) @rule (assignment) @assignment""",
            'urll': """(url) @url (query) @query""",
            'requirements': """(requirement) @package (specifier) @version""",
        }
        
        # File type configurations
        self.file_types = {
            'cpp': FileTypeConfig(
                extensions=['.cc', '.cpp', '.h', '.hpp', '.c', '.cxx', '.m', '.mm'],
                language='cpp',
                parser_type='treesitter',
                description='C/C++/Obj-C source and header files'
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
            'groovy': FileTypeConfig(['.groovy', '.gradle'], 'groovy', 'treesitter', 'Groovy source', query_scm=self.QUERIES.get('groovy')),
            'clojure': FileTypeConfig(['.clj', '.cljs', '.cljc'], 'clojure', 'treesitter', 'Clojure source', query_scm=self.QUERIES.get('clojure')),
            
            # Systems Programming
            'go': FileTypeConfig(['.go'], 'go', 'treesitter', 'Go source', query_scm=self.QUERIES['go']),
            'rust': FileTypeConfig(['.rs'], 'rust', 'treesitter', 'Rust source', query_scm=self.QUERIES['rust']),
            'zig': FileTypeConfig(['.zig'], 'zig', 'treesitter', 'Zig source', query_scm=self.QUERIES.get('zig')),
            'nim': FileTypeConfig(['.nim'], 'nim', 'treesitter', 'Nim source', query_scm=self.QUERIES.get('nim')),
            'd': FileTypeConfig(['.d'], 'd', 'treesitter', 'D source', query_scm=self.QUERIES.get('d')),
            'v': FileTypeConfig(['.v'], 'v', 'treesitter', 'V source', query_scm=self.QUERIES.get('v')),
            'odin': FileTypeConfig(['.odin'], 'odin', 'treesitter', 'Odin source', query_scm=self.QUERIES.get('odin')),
            'cuda': FileTypeConfig(['.cu', '.cuh'], 'cuda', 'treesitter', 'CUDA source', query_scm=self.QUERIES.get('cuda')),
            'fortran': FileTypeConfig(['.f', '.f90', '.f95'], 'fortran', 'treesitter', 'Fortran source', query_scm=self.QUERIES.get('fortran')),
            'asm': FileTypeConfig(['.asm', '.s'], 'asm', 'treesitter', 'Assembly source', query_scm=self.QUERIES.get('asm')),
            'ada': FileTypeConfig(['.adb', '.ads'], 'ada', 'treesitter', 'Ada source', query_scm=self.QUERIES.get('ada')),
            
            # Dynamic Languages
            'ruby': FileTypeConfig(['.rb'], 'ruby', 'treesitter', 'Ruby source', query_scm=self.QUERIES['ruby']),
            'php': FileTypeConfig(['.php'], 'php', 'treesitter', 'PHP source', query_scm=self.QUERIES['php']),
            'lua': FileTypeConfig(['.lua'], 'lua', 'treesitter', 'Lua source', query_scm=self.QUERIES.get('lua')),
            'perl': FileTypeConfig(['.pl', '.pm'], 'perl', 'treesitter', 'Perl source', query_scm=self.QUERIES.get('perl')),
            'elixir': FileTypeConfig(['.ex', '.exs'], 'elixir', 'treesitter', 'Elixir source', query_scm=self.QUERIES.get('elixir')),
            'erlang': FileTypeConfig(['.erl', '.hrl'], 'erlang', 'treesitter', 'Erlang source', query_scm=self.QUERIES.get('erlang')),
            'dart': FileTypeConfig(['.dart'], 'dart', 'treesitter', 'Dart source', query_scm=self.QUERIES.get('dart')),
            
            # .NET
            'csharp': FileTypeConfig(['.cs'], 'csharp', 'treesitter', 'C# source', query_scm=self.QUERIES['csharp']),
            'fsharp': FileTypeConfig(['.fs', '.fsx', '.fsi'], 'fsharp', 'treesitter', 'F# source', query_scm=self.QUERIES.get('fsharp')),
            
            # Web/JS Languages
            'html': FileTypeConfig(['.html', '.htm'], 'html', 'treesitter', 'HTML files', query_scm=self.QUERIES.get('html')),
            'css': FileTypeConfig(['.css', '.scss', '.sass', '.less'], 'css', 'treesitter', 'CSS files', query_scm=self.QUERIES.get('css')),
            'typescript': FileTypeConfig(['.ts'], 'typescript', 'treesitter', 'TypeScript files', query_scm=self.QUERIES.get('typescript')),
            'tsx': FileTypeConfig(['.tsx'], 'tsx', 'treesitter', 'TSX files', query_scm=self.QUERIES.get('tsx')),
            'vue': FileTypeConfig(['.vue'], 'vue', 'treesitter', 'Vue files', query_scm=self.QUERIES.get('vue')),
            'svelte': FileTypeConfig(['.svelte'], 'svelte', 'treesitter', 'Svelte files', query_scm=self.QUERIES.get('svelte')),
            'astro': FileTypeConfig(['.astro'], 'astro', 'treesitter', 'Astro files', query_scm=self.QUERIES.get('astro')),
            
            # Data/Config
            'json': FileTypeConfig(['.json'], 'json', 'treesitter', 'JSON files', query_scm=self.QUERIES.get('json')),
            'yaml': FileTypeConfig(['.yaml', '.yml'], 'yaml', 'treesitter', 'YAML files', query_scm=self.QUERIES.get('yaml')),
            'toml': FileTypeConfig(['.toml'], 'toml', 'treesitter', 'TOML files', query_scm=self.QUERIES.get('toml')),
            'xml': FileTypeConfig(['.xml'], 'xml', 'treesitter', 'XML files', query_scm=self.QUERIES.get('xml')),
            'graphql': FileTypeConfig(['.graphql', '.gql'], 'graphql', 'treesitter', 'GraphQL files', query_scm=self.QUERIES.get('graphql')),
            'csv': FileTypeConfig(['.csv'], 'csv', 'treesitter', 'CSV files', query_scm=self.QUERIES.get('csv')),
            
            # Query/Protocols
            'sql': FileTypeConfig(['.sql'], 'sql', 'treesitter', 'SQL files', query_scm=self.QUERIES.get('sql')),
            'protobuf': FileTypeConfig(['.proto'], 'protobuf', 'treesitter', 'Protocol Buffer files', query_scm=self.QUERIES.get('protobuf')),
            'thrift': FileTypeConfig(['.thrift'], 'thrift', 'treesitter', 'Thrift files', query_scm=self.QUERIES.get('thrift')),
            'capnp': FileTypeConfig(['.capnp'], 'capnp', 'treesitter', 'Cap n Proto files', query_scm=self.QUERIES.get('capnp')),
            
            # Scripts/Build/Config
            'bash': FileTypeConfig(['.sh', '.bash'], 'bash', 'treesitter', 'Shell scripts', query_scm=self.QUERIES.get('bash')),
            'dockerfile': FileTypeConfig(['Dockerfile', '.dockerfile'], 'dockerfile', 'treesitter', 'Docker files', query_scm=self.QUERIES.get('dockerfile')),
            'terraform': FileTypeConfig(['.tf', '.tfvars'], 'terraform', 'treesitter', 'Terraform files', query_scm=self.QUERIES.get('terraform')),
            'hcl': FileTypeConfig(['.hcl'], 'hcl', 'treesitter', 'HCL files', query_scm=self.QUERIES.get('hcl')),
            'cmake': FileTypeConfig(['CMakeLists.txt', '.cmake'], 'cmake', 'treesitter', 'CMake files', query_scm=self.QUERIES.get('cmake')),
            'make': FileTypeConfig(['Makefile', '.mk'], 'make', 'treesitter', 'Makefiles', query_scm=self.QUERIES.get('make')),
            'ninja': FileTypeConfig(['.ninja'], 'ninja', 'treesitter', 'Ninja build files', query_scm=self.QUERIES.get('ninja')),
            'bazel': FileTypeConfig(['BUILD', 'WORKSPACE', '.bazel', '.bzl'], 'bazel', 'treesitter', 'Bazel build files', query_scm=self.QUERIES.get('bazel')),
            'fish': FileTypeConfig(['.fish'], 'fish', 'treesitter', 'Fish shell scripts', query_scm=self.QUERIES.get('fish')),
            'powershell': FileTypeConfig(['.ps1', '.psm1', '.psd1'], 'powershell', 'treesitter', 'PowerShell scripts', query_scm=self.QUERIES.get('powershell')),
            'tcl': FileTypeConfig(['.tcl'], 'tcl', 'treesitter', 'Tcl scripts', query_scm=self.QUERIES.get('tcl')),
            
            'haskell': FileTypeConfig(['.hs'], 'haskell', 'treesitter', 'Haskell source', query_scm=self.QUERIES.get('haskell')),
            'ocaml': FileTypeConfig(['.ml', '.mli'], 'ocaml', 'treesitter', 'OCaml source', query_scm=self.QUERIES.get('ocaml')),
            'swift': FileTypeConfig(['.swift'], 'swift', 'treesitter', 'Swift source', query_scm=self.QUERIES.get('swift')),
            'elm': FileTypeConfig(['.elm'], 'elm', 'treesitter', 'Elm source', query_scm=self.QUERIES.get('elm')),
            'purescript': FileTypeConfig(['.purs'], 'purescript', 'treesitter', 'PureScript source', query_scm=self.QUERIES.get('purescript')),
            'racket': FileTypeConfig(['.rkt'], 'racket', 'treesitter', 'Racket source', query_scm=self.QUERIES.get('racket')),
            'scheme': FileTypeConfig(['.scm', '.ss'], 'scheme', 'treesitter', 'Scheme source', query_scm=self.QUERIES.get('scheme')),
            'commonlisp': FileTypeConfig(['.lisp', '.cl'], 'commonlisp', 'treesitter', 'Common Lisp source', query_scm=self.QUERIES.get('commonlisp')),
            'reasonml': FileTypeConfig(['.re', '.rei'], 'reasonml', 'treesitter', 'ReasonML source', query_scm=self.QUERIES.get('reasonml')),
            
            'markdown': FileTypeConfig(['.md', '.markdown'], 'markdown', 'treesitter', 'Markdown files', query_scm=self.QUERIES.get('markdown')),
            'rst': FileTypeConfig(['.rst'], 'rst', 'treesitter', 'reStructuredText files', query_scm=self.QUERIES.get('rst')),
            'latex': FileTypeConfig(['.tex'], 'latex', 'treesitter', 'LaTeX files', query_scm=self.QUERIES.get('latex')),
            'org': FileTypeConfig(['.org'], 'org', 'treesitter', 'Org-mode files', query_scm=self.QUERIES.get('org')),
            
            'r': FileTypeConfig(['.r', '.R'], 'r', 'treesitter', 'R source', query_scm=self.QUERIES.get('r')),
            'julia': FileTypeConfig(['.jl'], 'julia', 'treesitter', 'Julia source', query_scm=self.QUERIES.get('julia')),
            'matlab': FileTypeConfig(['.m'], 'matlab', 'treesitter', 'MATLAB source', query_scm=self.QUERIES.get('matlab')),
            
            # Hardware Description
            'verilog': FileTypeConfig(['.v', '.vh'], 'verilog', 'treesitter', 'Verilog source', query_scm=self.QUERIES.get('verilog')),
            'vhdl': FileTypeConfig(['.vhd', '.vhdl'], 'vhdl', 'treesitter', 'VHDL source', query_scm=self.QUERIES.get('vhdl')),
            
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
