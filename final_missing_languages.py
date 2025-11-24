#!/usr/bin/env python3
"""
FINAL Missing Languages to Add
Based on tree-sitter-language-pack official documentation
"""

# These are confirmed missing from our implementation
FINAL_MISSING = {
    # Recently added to pack or less common
    'dhall': '.dhall',
    'diff': '.diff .patch',
    'ebnf': '.ebnf',
    'eiffel': '.e',
    'ejs': '.ejs',
    'glimmer': '.gjs .gts',
    'idris': '.idr',
    'jinja': '.j2 .jinja .jinja2',
    'json5': '.json5',
    'jupyter': '.ipynb',
    'lean': '.lean',
    'marko': '.marko',
    'markdown_inline': '.md',
    'pike': '.pike',
    'pjs': '.pjs',
    'plsql': '.pls .plsql',
    'regex': '.regex',
    'sexpr': '.sexp',
    'sourcepawn': '.sp',
    'systemrdl': '.rdl',
    'tsq': '.tsq',
    'unison': '.u',
    'webdriver': '.webdriver',
    'wing': '.w',
    'yang': '.yang',
    'gitcommit': 'COMMIT_EDITMSG GIT_COMMIT_EDITMSG',
    'psv': '.psv',
}

print(f"Final missing languages: {len(FINAL_MISSING)}")
print("\nLanguages to add:")
for lang, ext in sorted(FINAL_MISSING.items()):
    print(f"  {lang:20s} -> {ext}")

# Create queries for these
FINAL_QUERIES = {}
for lang in FINAL_MISSING.keys():
    if lang in ['dhall', 'idris', 'lean', 'unison']:
        FINAL_QUERIES[lang] = """(function_definition) @function (type_definition) @type"""
    elif lang in ['diff', 'patch']:
        FINAL_QUERIES[lang] = """(hunk) @hunk (file) @file (change) @change"""
    elif lang in ['ebnf', 'regex', 'sexpr']:
        FINAL_QUERIES[lang] = """(rule) @rule (expression) @expression"""
    elif lang in ['eiffel', 'sourcepawn', 'pike']:
        FINAL_QUERIES[lang] = """(class_declaration) @class (function_declaration) @function"""
    elif lang in ['ejs', 'jinja', 'marko']:
        FINAL_QUERIES[lang] = """(template) @template (expression) @expression (directive) @directive"""
    elif lang in ['glimmer']:
        FINAL_QUERIES[lang] = """(component) @component (template) @template"""
    elif lang in ['json5', 'jupyter']:
        FINAL_QUERIES[lang] = """(object) @object (array) @array (pair) @pair"""
    elif lang in ['plsql']:
        FINAL_QUERIES[lang] = """(create_function) @function (create_procedure) @procedure (create_package) @package"""
    elif lang in ['systemrdl', 'yang']:
        FINAL_QUERIES[lang] = """(module) @module (definition) @definition"""
    elif lang in ['tsq']:
        FINAL_QUERIES[lang] = """(query) @query (predicate) @predicate"""
    elif lang in ['webdriver']:
        FINAL_QUERIES[lang] = """(command) @command (locator) @locator"""
    elif lang in ['wing']:
        FINAL_QUERIES[lang] = """(class_declaration) @class (function_declaration) @function (resource) @resource"""
    elif lang == 'gitcommit':
        FINAL_QUERIES[lang] = """(subject) @subject (message) @message (comment) @comment"""
    elif lang in ['psv', 'markdown_inline']:
        FINAL_QUERIES[lang] = """(text) @text"""
    else:
        FINAL_QUERIES[lang] = """(function) @function (class) @class"""

print(f"\nQueries prepared: {len(FINAL_QUERIES)}")
