# Use a multi-stage build to reduce final image size
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Add retry mechanism for pip install
RUN pip install --no-cache-dir -r requirements.txt || \
    (sleep 5 && pip install --no-cache-dir -r requirements.txt) || \
    (sleep 10 && pip install --no-cache-dir -r requirements.txt)

# Final stage
FROM python:3.9-slim
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"

# Install only required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for better model downloading
ENV HF_HOME="/app/huggingface"
ENV TRANSFORMERS_CACHE="/app/huggingface/transformers"
ENV HF_HUB_ENABLE_HF_TRANSFER=1
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Copy application code
COPY . .

# Create cache directories
RUN mkdir -p /app/huggingface/transformers

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Command to run the application
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1