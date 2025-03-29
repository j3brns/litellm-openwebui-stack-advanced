# RPi Open LLM API Gateway for Home and leisure


## Semi Advanced LiteLLM Proxy with Open WebUI chat front end Docker Based Builder 

### Includes hardening, optimisation, validation, prompt reporting, analytics + Guardrails


![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Docker](https://img.shields.io/badge/docker-powered-blue.svg)
![LiteLLM](https://img.shields.io/badge/LiteLLM-0.11.0-green.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

> _If it all seems too complex - try my simpler  [Bootstrap](Https://github.com/j3brns/litellm-openwebui-bootstrap)_

An start at a robust setup for running Open WebUI with LiteLLM as a backend proxy, providing access to state-of-the-art AI models through a user-friendly interface. This project uses Docker Compose to orchestrate the services and includes a few validation, monitoring, security, and management features to experiment and secure your household AI use ...

## 🚀 Features

- **(kind of) Production-Ready**: Secure, robust configuration with proper error handling and logging
- **Multiple Model Providers**: Support for Anthropic, OpenAI, DeepSeek, Codestral, Groq, and OpenRouter
- **Complete Monitoring of what has been accessed**: Prometheus and Grafana integration for real-time metrics and dashboards
- **User-Friendly Interface**: Nice intuitive UI for interacting with AI models via Open WebUI
- **Centralised Management**: Single point of control for all model access and API keys
- **Security-Focused**: Environment variable management, proper access controls, and credential extraction
- **Robust Database Backend**: PostgreSQL for request tracking, user management, and analytics
- **Configurable Guardrails**: Optional have go at content filtering and PII detection

## 📋 Prerequisites

- Docker and Docker Compose v2+ installed on your system
- API keys for the AI models you plan to use
- 2GB+ RAM and 1+ CPU cores for the server
- At least 5GB of free disk space

## ⚙️ Configuration

### Environment Setup

1. Copy the example environment file and customize it:
   ```bash
   cp example.env .env
   ```

2. Edit the `.env` file with your API keys and configuration settings:
   ```bash
   # Required
   MASTER_KEY='your_secure_master_key'  # Generate a strong random string
   
   # Add your provider API keys
   ANTHROPIC_API_KEY='your_anthropic_key'
   OPENAI_API_KEY='your_openai_key'
   # ... other provider keys
   ```

3. Validate your configuration (requires Python 3.9+):
   ```bash
   pip install -r requirements-dev.txt
   python validate_config.py --test-api
   ```

### Model Configuration

The `config.yml` file defines which models are available through the proxy. Customize this file to add or remove models based on your API key access.

## 🔧 Installation & Usage

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/litellm-proxy-openwebui.git
   cd litellm-proxy-openwebui
   ```

2. Start all services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Access the interfaces:
   - Open WebUI: [http://localhost:3000](http://localhost:3000)
   - LiteLLM API: [http://localhost:4000/docs](http://localhost:4000/docs)
   - Prometheus: [http://localhost:9090](http://localhost:9090)
   - Grafana: [http://localhost:3001](http://localhost:3001) (default login: admin/admin)

4. Monitor the logs:
   ```bash
   # View all logs
   docker-compose logs -f
   
   # View logs for a specific service
   docker-compose logs -f litellm
   ```

5. Stop all services:
   ```bash
   docker-compose down
   ```

## 🧩 Architecture

| Service    | Port | Description                                         |
|------------|------|-----------------------------------------------------|
| Open WebUI | 3000 | User interface for interacting with AI models       |
| LiteLLM    | 4000 | Backend proxy that handles requests to AI providers |
| PostgreSQL | 5432 | Database for storing request logs and user data     |
| Prometheus | 9090 | Metrics collection and storage                      |
| Grafana    | 3001 | Metrics visualization and dashboards                |

## 🔒 Security Best Practices

- **API Keys**: Store securely in the `.env` file which is excluded from version control
- **Master Key**: Use a strong, unique key for controlling access to your proxy
- **Database Credentials**: Customize the default database password in production
- **Authentication**: Enable `WEBUI_AUTH=True` in production environments
- **Resource Limits**: Container resources are constrained to prevent DoS issues
- **Logging**: Sensitive information is redacted from logs by default
- **Network Isolation**: Services communicate on an isolated Docker network
- **Regular Updates**: Keep your Docker images updated with security patches

## 🔍 Troubleshooting

If you encounter issues:

1. Check the container logs:
   ```bash
   docker-compose logs litellm
   docker-compose logs open-webui
   ```

2. Verify your API keys are correctly set in the `.env` file

3. Use the validation script to check your configuration:
   ```bash
   python validate_config.py --test-api
   ```

4. Check the Prometheus metrics for performance issues:
   ```
   http://localhost:9090/graph
   ```

5. Common issues and solutions:
   - **"API key invalid" errors**: Check your `.env` file and provider account status
   - **Connection timeouts**: Ensure your firewall allows outbound connections
   - **Database errors**: Check PostgreSQL logs with `docker-compose logs db`

## 📊 Monitoring & Analytics

This setup includes comprehensive monitoring:

1. **Prometheus Metrics**: Available at [http://localhost:9090](http://localhost:9090)
   - Request rates, latencies, and error counts
   - System resource usage

2. **Grafana Dashboards**: Available at [http://localhost:3001](http://localhost:3001)
   - Pre-configured dashboards for LiteLLM metrics
   - CPU, memory, and network usage visualization

3. **LiteLLM Internal Metrics**: Available at [http://localhost:4000/metrics](http://localhost:4000/metrics)

## 📦 Advanced Customization

### Adding Custom Models

1. Add your API key to the `.env` file:
   ```
   YOUR_PROVIDER_API_KEY='your_api_key'
   ```

2. Add the model to `config.yml`:
   ```yaml
   - model_name: Your Custom Model
     litellm_params:
       model: provider/model-id
       api_key: os.environ/YOUR_PROVIDER_API_KEY
       timeout: 120
     model_info:
       description: "Your custom model description"
       context_length: 32768
   ```

### Enabling Guardrails

Uncomment and configure the guardrails section in `config.yml`:

```yaml
guardrails:
  - guardrail_name: "pii-filter"
    litellm_params:
      guardrail: presidio
      mode: "pre_call"
      output_parse_pii: True
```

### Custom Routing Strategies

Modify the routing strategy in `config.yml`:

```yaml
routing_strategy:
  lowest_latency:
    num_fallbacks: 2
  lowest_tpm_usage:
    num_fallbacks: 2
```

## 📝 License

This project is distributed under the MIT License. See `LICENSE` file for more information.

## 🙏 Acknowledgements

- [LiteLLM](https://github.com/BerriAI/litellm) - The universal API for LLMs
- [Open WebUI](https://github.com/open-webui/open-webui) - User-friendly interface for AI models
- All the amazing AI model providers that make this possible