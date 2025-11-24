# Chrome Source Code RAG System

A professional, production-ready Retrieval-Augmented Generation (RAG) system for indexing and analyzing Chrome/Chromium source code. Designed for security vulnerability analysis and code comprehension.

## 🐳 Running with Docker

You can run the tool in a container to avoid dependency issues.

### Prerequisites
- Docker
- Docker Compose

### Usage

1. **Build the image**:
   ```bash
   docker-compose build
   ```

2. **Index a directory**:
   Mount your source code directory to `/app/source` (or any path) and run:
   ```bash
   # Example: Indexing a local folder mapped to /source
   docker run -v $(pwd)/test_samples:/source -v $(pwd)/chrome_rag_db:/app/chrome_rag_db chrome-rag index --path /source
   ```

3. **Search**:
   ```bash
   docker run -v $(pwd)/chrome_rag_db:/app/chrome_rag_db chrome-rag search --query "vulnerability"
   ```

4. **Web Interface**:
   To run the Streamlit app in Docker, you'll need to expose the port:
   ```bash
   docker run -p 8501:8501 -v $(pwd)/chrome_rag_db:/app/chrome_rag_db chrome-rag streamlit run web_app.py
   ```

## 🔍 Hybrid Search

The system now uses **Hybrid Search** combining:
1. **Vector Search**: Finds semantically similar code.
2. **BM25 (Keyword) Search**: Finds exact matches for variable names, constants, etc.
3. **Reciprocal Rank Fusion (RRF)**: Merges results for best accuracy.

This happens automatically when you use the `search` command.

## Features

### 🎯 Multi-Language Support
- **C/C++** (.cc, .cpp, .h, .hpp) - Functions, classes, namespaces, enums, macros
- **Python** (.py) - Functions, classes, methods, constants
- **JavaScript/TypeScript** (.js, .ts, .jsx, .tsx) - Functions, arrow functions, classes, methods
- **Mojom** (.mojom, .mojo) - Interfaces, structs, unions, enums, constants
- **GN Build** (.gn, .gni) - Build targets, templates, variables

### ⚡ Professional Architecture
- **Parallel Processing** for 4x-8x faster indexing
- **Incremental Updates** to skip unchanged files
- **Tree-sitter parsing** for accurate C++, Python, and JavaScript analysis
- **Batch processing** for efficient indexing of large codebases
- **Vector database** (ChromaDB) for semantic code search

### 🔍 Powerful Interfaces
- **Web UI** (Streamlit) for easy exploration
- **CLI** for automation and power users
- Semantic search across all code
- Symbol lookup by name
- Database statistics and insights

## Installation

```bash
# Clone or download this repository
cd chrome-rag-system

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Index Chrome Source Code

```bash
# Index the entire Chrome src/ directory
python cli.py index --path /path/to/chromium/src

# Index only specific file types
python cli.py index --path /path/to/chromium/src --file-types cpp,python

# Clear existing database and reindex
python cli.py index --path /path/to/chromium/src --clear
```

### 2. Search for Code

```bash
# Semantic search
python cli.py search --query "memory allocation buffer overflow"

# Search with filters
python cli.py search --query "render process" --language cpp --n-results 10

# Show full code without truncation
python cli.py search --query "sandbox escape" --full
```

### 3. Lookup Symbols

```bash
# Find a specific class
python cli.py symbol --name RenderFrameHost --type class

# Find a function across all languages
python cli.py symbol --name ProcessMessage

# Filter by language
python cli.py symbol --name WebContents --language cpp
```

### 4. View Statistics

```bash
# View database statistics
python cli.py stats
```

### 5. Web Interface

```bash
# Launch the web application
streamlit run web_app.py
```

### 6. Clear Database

```bash
# Clear all indexed data
python cli.py clear --yes
```

## Architecture

```
chrome-rag-system/
├── config.py              # Configuration management
├── rag.py                 # Vector database operations
├── indexer.py             # File discovery and processing
├── cli.py                 # Command-line interface
├── chunkers/              # Language-specific parsers
│   ├── base_chunker.py    # Abstract base class
│   ├── cpp_chunker.py     # C++ parser
│   ├── python_chunker.py  # Python parser
│   ├── javascript_chunker.py  # JavaScript/TypeScript parser
│   ├── mojom_chunker.py   # Mojom interface parser
│   └── gn_chunker.py      # GN build system parser
└── utils/                 # Logging and utilities
    └── logger.py          # Rich console output
```

## Configuration

Edit `config.py` to customize:

- Database path and collection name
- Batch size for processing
- Excluded directories
- File type mappings
- Chunk size limits

```python
# Example: Change database path
CONFIG.db_path = "/custom/path/to/db"

# Example: Add excluded directories
CONFIG.exclude_dirs.add('experimental')

# Example: Adjust batch size
CONFIG.batch_size = 200
```

## Advanced Usage

### Python API

```python
from rag import ChromeRAGSystem
from indexer import ChromeIndexer

# Initialize system
rag = ChromeRAGSystem(db_path="./my_db")
indexer = ChromeIndexer(rag)

# Index directory
stats = indexer.index_directory("/path/to/chromium/src")

# Semantic search
results = rag.retrieve_context("buffer overflow", n_results=5)

# Symbol lookup
symbols = rag.retrieve_symbol("RenderFrameHost", symbol_type="class")

# Get statistics
stats = rag.get_statistics()
```

### Vulnerability Analysis Template

```python
from rag import ChromeRAGSystem, VulnerabilityAnalyzer

rag = ChromeRAGSystem()
analyzer = VulnerabilityAnalyzer(rag)

# Analyze a file (integrate with your AI API)
results = await analyzer.analyze_file("/path/to/suspicious.cc")
```

## Use Cases

### 🔒 Security Research
- Find vulnerable code patterns across the codebase
- Track usage of security-sensitive APIs
- Analyze attack surface areas

### 📚 Code Comprehension
- Understand complex class hierarchies
- Find all implementations of an interface
- Trace function call paths

### 🔍 Bug Hunting
- Search for similar bugs across modules
- Find unsafe coding patterns
- Locate error handling gaps

### 🏗️ Refactoring
- Find all usages of deprecated APIs
- Identify code duplication
- Analyze dependencies

## Performance

- **Indexing speed**: ~100-500 files/second (depending on file size)
- **Batch processing**: Efficient memory usage for large codebases
- **Search latency**: <100ms for most queries
- **Database size**: ~1-2GB for full Chrome codebase

## Troubleshooting

### Issue: Import errors

```bash
# Ensure all dependencies are installed
pip install -r requirements.txt --upgrade
```

### Issue: Slow indexing

```bash
# Increase batch size
python cli.py index --path /path/to/src --batch-size 200

# Index only specific file types
python cli.py index --path /path/to/src --file-types cpp
```

### Issue: Out of memory
- Reduce batch size: `--batch-size 50`
- Disable parallel processing: `--no-parallel`
- Index subdirectories separately
- Exclude large test directories in `config.py`

## Contributing

This system is designed to be extensible:

1. **Add new languages**: Create a new chunker in `chunkers/`
2. **Custom metadata**: Extend the `CodeChunk` dataclass
3. **AI integration**: Implement the `VulnerabilityAnalyzer` template
4. **Enhanced search**: Add filters to `retrieve_context()`

## License

This project is provided as-is for educational and research purposes.

## Credits

Built with:
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [tree-sitter](https://tree-sitter.github.io/) - Code parsing
- [Rich](https://rich.readthedocs.io/) - Terminal UI

---

**Note**: This system is designed for Chrome/Chromium source code but can be adapted for any large codebase with similar file structures.
