# Comprehensive Language Test Suite

This directory contains **complex test files** for verifying support for 35+ programming languages.

## Tested Languages

### Systems Programming (7)
- C++, Go, Rust  
- Zig, Nim, D, CUDA

### JVM Languages (3)
- Java, Kotlin, Scala

### .NET (1)
- C# ✅ FIXED

### Dynamic Languages (8)
- Python, Ruby, PHP, Lua  
- Perl, Elixir, Erlang, Dart

### Web/JS Ecosystem (5)
- JavaScript, TypeScript, TSX  
- HTML, CSS

### Data Formats (4)
- JSON, YAML, TOML, XML

### Query Languages (2)
- SQL, GraphQL

### Functional Languages (3)
- Haskell, OCaml, Swift

### Documentation (1)
- Markdown

### Config/Infrastructure (4)
- Bash, Dockerfile, Terraform, Nginx

### Scientific/Data (2)
- R, Julia

### Blockchain (1)
- Solidity

### Protocols (2)
- Protocol Buffers, Thrift

## Running Tests

```bash
# Test all languages
python tests/test_all_languages.py

# Index specific directory
python cli.py index --path test_samples/all_languages
```

## Test File Complexity

Each test file includes:
- **Advanced language features** (generics, traits, coroutines)
- **Complex structures** (inheritance, modules, namespaces)
- **Real-world patterns** (repositories, services, decorators)
