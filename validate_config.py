#!/usr/bin/env python3
"""
LiteLLM Configuration Validator

This script validates your LiteLLM configuration before deployment.
Run it to check for common issues in your setup.
"""

import os
import sys
import yaml
import dotenv
import requests
import argparse
from typing import Dict, List, Any, Optional

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message: str, status: str, color: str) -> None:
    """Print a formatted status message"""
    print(f"{message.ljust(60)} [{color}{status}{Colors.ENDC}]")

def load_env_file(env_file: str = '.env') -> Dict[str, str]:
    """Load environment variables from .env file"""
    if not os.path.exists(env_file):
        print(f"{Colors.WARNING}Warning: {env_file} file not found{Colors.ENDC}")
        return {}
    
    dotenv.load_dotenv(env_file)
    return {key: val for key, val in os.environ.items()}

def validate_env_variables(env_vars: Dict[str, str]) -> List[str]:
    """Validate required environment variables"""
    errors = []
    
    # Check for required variables
    if not env_vars.get('MASTER_KEY'):
        errors.append("MASTER_KEY is required but not set")
    
    # Check for API keys
    api_keys = ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'DEEPSEEK_API_KEY', 
                'CODESTRAL_API_KEY', 'GROQ_API_KEY', 'OPENROUTER_API_KEY']
    
    if not any(env_vars.get(key) for key in api_keys):
        errors.append("No API keys set. At least one provider API key is required")
    
    # Check database configuration
    if 'DB_PASSWORD' in env_vars and len(env_vars['DB_PASSWORD']) < 10:
        errors.append("DB_PASSWORD should be at least 10 characters long for security")
    
    return errors

def load_config_file(config_file: str = 'config.yml') -> Optional[Dict[str, Any]]:
    """Load and parse the config YAML file"""
    if not os.path.exists(config_file):
        print(f"{Colors.FAIL}Error: {config_file} not found{Colors.ENDC}")
        return None
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            return config
    except yaml.YAMLError as e:
        print(f"{Colors.FAIL}Error parsing {config_file}: {e}{Colors.ENDC}")
        return None
    except Exception as e:
        print(f"{Colors.FAIL}Error reading {config_file}: {e}{Colors.ENDC}")
        return None

def validate_config(config: Dict[str, Any], env_vars: Dict[str, str]) -> List[str]:
    """Validate the configuration file"""
    errors = []
    
    # Check model list
    if not config.get('model_list'):
        errors.append("No models defined in configuration")
    else:
        # Check each model configuration
        for idx, model in enumerate(config['model_list']):
            model_name = model.get('model_name', f"Model #{idx+1}")
            
            if not model.get('litellm_params', {}).get('model'):
                errors.append(f"Model '{model_name}' is missing required 'model' parameter")
            
            api_key_ref = model.get('litellm_params', {}).get('api_key', '')
            if isinstance(api_key_ref, str) and api_key_ref.startswith('os.environ/'):
                env_key = api_key_ref.replace('os.environ/', '')
                if not env_vars.get(env_key):
                    errors.append(f"Model '{model_name}' references undefined environment variable '{env_key}'")
    
    # Check general settings
    if 'general_settings' in config:
        master_key_ref = config['general_settings'].get('master_key', '')
        if isinstance(master_key_ref, str) and master_key_ref.startswith('os.environ/'):
            env_key = master_key_ref.replace('os.environ/', '')
            if not env_vars.get(env_key):
                errors.append(f"Master key references undefined environment variable '{env_key}'")
    
    return errors

