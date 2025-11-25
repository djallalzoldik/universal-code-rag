# Docker Indexing - Quick Fix Guide

## The Problem
Your Docker command was **missing the cache volume mount**, so Docker couldn't see the downloaded model file and kept trying to download it again.

## The Solution

### Step 1: Fix Permissions (Run Once)
```bash
sudo chown -R $(whoami):$(whoami) ~/chrome-rag-cache
```

### Step 2: Run Docker with ALL 3 Volume Mounts

**COPY AND RUN THIS EXACT COMMAND:**
```bash
docker run --rm \
  -v /home/djallalakira/chrome-rag-system/test_samples:/source \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v /home/djallalakira/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag index --path /source
```

### What Changed?
Added this line (you were missing it):
```bash
  -v /home/djallalakira/chrome-rag-cache:/root/.cache/chroma \
```

## Verify It Works

After running the command, you should see:
- ✅ "Found 55 files"
- ✅ Processing files progress bar reaches 100%
- ✅ "Indexing complete!" message
- ✅ Statistics showing 765 chunks created

## Expected Warnings (These are OK!)
```
ERROR Failed to initialize sql parser
ERROR Failed to initialize markdown parser  
ERROR Failed to initialize haskell parser
ERROR Failed to initialize xml parser
ERROR Failed to initialize protobuf parser
```

**These are NOT blocking errors** - the files still get indexed using fallback strategies.

## For Your Real Chrome Source Code

Once this works with test samples, use:
```bash
docker run --rm \
  -v /path/to/your/chrome/source:/source \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  -v /home/djallalakira/chrome-rag-cache:/root/.cache/chroma \
  chrome-rag index --path /source
```

Replace `/path/to/your/chrome/source` with your actual Chrome source directory.
