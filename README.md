# Chrome Source Code RAG System

![Production Ready](https://img.shields.io/badge/status-production%20ready-success)
![Zero Errors](https://img.shields.io/badge/indexing-zero%20errors-success)
![Docker Size](https://img.shields.io/badge/docker%20image-optimized-blue)
![CI/CD](https://img.shields.io/badge/build-passing-success)
![License](https://img.shields.io/badge/license-MIT-green)

A professional, production-ready Retrieval-Augmented Generation (RAG) system designed for deep analysis of the Chrome/Chromium codebase. It combines vector search, keyword search (BM25), and structural code parsing to provide accurate, context-aware code retrieval for security research and vulnerability analysis.

---

## 🚀 Key Features

### 🎯 Zero-Error Indexing
- **Robust Parsing**: Built on `tree-sitter` with a custom `QueryCursor` implementation to ensure **100% error-free indexing**.
- **Resilient Fallbacks**: Automatically falls back to text-based chunking for unsupported or malformed files.
- **Full Coverage**: Successfully processes complex C++, Python, JavaScript, and system files without crashing.

### 🔍 Advanced Hybrid Search
- **Vector Search**: Uses `ChromaDB` to find semantically similar code (e.g., "memory leak patterns").
- **Keyword Search**: Uses `BM25` to find exact matches for identifiers and constants.
- **RRF Fusion**: Combines results using Reciprocal Rank Fusion for superior relevance.
- **Smart Filtering**: Filter by language (e.g., `cpp`, `python`) and code type (e.g., `class`, `function`).

### 🐳 Production-Grade Docker
- **Optimized Image**: Multi-stage build reduces image size to **<1GB**.
- **Fast Builds**: `.dockerignore` reduces build context by **99.7%** (from 959MB to 311KB).
- **Health Monitoring**: Integrated `health_check.py` and Docker `HEALTHCHECK` for reliability.
- **Orchestration**: Includes `docker-compose.prod.yml` with resource limits and restart policies.

### 🔄 Automated CI/CD
- **GitHub Actions**: Full pipeline defined in `.github/workflows/ci.yml`.
- **Automated Testing**: Runs architecture, chunking, and search tests on every push.
- **Build Verification**: Automatically builds and verifies Docker images.

### 🌐 Multi-Language Support (33+ Languages)
The system intelligently chunks and indexes:
- **Core**: C++, Python, JavaScript, TypeScript, Java, Rust, Go
- **Web**: HTML, CSS, PHP, Ruby, Swift, Kotlin, Scala
- **System**: Bash, Shell, Batch, PowerShell, Perl, Lua
- **Config**: JSON, YAML, TOML, XML, SQL, CSV
- **Chrome Specific**: Mojom (IPC), GN (Build), Protocol Buffers

---

## 🛠️ Installation & Deployment

### Option 1: Docker (Recommended)

The easiest way to run the system is using Docker. You **must** mount your source code and database directory for the container to access them.

```bash
# 1. Build the image
docker build -t chrome-rag .

# 2. Pre-download embedding model (first time only, ~79MB)
mkdir -p ~/chrome-rag-cache
wget -O ~/chrome-rag-cache/onnx_models/all-MiniLM-L6-v2/onnx.tar.gz \
  https://chroma-onnx-models.s3.amazonaws.com/all-MiniLM-L6-v2/onnx.tar.gz

# 3. Run the container (Mounting Volumes is REQUIRED)
# Note: All 3 volume mounts are required
docker run --rm \
  -v /path/to/your/code:/source \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v ~/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag index --path /source
```

**Volume Mounts Explained:**
- `-v /path/to/your/code:/source`: Maps your local code to `/source` inside the container
- `-v $(pwd)/chrome_rag_db:/app/chrome_rag_db`: Saves the index locally so it persists after the container stops
- `-v ~/chrome-rag-cache:/root/.cache/chroma`: Caches the embedding model to avoid re-downloading (79MB)

**Expected Warnings:**
You may see warnings like `Failed to initialize sql parser` or `Invalid node type for markdown`. These are **normal and non-blocking**. The system automatically falls back to alternative chunking strategies and successfully indexes all files (verify with `Files Failed: 0` in the final statistics).

For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md).

### Option 2: Local Installation

Requires Python 3.10+.

```bash
# 1. Clone repository
git clone https://github.com/djallalzoldik/universal-code-rag.git
cd universal-code-rag

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run CLI
python cli.py --help
```

---

## 📖 Usage Guide

### Docker Usage (Recommended)

All commands work the same with Docker - just prefix with the Docker run command and mount your volumes.

**Base Docker Command Format:**
```bash
docker run --rm \
  -v /path/to/your/code:/source \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v ~/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag [COMMAND] [OPTIONS]
```

---

### 1. Indexing Code

Index a directory containing source code. The system automatically detects languages and chunks code intelligently.

**Docker:**
```bash
# Index entire directory
docker run --rm \
  -v /path/to/chromium/src:/source \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v ~/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag index --path /source

# Index only specific file types (faster)
docker run --rm \
  -v /path/to/chromium/src:/source \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v ~/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag index --path /source --file-types cpp,python,mojom

# Clear database and reindex
docker run --rm \
  -v /path/to/chromium/src:/source \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v ~/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag index --path /source --clear

# Force re-index all files (ignore incremental state)
docker run --rm \
  -v /path/to/chromium/src:/source \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v ~/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag index --path /source --force
```

**Local:**
```bash
# Index the entire Chrome src directory
python cli.py index --path /path/to/chromium/src

# Index only specific languages (faster)
python cli.py index --path /src --file-types cpp,python,mojom

# Clear and reindex
python cli.py index --path /src --clear
```

---

### 2. Semantic Search

Search for concepts, vulnerabilities, or code patterns using natural language.

**Docker:**
```bash
# General search
docker run --rm \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v ~/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag search --query "buffer overflow in render process"

# Filtered search (C++ only, top 10 results)
docker run --rm \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v ~/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag search --query "memory allocation" --language cpp --n-results 10

# Search in specific code types (only functions)
docker run --rm \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v ~/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag search --query "authentication logic" --type function
```

**Local:**
```bash
# General search
python cli.py search --query "buffer overflow in render process"

# Filtered search (C++ only, top 10 results)
python cli.py search --query "memory allocation" --language cpp --n-results 10
```

---

### 3. Symbol Lookup

Find definitions of specific classes, functions, or structs by exact name.

**Docker:**
```bash
# Find a class definition
docker run --rm \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v ~/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag symbol --name RenderFrameHost --type class

# Find a function across all languages
docker run --rm \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v ~/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag symbol --name ProcessMessage

# Find in specific language
docker run --rm \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v ~/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag symbol --name HandleRequest --language python
```

**Local:**
```bash
# Find a class definition
python cli.py symbol --name RenderFrameHost --type class

# Find a function across all languages
python cli.py symbol --name ProcessMessage
```

---

### 4. Database Statistics

View insights about the indexed codebase - total files, chunks, languages, etc.

**Docker:**
```bash
docker run --rm \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v ~/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag stats
```

**Local:**
```bash
python cli.py stats
```

---

### 5. Clear Database

Remove all indexed data and start fresh.

**Docker:**
```bash
docker run --rm \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v ~/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag clear
```

**Local:**
```bash
python cli.py clear
```

---

### 6. Web Interface (Local Only)

Launch the Streamlit-based UI for interactive exploration.

```bash
streamlit run web_app.py
```

> **Note:** Web interface is not available in Docker. For interactive use, run locally or use the CLI commands above.

---

### Common Docker Tips

**Shorter Alias:**
Add this to your `~/.bashrc` or `~/.zshrc`:
```bash
alias chrome-rag='docker run --rm \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v ~/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag'
```

Then use: `chrome-rag stats` or `chrome-rag search --query "XSS vulnerability"`

**Production deployment** with docker-compose, health checks, and resource limits: see [DEPLOYMENT.md](DEPLOYMENT.md).

**Quick Docker Reference Guide:** see [DOCKER_RUN_GUIDE.md](DOCKER_RUN_GUIDE.md).

---

## 🏗️ System Architecture

The system is built with a modular, extensible architecture:

```
chrome-rag-system/
├── config.py              # Centralized configuration
├── rag.py                 # Core RAG logic (Vector DB + BM25 + RRF)
├── indexer.py             # File discovery and parallel processing orchestration
├── cli.py                 # Command-line interface entry point
├── web_app.py             # Streamlit web interface
├── health_check.py        # Container health monitoring script
├── chunkers/              # Language-specific code parsers
│   ├── base_chunker.py    # Abstract base class
│   ├── tree_sitter_chunker.py  # Universal parser using tree-sitter
│   └── ... (legacy chunkers)
├── utils/                 # Utilities
│   ├── logger.py          # Rich terminal logging
│   └── state_manager.py   # Incremental indexing state
└── .github/               # CI/CD workflows
```

---

## 🧪 Testing

The project includes a comprehensive test suite ensuring stability and correctness.

```bash
# Run all tests
python tests/test_all_architectures.py

# Run specific feature tests
python tests/test_adaptive_chunking.py
python tests/test_hybrid_search.py
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Status**: 🟢 **Active & Maintained**
**Version**: 1.0.0
