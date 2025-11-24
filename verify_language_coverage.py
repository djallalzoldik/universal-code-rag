#!/usr/bin/env python3
"""
Cross-reference check: Official tree-sitter-language-pack vs Our Implementation
"""

# Official list from tree-sitter-language-pack documentation (165+ languages)
OFFICIAL_LANGUAGES = {
    'actionscript', 'ada', 'agda', 'apex', 'arduino', 'asm', 'astro', 
    'bash', 'beancount', 'bibtex', 'bicep', 'bitbake', 'bsl',
    'c', 'cairo', 'capnp', 'chatito', 'clarity', 'clojure', 'cmake', 'comment', 'commonlisp', 'cpon',
    'cpp', 'csharp', 'css', 'csv', 'cuda',
    'd', 'dart', 'dockerfile', 'doxygen', 'dtd',
    'elisp', 'elixir', 'elm', 'embeddedtemplate', 'erlang',
    'fennel', 'firrtl', 'fish', 'fortran', 'fsharp', 'func',
    'gdscript', 'gitattributes', 'gitcommit', 'gitignore', 'gleam', 'glsl', 'gn', 'go', 'gomod', 'gosum', 'graphql', 'groovy', 'gstlaunch',
    'hack', 'hare', 'haskell', 'haxe', 'hcl', 'heex', 'hlsl', 'html', 'http', 'hyprlang',
    'ini', 'ispc',
    'janet', 'java', 'javascript', 'jsdoc', 'json', 'jsonnet', 'julia',
    'kconfig', 'kdl', 'kotlin',
    'latex', 'linkerscript', 'llvm', 'lua', 'luadoc', 'luap', 'luau',
    'magik', 'make', 'markdown', 'markdown_inline', 'matlab', 'mermaid', 'meson',
    'netlinx', 'nim', 'ninja', 'nix', 'nqc',
    'objc', 'ocaml', 'odin', 'org',
    'pascal', 'pem', 'perl', 'pgn', 'php', 'po', 'pony', 'powershell', 'printf', 'prisma', 'properties', 'proto', 'psv', 'puppet', 'purescript', 'pymanifest', 'python',
    'qmldir', 'qmljs', 'query',
    'r', 'racket', 'rbs', 're2c', 'readline', 'rego', 'requirements', 'ron', 'rst', 'ruby', 'rust',
    'scala', 'scheme', 'scss', 'slang', 'smali', 'smithy', 'solidity', 'sparql', 'sql', 'squirrel', 'starlark', 'svelte', 'swift',
    'tablegen', 'tcl', 'test', 'thrift', 'toml', 'tsv', 'tsx', 'twig', 'typescript', 'typst',
    'udev', 'ungrammar', 'uxntal',
    'v', 'verilog', 'vhdl', 'vim', 'vue',
    'wast', 'wat', 'wgsl', 'xcompose', 'xml',
    'yaml', 'yuck', 'zig',
    
    # Additional from extended search
    'dhall', 'diff', 'dot', 'ebnf', 'eiffel', 'ejs', 'glimmer', 'idris', 'jinja', 'json5', 'jupyter', 
    'lean', 'marko', 'pike', 'pjs', 'plsql', 'regex', 'sexpr', 'sourcepawn', 'systemrdl', 'tsq', 
    'unison', 'webdriver', 'wing', 'yang'
}

# Our current implementation
OUR_LANGUAGES = {
    'c', 'cpp', 'java', 'kotlin', 'scala', 'groovy', 'clojure',
    'go', 'rust', 'zig', 'nim', 'd', 'v', 'odin', 'cuda', 'fortran', 'asm', 'carbon',
    'csharp', 'fsharp',
    'python', 'ruby', 'php', 'lua', 'perl', 'elixir', 'erlang', 'dart', 'actionscript',
    'bash', 'fish', 'powershell', 'tcl',
    'haskell', 'ocaml', 'swift', 'elm', 'purescript', 'racket', 'scheme', 'commonlisp', 'reasonml', 'agda',
    'javascript', 'typescript', 'tsx', 'html', 'css', 'vue', 'svelte', 'astro',
    'json', 'yaml', 'toml', 'xml', 'csv', 'ini', 'properties',
    'sql', 'graphql',
    'protobuf', 'thrift', 'capnp',
    'dockerfile', 'terraform', 'hcl', 'cmake', 'make', 'ninja', 'bazel', 'bitbake',
    'markdown', 'rst', 'latex', 'org', 'bibtex', 'pod',
    'r', 'julia', 'matlab', 'scilab',
    'verilog', 'vhdl', 'systemverilog',
    'solidity', 'cairo', 'clarity',
    'apex', 'arduino',
    'beancount', 'ledger',
    'ada', 'bicep', 'chatito', 'devicetree', 'dot', 'git_config', 'git_rebase', 
    'gitattributes', 'gitignore', 'gpg', 'http', 'just', 'kdl', 'meson', 'nix',
    'passwd', 'smithy', 'starlark', 'textproto', 'todotxt', 'tsv', 'udev', 'urll', 'requirements',
    # From addon file
    'gdscript', 'glsl', 'hlsl', 'wgsl', 'ispc', 'firrtl', 'magik', 'squirrel', 'nqc',
    'elisp', 'fennel', 'janet',
    'jsdoc', 'twig', 'heex', 'embeddedtemplate',
    'jsonnet', 'ron', 'cpon', 'hyprlang',
    'llvm', 'linkerscript', 'tablegen', 'smali',
    'objc', 'hack', 'haxe',
    'sparql', 'rego', 'prisma',
    'vim', 'doxygen', 'comment', 'readline',
    'mermaid', 'puppet', 'kconfig', 'gstlaunch',
    'luau', 'luap', 'luadoc',
    'typst', 'dtd',
    'gleam', 'hare', 'pony', 'rbs',
    'bsl', 'func', 'netlinx', 'pascal', 'pem', 'pgn', 'po', 'printf',
    'pymanifest', 'qmljs', 'qmldir', 'query', 're2c', 'slang', 'test',
    'ungrammar', 'uxntal', 'wast', 'wat', 'xcompose', 'yuck', 'gomod', 'gosum', 'scss'
}

print(f"Official languages: {len(OFFICIAL_LANGUAGES)}")
print(f"Our languages: {len(OUR_LANGUAGES)}")

missing = OFFICIAL_LANGUAGES - OUR_LANGUAGES
print(f"\n❌ Missing languages ({len(missing)}):")
for lang in sorted(missing):
    print(f"  - {lang}")

extra = OUR_LANGUAGES - OFFICIAL_LANGUAGES  
print(f"\n➕ Extra languages we have ({len(extra)}):")
for lang in sorted(extra):
    print(f"  - {lang}")

print(f"\n✅ Coverage: {len(OUR_LANGUAGES & OFFICIAL_LANGUAGES)}/{len(OFFICIAL_LANGUAGES)} = {100 * len(OUR_LANGUAGES & OFFICIAL_LANGUAGES) / len(OFFICIAL_LANGUAGES):.1f}%")
