# Use the official LiteLLM image as base
FROM ghcr.io/berriai/litellm-database:0.11.0

# Labels for better container management
LABEL maintainer="Your Name <your.email@example.com>"
LABEL version="1.0.0"
LABEL description="LiteLLM proxy for multiple AI model providers"

# Set work directory
WORKDIR /app

# Install additional dependencies if needed
RUN pip install --no-cache-dir \
    prometheus-client==0.17.1 \
    presidio-analyzer==2.2.33 \
    presidio-anonymizer==2.2.33 \
    redis==4.6.0

# Copy configuration files
COPY config.yml /app/config.yml
COPY scripts/entrypoint.sh /app/entrypoint.sh

# Create directory for logs
RUN mkdir -p /app/logs && \
    touch /app/logs/litellm.log && \
    chmod -R 755 /app/logs

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=4000

# Expose port
EXPOSE 4000/tcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:4000/health || exit 1

# Set user to non-root for better security
# Uncomment if the base image supports it
# RUN adduser --disabled-password --gecos "" appuser
# USER appuser

# Define entrypoint and default command
ENTRYPOINT ["/app/entrypoint.sh"]

# Production command (default)
CMD ["--port", "4000", "--config", "config.yml"]

# For debugging, override with: 
# CMD ["--port", "4000", "--config", "config.yml", "--detailed_debug"]