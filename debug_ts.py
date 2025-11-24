import tree_sitter_php
import tree_sitter_java
import tree_sitter_go
import tree_sitter_rust
import tree_sitter_ruby
import tree_sitter_c_sharp

print("PHP dir:", dir(tree_sitter_php))
try:
    print("PHP language:", tree_sitter_php.language())
except Exception as e:
    print("PHP error:", e)

print("Java dir:", dir(tree_sitter_java))
print("Go dir:", dir(tree_sitter_go))
