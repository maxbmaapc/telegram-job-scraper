# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs sessions data

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV WEB_HOST=0.0.0.0
ENV WEB_PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:8080/health || exit 1

# Create a startup script to run both services
RUN echo '#!/bin/bash\n\
# Start the web server in the background\n\
python -m web.app &\n\
WEB_PID=$!\n\
\n\
# Wait a moment for web server to start\n\
sleep 5\n\
\n\
# Start the Telegram scraper\n\
python -m src.main --mode continuous\n\
\n\
# If scraper exits, kill web server\n\
kill $WEB_PID\n\
wait' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]
