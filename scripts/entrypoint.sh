#!/bin/bash
set -e

# Function to validate environment variables
validate_env() {
  # Check required variables
  if [ -z "${MASTER_KEY}" ]; then
    echo "ERROR: MASTER_KEY environment variable is required"
    exit 1
  fi
  
  # Warn about missing API keys
  if [ -z "${ANTHROPIC_API_KEY}" ] && [ -z "${OPENAI_API_KEY}" ] && \
     [ -z "${DEEPSEEK_API_KEY}" ] && [ -z "${CODESTRAL_API_KEY}" ] && \
     [ -z "${GROQ_API_KEY}" ] && [ -z "${OPENROUTER_API_KEY}" ]; then
    echo "WARNING: No API keys provided. At least one provider API key is recommended."
  fi
  
  # Check database connection
  if [ -z "${DATABASE_URL}" ]; then
    echo "WARNING: DATABASE_URL not set, using default configuration"
  fi
  
  echo "Environment validation complete"
}

# Function to check if config file exists
check_config() {
  CONFIG_PATH="/app/config.yml"
  if [ ! -f "$CONFIG_PATH" ]; then
    echo "ERROR: Config file not found at $CONFIG_PATH"
    exit 1
  fi
  echo "Config file found at $CONFIG_PATH"
}

# Function to wait for database
wait_for_db() {
  if [ -n "${DATABASE_URL}" ]; then
    echo "Waiting for database to be ready..."
    
    # Extract host and port from DATABASE_URL
    if [[ $DATABASE_URL =~ ://[^:]+:([^@]+)@([^:]+):([0-9]+)/([^?]+) ]]; then
      DB_HOST="${BASH_REMATCH[2]}"
      DB_PORT="${BASH_REMATCH[3]}"
      
      # Wait for database connection
      RETRIES=10
      until nc -z $DB_HOST $DB_PORT || [ $RETRIES -eq 0 ]; do
        echo "Waiting for database at $DB_HOST:$DB_PORT, $RETRIES remaining attempts..."
        RETRIES=$((RETRIES-1))
        sleep 5
      done
      
      if [ $RETRIES -eq 0 ]; then
        echo "ERROR: Failed to connect to database after multiple attempts"
        exit 1
      fi
      
      echo "Database is ready!"
    else
      echo "WARNING: Could not parse DATABASE_URL, skipping database connection check"
    fi
  fi
}

# Main execution
echo "Starting LiteLLM Proxy..."
validate_env
check_config
wait_for_db

echo "Launching LiteLLM with arguments: $@"
exec litellm "$@"