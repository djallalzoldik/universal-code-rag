#!/usr/bin/env python3
"""
File Architecture Taxonomy
Categorizes all 200+ languages by their structural patterns
"""

from enum import Enum
from typing import Dict, List, Set

class FileArchitecture(Enum):
    """
    File architecture types based on structural patterns
    Each architecture requires a different chunking strategy
    """
    # Code-based: Files with functions, classes, methods
    FUNCTION_BASED = "function_based"  # Python, Java, C++, JavaScript, etc.
    
    # Config-based: Files with sections and key-value pairs
    SECTION_BASED = "section_based"    # YAML, TOML, INI, HCL
    
    # Document-based: Files with hierarchical headings
    HEADING_BASED = "heading_based"    # Markdown, RST, LaTeX, Org-mode
    
    # Markup-based: Files with nested elements/tags
    ELEMENT_BASED = "element_based"    # HTML, XML, SVG
    
    # Build-based: Files with targets, rules, recipes
    RULE_BASED = "rule_based"          # Makefile, CMake, Ninja, Bazel
    
    # Data-based: Files with records, rows, entries
    RECORD_BASED = "record_based"      # CSV, JSON (as data), SQL dumps
    
    # Query-based: Files with queries, operations
    QUERY_BASED = "query_based"        # SQL, GraphQL, SPARQL
    
    # Template-based: Files with templates and interpolation
    TEMPLATE_BASED = "template_based"  # Jinja, EJS, Twig, Handlebars
    
    # Schema-based: Files defining data structures
    SCHEMA_BASED = "schema_based"      # Protocol Buffers, Thrift, GraphQL schemas


# Map each language to its primary architecture
LANGUAGE_ARCHITECTURE: Dict[str, FileArchitecture] = {
    # FUNCTION_BASED (Code with functions/classes/methods)
    **{lang: FileArchitecture.FUNCTION_BASED for lang in [
        'c', 'cpp', 'java', 'python', 'javascript', 'typescript', 'tsx',
        'go', 'rust', 'zig', 'nim', 'd', 'v', 'odin', 'carbon',
        'csharp', 'fsharp', 'kotlin', 'scala', 'groovy', 'clojure',
        'ruby', 'php', 'lua', 'perl', 'elixir', 'erlang', 'dart',
        'haskell', 'ocaml', 'swift', 'elm', 'purescript', 'racket', 'scheme',
        'commonlisp', 'reasonml', 'agda', 'idris', 'lean',
        'fortran', 'ada', 'pascal', 'actionscript',
        'apex', 'hack', 'haxe', 'gdscript', 'objc',
        'bash', 'fish', 'powershell', 'tcl',
        'r', 'julia', 'matlab', 'scilab',
        'solidity', 'cairo', 'clarity', 'vyper',
        'gleam', 'hare', 'pony', 'unison',
        'elisp', 'fennel', 'janet',
        'bsl', 'pike', 'sourcepawn', 'squirrel', 'pony',
        'magik', 'netlinx', 'nqc',
    ]},
    
    # SECTION_BASED (Config files with sections)
    **{lang: FileArchitecture.SECTION_BASED for lang in [
        'yaml', 'toml', 'ini', 'hcl', 'terraform', 'bicep',
        'properties', 'kdl', 'ron', 'dhall',
        'git_config', 'gitattributes', 'gitignore',
        'readline', 'udev', 'kconfig',
    ]},
    
    # HEADING_BASED (Documentation with hierarchical structure)
    **{lang: FileArchitecture.HEADING_BASED for lang in [
        'markdown', 'markdown_inline', 'rst', 'latex', 'org', 'typst',
        'pod', 'doxygen', 'asciidoc',
    ]},
    
    # ELEMENT_BASED (Markup with nested elements)
    **{lang: FileArchitecture.ELEMENT_BASED for lang in [
        'html', 'xml', 'svg', 'dtd', 'pem',
        'vue', 'svelte', 'astro',
    ]},
    
    # RULE_BASED (Build files with targets/rules)
    **{lang: FileArchitecture.RULE_BASED for lang in [
        'make', 'cmake', 'ninja', 'bazel', 'starlark', 'bitbake',
        'meson', 'just', 'gn',
    ]},
    
    # RECORD_BASED (Data files with records)
    **{lang: FileArchitecture.RECORD_BASED for lang in [
        'csv', 'tsv', 'psv',
        'json', 'json5', 'jsonnet',  # When used as data, not config
        'beancount', 'ledger',
        'po', 'pgn',
    ]},
    
    # QUERY_BASED (Query languages)
    **{lang: FileArchitecture.QUERY_BASED for lang in [
        'sql', 'plsql', 'graphql', 'sparql', 'rego',
    ]},
    
    # TEMPLATE_BASED (Template files)
    **{lang: FileArchitecture.TEMPLATE_BASED for lang in [
        'jinja', 'ejs', 'twig', 'heex', 'embeddedtemplate',
        'mustache', 'handlebars',
    ]},
    
    # SCHEMA_BASED (Schema definition files)
    **{lang: FileArchitecture.SCHEMA_BASED for lang in [
        'protobuf', 'proto', 'thrift', 'capnp',
        'prisma', 'smithy', 'avro',
        'yang', 'systemrdl',
    ]},
}


