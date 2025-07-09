# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs app/static/images/products app/static/images/accessories app/static/images/thumbnails

# Create non-root user and set permissions
RUN adduser --disabled-password --gecos '' --shell /bin/bash appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app/logs
USER appuser

# Expose port
EXPOSE 8000

# Set environment to production
ENV ENVIRONMENT=production
ENV HOST=0.0.0.0
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=5 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

RUN alembic upgrade head

CMD ["python", "production_start.py"]
