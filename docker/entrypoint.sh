#!/bin/bash
set -e

echo "🚀 CEREBRO-RED v2 Backend Entrypoint"
echo "======================================"

# Fix permissions for data directories
echo "📁 Setting up directories..."

# Create directories if they don't exist
mkdir -p /tmp/audit_logs /app/data/experiments /app/data/results 2>/dev/null || true

# Ensure directories are writable (running as root now, so this should work)
chmod -R 777 /tmp/audit_logs 2>/dev/null || true
chmod -R 777 /app/data 2>/dev/null || true

# Touch database file to ensure it exists with correct permissions
touch /tmp/cerebro.db 2>/dev/null || true
chmod 666 /tmp/cerebro.db 2>/dev/null || true

echo "✅ Directories ready"

# Print environment for debugging
echo ""
echo "🔧 Environment Configuration:"
echo "   OLLAMA_API_BASE: ${OLLAMA_API_BASE:-not set}"
echo "   OLLAMA_BASE_URL: ${OLLAMA_BASE_URL:-not set}"
echo "   OLLAMA_HOST: ${OLLAMA_HOST:-not set}"
echo "   CEREBRO_PORT: ${CEREBRO_PORT:-9000}"
echo "   CEREBRO_VERBOSITY: ${CEREBRO_VERBOSITY:-2}"
echo "   Current User: $(whoami)"
echo ""

# Test Ollama connectivity
echo "🔍 Testing Ollama connectivity..."
if curl -s --connect-timeout 5 "${OLLAMA_API_BASE:-http://host.docker.internal:11434}/api/tags" > /dev/null 2>&1; then
    echo "✅ Ollama is reachable at ${OLLAMA_API_BASE:-http://host.docker.internal:11434}"
    # Show available models
    echo "📋 Available Ollama models:"
    curl -s "${OLLAMA_API_BASE:-http://host.docker.internal:11434}/api/tags" | python3 -c "import sys,json; d=json.load(sys.stdin); print('   ' + '\n   '.join(m['name'] for m in d.get('models',[])) if d.get('models') else '   (no models)')" 2>/dev/null || echo "   (could not list models)"
else
    echo "⚠️  WARNING: Cannot reach Ollama at ${OLLAMA_API_BASE:-http://host.docker.internal:11434}"
    echo "   Make sure Ollama is running on the host and the URL is correct"
fi
echo ""

# Start application directly (no user switch to avoid cap_drop issues)
echo "🏃 Starting application..."
exec "$@"
