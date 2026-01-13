#!/usr/bin/env bash
# ============================================================================
# Environment Variable Validation Script for Cerebro-Red v2
# ============================================================================
# Validates .env files for completeness, format, and common misconfigurations
# Usage: ./scripts/validate_env.sh [env_file]
# ============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0
CHECKS=0

# Default .env file
ENV_FILE="${1:-.env}"

# Print header
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Cerebro-Red v2 - Environment Validation${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Validating: ${BLUE}${ENV_FILE}${NC}"
echo ""

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED} Error: ${ENV_FILE} not found${NC}"
    echo ""
    echo "Please create .env file from template:"
    echo "  cp .env.example .env"
    echo ""
    exit 1
fi

# Function to check if variable is set
check_var() {
    local var_name="$1"
    local var_desc="$2"
    local required="${3:-true}"

    CHECKS=$((CHECKS + 1))

    # Source the env file to get the variable
    set +u
    local var_value=$(grep "^${var_name}=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2- | sed 's/^"//' | sed 's/"$//')
    set -u

    if [ -z "$var_value" ]; then
        if [ "$required" = "true" ]; then
            echo -e "${RED} ${var_name}${NC} - ${var_desc} (REQUIRED)"
            ERRORS=$((ERRORS + 1))
        else
            echo -e "${YELLOW} ${var_name}${NC} - ${var_desc} (optional, not set)"
            WARNINGS=$((WARNINGS + 1))
        fi
        return 1
    else
        echo -e "${GREEN} ${var_name}${NC} - ${var_desc}"
        echo "$var_value"
        return 0
    fi
}

# Function to validate port number
validate_port() {
    local var_name="$1"
    local port_value="$2"

    if ! [[ "$port_value" =~ ^[0-9]+$ ]]; then
        echo -e "${RED} ${var_name}=${port_value}${NC} - Must be a number"
        ERRORS=$((ERRORS + 1))
        return 1
    fi

    if [ "$port_value" -lt 1024 ] || [ "$port_value" -gt 65535 ]; then
        echo -e "${YELLOW} ${var_name}=${port_value}${NC} - Port should be between 1024-65535"
        WARNINGS=$((WARNINGS + 1))
        return 1
    fi

    return 0
}

# Function to validate boolean
validate_boolean() {
    local var_name="$1"
    local bool_value="$2"

    if [[ ! "$bool_value" =~ ^(true|false|True|False|TRUE|FALSE|0|1)$ ]]; then
        echo -e "${RED} ${var_name}=${bool_value}${NC} - Must be true/false"
        ERRORS=$((ERRORS + 1))
        return 1
    fi

    return 0
}

# Function to validate log level
validate_log_level() {
    local var_name="$1"
    local level_value="$2"

    if [[ ! "$level_value" =~ ^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$ ]]; then
        echo -e "${RED} ${var_name}=${level_value}${NC} - Must be DEBUG, INFO, WARNING, ERROR, or CRITICAL"
        ERRORS=$((ERRORS + 1))
        return 1
    fi

    return 0
}

# Function to check for production misconfigurations
check_production_config() {
    local env_value=$(grep "^CEREBRO_ENV=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)

    if [ "$env_value" = "production" ]; then
        echo ""
        echo -e "${BLUE}Production Environment Checks:${NC}"

        # Check DEBUG mode
        local debug_value=$(grep "^CEREBRO_DEBUG=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)
        if [[ "$debug_value" =~ ^(true|True|TRUE|1)$ ]]; then
            echo -e "${RED} CEREBRO_DEBUG=true in production${NC} - Should be false"
            ERRORS=$((ERRORS + 1))
        else
            echo -e "${GREEN} CEREBRO_DEBUG=false${NC}"
        fi

        # Check CORS
        local cors_value=$(grep "^CORS_ORIGINS=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)
        if [ "$cors_value" = "*" ]; then
            echo -e "${RED} CORS_ORIGINS=*${NC} - Wildcard CORS in production is insecure"
            ERRORS=$((ERRORS + 1))
        else
            echo -e "${GREEN} CORS_ORIGINS configured${NC}"
        fi

        # Check API key
        local api_enabled=$(grep "^API_KEY_ENABLED=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)
        local api_key=$(grep "^API_KEY=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)
        if [[ "$api_enabled" =~ ^(true|True|TRUE|1)$ ]] && [ -z "$api_key" ]; then
            echo -e "${RED} API_KEY_ENABLED=true but API_KEY is empty${NC}"
            ERRORS=$((ERRORS + 1))
        else
            echo -e "${GREEN} API authentication configured${NC}"
        fi

        # Check log level
        local log_level=$(grep "^CEREBRO_LOG_LEVEL=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)
        if [ "$log_level" = "DEBUG" ]; then
            echo -e "${YELLOW} CEREBRO_LOG_LEVEL=DEBUG${NC} - Consider INFO or WARNING for production"
            WARNINGS=$((WARNINGS + 1))
        else
            echo -e "${GREEN} CEREBRO_LOG_LEVEL=${log_level}${NC}"
        fi
    fi
}

# Main validation
echo -e "${BLUE}Required Variables:${NC}"
echo ""

# Application Settings
check_var "CEREBRO_ENV" "Application environment" true
check_var "CEREBRO_HOST" "Application host" true
if check_var "CEREBRO_PORT" "Application port" true; then
    cerebro_port=$(grep "^CEREBRO_PORT=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2- | sed 's/^"//' | sed 's/"$//')
    validate_port "CEREBRO_PORT" "$cerebro_port"
fi

# Database
check_var "DATABASE_URL" "Database connection string" true

# LLM Provider
llm_provider=$(check_var "DEFAULT_LLM_PROVIDER" "LLM provider (ollama, openai, azure)" true && grep "^DEFAULT_LLM_PROVIDER=" "$ENV_FILE" | cut -d'=' -f2)

# Provider-specific checks
echo ""
echo -e "${BLUE}LLM Provider Configuration:${NC}"
echo ""

case "$llm_provider" in
    "ollama")
        check_var "OLLAMA_BASE_URL" "Ollama base URL" true
        check_var "OLLAMA_MODEL_ATTACKER" "Ollama attacker model" true
        check_var "OLLAMA_MODEL_TARGET" "Ollama target model" true
        check_var "OLLAMA_MODEL_JUDGE" "Ollama judge model" true
        ;;
    "openai")
        check_var "OPENAI_API_KEY" "OpenAI API key" true
        check_var "OPENAI_MODEL_ATTACKER" "OpenAI attacker model" false
        check_var "OPENAI_MODEL_TARGET" "OpenAI target model" false
        ;;
    "azure")
        check_var "AZURE_OPENAI_API_KEY" "Azure OpenAI API key" true
        check_var "AZURE_OPENAI_ENDPOINT" "Azure OpenAI endpoint" true
        check_var "AZURE_OPENAI_API_VERSION" "Azure OpenAI API version" false
        ;;
    *)
        if [ -n "$llm_provider" ]; then
            echo -e "${YELLOW} Unknown LLM provider: ${llm_provider}${NC}"
            WARNINGS=$((WARNINGS + 1))
        fi
        ;;
esac

# Optional but recommended
echo ""
echo -e "${BLUE}Optional Configuration:${NC}"
echo ""

check_var "API_KEY_ENABLED" "API key authentication" false
check_var "RATE_LIMIT_ENABLED" "Rate limiting" false
check_var "MAX_CONCURRENT_EXPERIMENTS" "Max concurrent experiments" false
check_var "CEREBRO_LOG_LEVEL" "Log level" false

# Production-specific checks
check_production_config

# Summary
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Validation Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Total checks: ${CHECKS}"
echo -e "${GREEN} Passed: $((CHECKS - ERRORS - WARNINGS))${NC}"

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW} Warnings: ${WARNINGS}${NC}"
fi

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED} Errors: ${ERRORS}${NC}"
    echo ""
    echo "Please fix the errors above and try again."
    echo ""
    exit 1
else
    echo ""
    echo -e "${GREEN} Environment validation passed!${NC}"
    echo ""
    exit 0
fi
