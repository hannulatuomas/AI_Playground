# Configuration Best Practices

## Overview

This document describes configuration best practices for the AI Agent Console, including common issues and their solutions.

## Recent Configuration Fixes

### Issue 1: Fallback Provider Validation Error

**Error Message:**
```
Primary, fallback, and secondary fallback providers must be different
```

**Cause:**
The configuration validation requires that all three provider settings (`primary_provider`, `fallback_provider`, and `secondary_fallback_provider`) must have different values when fallback is enabled. The default value for `secondary_fallback_provider` is "openai", which conflicts if you also set `fallback_provider` to "openai".

**Solution:**
Explicitly set `secondary_fallback_provider` in your config.yaml:

```yaml
fallback:
  enabled: true
  primary_provider: "ollama"
  fallback_provider: "openai"
  secondary_fallback_provider: null  # Set to null to disable third-tier fallback
```

**Alternative Solutions:**
- Set `secondary_fallback_provider` to a different provider (e.g., "llamacpp")
- Disable fallback entirely by setting `enabled: false`

### Issue 2: OpenAI API Key Validation Warning

**Warning Message:**
```
OpenAI base_url is set but api_key is missing
```

**Cause:**
The OpenAI configuration has a `base_url` specified but the `api_key` is missing or empty. This triggers a warning because having a base URL without an API key suggests incomplete configuration.

**Solution:**
Set the `api_key` to `null` instead of an empty string:

```yaml
openai:
  api_key: null  # Use null instead of ""
  base_url: "https://api.openai.com/v1"
```

**Alternative Solutions:**
- Provide an actual OpenAI API key
- Remove the `base_url` if not using OpenAI
- Set the API key via environment variable: `export AI_AGENT_OPENAI__API_KEY="sk-..."`

## Configuration Best Practices

### 1. API Keys and Secrets

**DO:**
- Set API keys to `null` when not configured
- Use environment variables for sensitive values
- Add API keys to `.gitignore` if using separate config files

```yaml
openai:
  api_key: null  # Will be overridden by AI_AGENT_OPENAI__API_KEY env var
```

**DON'T:**
- Use empty strings `""` for missing API keys
- Commit API keys to version control
- Store API keys in plain text in config files

### 2. Provider Fallback Configuration

**DO:**
- Explicitly define all three fallback levels if using multiple providers
- Set unused fallback levels to `null`
- Use different providers for each fallback level

```yaml
fallback:
  enabled: true
  primary_provider: "ollama"       # Local LLM
  fallback_provider: "openai"       # Cloud API
  secondary_fallback_provider: null # Disabled
```

**DON'T:**
- Rely on default values for fallback providers
- Use the same provider for multiple fallback levels
- Leave fallback enabled with incomplete configuration

### 3. Model Configuration

**DO:**
- Specify models that are actually available
- Use appropriate models for agent complexity
- Consider performance vs. quality trade-offs

```yaml
models:
  ollama_default: "llama3.3"  # Use installed models
  openai_default: "gpt-3.5-turbo"  # Cost-effective choice
  temperature: 0.7  # Balanced creativity
```

**DON'T:**
- Specify models that aren't downloaded/available
- Use oversized models for simple tasks
- Set temperature to extremes without testing

### 4. Environment Variable Overrides

**DO:**
- Use environment variables for deployment-specific settings
- Follow the naming convention: `AI_AGENT_SECTION__KEY`
- Document required environment variables

```bash
# Override OpenAI API key
export AI_AGENT_OPENAI__API_KEY="sk-..."

# Override Ollama host
export AI_AGENT_OLLAMA__HOST="http://192.168.1.100"

# Override logging level
export AI_AGENT_LOGGING__LEVEL="DEBUG"
```

**DON'T:**
- Override core structural settings via environment variables
- Use environment variables for settings that rarely change
- Forget to document environment variable requirements

## Testing Your Configuration

### Validate Configuration

Test your configuration file:

```bash
python main.py config --show
```

This will:
- Load the configuration
- Validate all settings
- Display the complete configuration
- Show any warnings or errors

### Common Validation Checks

1. **Provider Validation**: Ensures fallback providers are different
2. **API Key Validation**: Warns if base_url is set without api_key
3. **Model Name Validation**: Ensures model names are not empty
4. **Path Validation**: Checks that paths are valid
5. **Range Validation**: Ensures numeric values are within acceptable ranges

## Troubleshooting

### Configuration Won't Load

**Symptoms:**
- Application exits with validation error
- Configuration error messages in output

**Solutions:**
1. Check YAML syntax (indentation, colons, quotes)
2. Validate required fields are present
3. Ensure fallback providers are all different
4. Set API keys to `null` if not using them
5. Run `python main.py config --show` to see specific errors

### Warning Messages

**Symptoms:**
- Configuration loads but shows warnings
- Application works but displays notices

**Solutions:**
- Warnings are informational and don't prevent operation
- Address warnings by providing missing configuration
- Use environment variables for sensitive values
- Set unused optional fields to `null`

## Migration from Legacy TOML Format

If migrating from legacy `config.toml` to `config.yaml`:

1. **Syntax Changes:**
   - `[section]` → `section:`
   - `key = value` → `key: value`
   - `['item1', 'item2']` → `- item1` / `- item2`

2. **Value Changes:**
   - Empty strings `""` → `null` for missing values
   - Boolean values: same in both formats

3. **Structure:**
   - Indentation matters in YAML (use 2 spaces)
   - Comments use `#` in both formats
   - Strings can be unquoted in YAML (unless special characters)

## Example: Complete Fallback Configuration

```yaml
# Proper fallback configuration with all three levels
fallback:
  # Enable automatic fallback
  enabled: true
  
  # Primary provider (first choice)
  primary_provider: "ollama"
  
  # Fallback provider (second choice)
  fallback_provider: "openai"
  
  # Secondary fallback provider (third choice)
  # Set to null to disable third-tier fallback
  secondary_fallback_provider: null
```

## Example: OpenAI Configuration

```yaml
# Proper OpenAI configuration
openai:
  # Use null for missing API keys, not empty strings
  api_key: null
  
  # Base URL for OpenAI or compatible services
  base_url: "https://api.openai.com/v1"
  
  # Request timeout
  timeout: 120
  
  # Token limit (null = use model default)
  max_tokens: null
```

## Getting Help

If you continue to experience configuration issues:

1. Check the full configuration with `python main.py config --show`
2. Review error messages for specific validation failures
3. Consult this document for best practices
4. Check the example configurations in the repository
5. Ensure environment variables are properly set

## Summary

- ✅ Use `null` for missing values, not empty strings
- ✅ Explicitly configure all fallback provider levels
- ✅ Test configuration with `python main.py config --show`
- ✅ Use environment variables for sensitive data
- ✅ Follow YAML syntax rules (indentation, colons)
- ❌ Don't commit API keys to version control
- ❌ Don't use the same provider for multiple fallback levels
- ❌ Don't ignore validation warnings
