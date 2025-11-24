FROM python:3.10-slim

# Install system dependencies
# build-essential is needed for tree-sitter
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directory for database
RUN mkdir -p chrome_rag_db logs

# Set entrypoint
ENTRYPOINT ["python", "cli.py"]
CMD ["--help"]