# Define what to extract for each architecture type
ARCHITECTURE_EXTRACTION_STRATEGY: Dict[FileArchitecture, Dict[str, str]] = {
    FileArchitecture.FUNCTION_BASED: {
        "primary": "function, class, method, interface, trait, struct, enum",
        "secondary": "module, namespace, package",
        "fallback": "top-level declarations",
    },
    
    FileArchitecture.SECTION_BASED: {
        "primary": "section, block, table, nested_object",
        "secondary": "key-value pairs, array items",
        "fallback": "logical groups separated by blank lines",
    },
    
    FileArchitecture.HEADING_BASED: {
        "primary": "heading levels (h1, h2, h3...)",
        "secondary": "code blocks, lists, tables",
        "fallback": "paragraphs separated by blank lines",
    },
    
    FileArchitecture.ELEMENT_BASED: {
        "primary": "semantic elements (div, section, article)",
        "secondary": "scripts, styles, components",
        "fallback": "top-level elements",
    },
    
    FileArchitecture.RULE_BASED: {
        "primary": "targets, rules, recipes, tasks",
        "secondary": "variables, macros, functions",
        "fallback": "logical rule groups",
    },
    
    FileArchitecture.RECORD_BASED: {
        "primary": "records, rows, entries, transactions",
        "secondary": "data blocks, grouped records",
        "fallback": "fixed-size chunks with headers",
    },
    
    FileArchitecture.QUERY_BASED: {
        "primary": "queries, operations, statements",
        "secondary": "subqueries, CTEs, views",
        "fallback": "statement-level chunks",
    },
    
    FileArchitecture.TEMPLATE_BASED: {
        "primary": "template blocks, macros, includes",
        "secondary": "variables, expressions, filters",
        "fallback": "logical template sections",
    },
    
    FileArchitecture.SCHEMA_BASED: {
        "primary": "messages, services, types, models",
        "secondary": "fields, enums, options",
        "fallback": "top-level definitions",
    },
}


def get_architecture(language: str) -> FileArchitecture:
    """
    Get the architecture type for a given language
    Returns FUNCTION_BASED as default for unknown languages
    """
    return LANGUAGE_ARCHITECTURE.get(language, FileArchitecture.FUNCTION_BASED)


def get_extraction_strategy(language: str) -> Dict[str, str]:
    """Get the extraction strategy for a language based on its architecture"""
    architecture = get_architecture(language)
    return ARCHITECTURE_EXTRACTION_STRATEGY[architecture]


# Statistics
def print_architecture_stats():
    """Print statistics about architecture distribution"""
    from collections import Counter
    
    arch_counts = Counter(LANGUAGE_ARCHITECTURE.values())
    
    print("File Architecture Distribution:")
    print("=" * 60)
    for arch, count in arch_counts.most_common():
        print(f"{arch.value:20s}: {count:3d} languages")
    print("=" * 60)
    print(f"Total: {len(LANGUAGE_ARCHITECTURE)} languages categorized")
    
    print("\n\nLanguages by Architecture:")
    print("=" * 60)
    for arch in FileArchitecture:
        langs = [lang for lang, a in LANGUAGE_ARCHITECTURE.items() if a == arch]
        if langs:
            print(f"\n{arch.value.upper()}:")
            print(f"  ({len(langs)} languages)")
            print(f"  {', '.join(sorted(langs)[:10])}", end='')
            if len(langs) > 10:
                print(f"... and {len(langs) - 10} more")
            else:
                print()


if __name__ == "__main__":
    print_architecture_stats()
