# Additional language queries for tree-sitter-language-pack (80+ languages)
ADDITIONAL_QUERIES = {
    # Game Dev/Graphics
    'gdscript': """(class_definition) @class (function_definition) @function""",
    'glsl': """(function_definition) @function (struct_specifier) @struct""",
    'hlsl': """(function_definition) @function (struct_declaration) @struct""",
    'wgsl': """(function_declaration) @function (struct_declaration) @struct""",
    'ispc': """(function_definition) @function (struct_specifier) @struct""",
    'firrtl': """(module) @module (circuit) @circuit""",
    'magik': """(method_definition) @method (procedure_definition) @procedure""",
    'squirrel': """(function_declaration) @function (class_declaration) @class""",
    'nqc': """(task) @task (function_definition) @function""",
    
    # Lisp/Functional Variants
    'elisp': """(defun) @function (defmacro) @macro (defvar) @variable""",
    'fennel': """(function_definition) @function (lambda) @lambda""",
    'janet': """(defn) @function (defmacro) @macro""",
    
    # Web/JS Extended
    'jsdoc': """(tag) @tag (type) @type""",
    'twig': """(block) @block (variable) @variable (function_call) @function""",
    'heex': """(component) @component (slot) @slot""",
    'embeddedtemplate': """(code) @code (directive) @directive""",
    
    # Data/Config Extended
    'jsonnet': """(function) @function (local_bind) @binding""",
    'ron': """(struct_variant) @struct (enum_variant) @enum""",
    'cpon': """(map) @map (array) @array""",
    'kdl': """(node) @node (property) @property""",
    'hyprlang': """(section) @section (keyword) @keyword""",
    
    # Systems/Low-level
    'llvm': """(define) @function (declare) @declaration (type) @type""",
    'linkerscript': """(sections) @sections (memory) @memory""",
    'tablegen': """(def) @definition (class) @class""",
    'asm': """(instruction) @instruction (label) @label""",
    'smali': """(class_directive) @class (method_directive) @method""",
    
    # Mobile/Platform
    'objc': """(class_interface) @class (method_declaration) @method (protocol_declaration) @protocol""",
    'hack': """(class_declaration) @class (function_declaration) @function""",
    'apex': """(class_declaration) @class (method_declaration) @method""",
    '

haxe': """(class_declaration) @class (function_declaration) @function""",
    'gdscript': """(class_definition) @class (function_definition) @function""",
    
    # Query/Data
    'sparql': """(select_query) @select (construct_query) @construct""",
    'rego': """(rule) @rule (function) @function""",
    'prisma': """(model_declaration) @model (enum_declaration) @enum""",
    'graphql': """(operation_definition) @operation (fragment_definition) @fragment""",
    
    # Tools/Editors
    'vim': """(function_definition) @function (command_declaration) @command""",
    'doxygen': """(command) @command (paragraph) @paragraph""",
    'comment': """(comment) @comment""",
    'readline': """(binding) @binding (conditional) @conditional""",
    
    # Build/Config Extended
    'mermaid': """(diagram) @diagram (node) @node""",
    'puppet': """(class) @class (define) @define (resource) @resource""",
    'kconfig': """(config) @config (menu) @menu""",
    'gstlaunch': """(element) @element (property) @property""",
    
    # Scripting Extended
    'luau': """(function_declaration) @function (type_declaration) @type""",
    'luap': """(pattern) @pattern (capture) @capture""",
    'luadoc': """(comment) @comment (tag) @tag""",
    
    # Documentation
    'typst': """(function) @function (heading) @heading (markup) @markup""",
    'pod': """(command) @command (paragraph) @paragraph""",
    'dtd': """(element_decl) @element (attlist_decl) @attribute""",
    
    # Functional/ML
    'gleam': """(function_definition) @function (type_definition) @type""",
    'hare': """(function_declaration) @function (type_declaration) @type""",
    'pony': """(class_def) @class (fun_def) @function""",
    'rbs': """(class_decl) @class (interface_decl) @interface""",
    
    # Other
    'bsl': """(procedure) @procedure (function) @function""",
    'func': """(function_definition) @function""",
    'netlinx': """(program) @program (define_function) @function""",
    'pascal': """(class_declaration) @class (function_declaration) @function""",
    'pem': """(certificate) @certificate (key) @key""",
    'pgn': """(game) @game (move) @move""",
    'po': """(msgid) @msgid (msgstr) @msgstr""",
    'printf': """(directive) @directive""",
    'pymanifest': """(include) @include (exclude) @exclude""",
    'qmljs': """(ui_object_definition) @component (function_declaration) @function""",
    'qmldir': """(module_identifier) @module (type_info) @type""",
    'query': """(query) @query (predicate) @predicate""",
    're2c': """(rule) @rule (action) @action""",
    'slang': """(function_declaration) @function (class_declaration) @class""",
    'test': """(test_case) @test (assertion) @assertion""",
    'ungrammar': """(rule) @rule (alternative) @alternative""",
    'uxntal': """(label) @label (macro) @macro""",
    'wast': """(module) @module (func) @function""",
    'wat': """(module) @module (func) @function""",
    'xcompose': """(sequence) @sequence (action) @action""",
    'yuck': """(defwidget) @widget (defvar) @variable""",
    'gomod': """(module_directive) @module (require_directive) @require""",
    'gosum': """(entry) @entry""",
    'scss': """(ruleset) @rule (mixin_statement) @mixin (function_statement) @function""",
}

print(f"Total additional queries: {len(ADDITIONAL_QUERIES)}")