def test_api_keys(env_vars: Dict[str, str]) -> Dict[str, bool]:
    """Test API keys by making simple requests to provider endpoints"""
    results = {}
    
    # Test Anthropic
    if env_vars.get('ANTHROPIC_API_KEY'):
        try:
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': env_vars['ANTHROPIC_API_KEY'],
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json'
                },
                json={
                    'model': 'claude-3-haiku-20240307',
                    'max_tokens': 1,
                    'messages': [{'role': 'user', 'content': 'Hello'}]
                },
                timeout=5
            )
            results['anthropic'] = response.status_code == 200 or response.status_code == 400
        except Exception:
            results['anthropic'] = False
    
    # Test OpenAI
    if env_vars.get('OPENAI_API_KEY'):
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f"Bearer {env_vars['OPENAI_API_KEY']}",
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-3.5-turbo',
                    'max_tokens': 1,
                    'messages': [{'role': 'user', 'content': 'Hello'}]
                },
                timeout=5
            )
            results['openai'] = response.status_code == 200 or response.status_code == 400
        except Exception:
            results['openai'] = False
    
    # Test Groq
    if env_vars.get('GROQ_API_KEY'):
        try:
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={
                    'Authorization': f"Bearer {env_vars['GROQ_API_KEY']}",
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'llama-3.1-8b-instant',
                    'max_tokens': 1,
                    'messages': [{'role': 'user', 'content': 'Hello'}]
                },
                timeout=5
            )
            results['groq'] = response.status_code == 200 or response.status_code == 400
        except Exception:
            results['groq'] = False
            
    # Check other API keys similarly
    # For brevity, we'll just mark the rest as untested rather than implement all tests
    for key in ['DEEPSEEK_API_KEY', 'CODESTRAL_API_KEY', 'OPENROUTER_API_KEY']:
        if env_vars.get(key):
            provider = key.split('_')[0].lower()
            results[provider] = "untested"
            
    return results

def main():
    """Main function to validate configuration"""
    parser = argparse.ArgumentParser(description='Validate LiteLLM configuration')
    parser.add_argument('--env', default='.env', help='Path to .env file')
    parser.add_argument('--config', default='config.yml', help='Path to config.yml file')
    parser.add_argument('--test-api', action='store_true', help='Test API key validity')
    args = parser.parse_args()

    print(f"{Colors.HEADER}{Colors.BOLD}LiteLLM Configuration Validator{Colors.ENDC}")
    print(f"{Colors.BOLD}==============================={Colors.ENDC}\n")

    # Load and validate environment variables
    print(f"{Colors.BOLD}Checking environment variables...{Colors.ENDC}")
    env_vars = load_env_file(args.env)
    env_errors = validate_env_variables(env_vars)
    
    if not env_errors:
        print_status("Environment variables", "PASSED", Colors.OKGREEN)
    else:
        print_status("Environment variables", "FAILED", Colors.FAIL)
        for error in env_errors:
            print(f" - {Colors.FAIL}{error}{Colors.ENDC}")

    # Load and validate config file
    print(f"\n{Colors.BOLD}Checking configuration file...{Colors.ENDC}")
    config = load_config_file(args.config)
    
    if config:
        config_errors = validate_config(config, env_vars)
        if not config_errors:
            print_status("Configuration file", "PASSED", Colors.OKGREEN)
        else:
            print_status("Configuration file", "FAILED", Colors.FAIL)
            for error in config_errors:
                print(f" - {Colors.FAIL}{error}{Colors.ENDC}")
    else:
        print_status("Configuration file", "NOT FOUND", Colors.FAIL)

    # Test API keys if requested
    if args.test_api:
        print(f"\n{Colors.BOLD}Testing API keys...{Colors.ENDC}")
        key_results = test_api_keys(env_vars)
        
        for provider, status in key_results.items():
            if status is True:
                print_status(f"{provider.upper()} API key", "VALID", Colors.OKGREEN)
            elif status is False:
                print_status(f"{provider.upper()} API key", "INVALID", Colors.FAIL)
            else:
                print_status(f"{provider.upper()} API key", "UNTESTED", Colors.WARNING)

    # Summary
    all_errors = env_errors + (config_errors if config else ["Config file not found"])
    if not all_errors:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ All checks passed! Your configuration looks valid.{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}✗ Found {len(all_errors)} issues with your configuration.{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()