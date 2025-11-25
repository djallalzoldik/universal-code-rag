# Multi-stage Docker build for optimized image size
# Stage 1: Builder - Compile and install dependencies
FROM python:3.10-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime - Minimal production image
FROM python:3.10-slim

# Install only runtime dependencies (git for gitpython)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p chrome_rag_db logs

# Make PATH include user packages
ENV PATH=/root/.local/bin:$PATH

# Add health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python health_check.py || exit 1

# Set entrypoint and default command
ENTRYPOINT ["python", "cli.py"]
CMD ["--help"]
