#!/bin/bash
# Start Backend API with proper cache configuration

echo "🚀 Starting Backend API Server..."
echo ""

# Set Python cache prefix to target/pycache
export PYTHONPYCACHEPREFIX=target/pycache

# Load environment variables from .env
if [ -f .env ]; then
    echo "✅ Loading .env configuration..."
    export $(grep -v '^#' .env | xargs)
else
    echo "⚠️  Warning: .env file not found"
fi

# Default values
API_HOST=${API_HOST:-0.0.0.0}
API_PORT=${API_PORT:-8000}

echo ""
echo "📦 Cache directory: $PYTHONPYCACHEPREFIX"
echo "🌐 API will run on: http://$API_HOST:$API_PORT"
echo ""

# Start uvicorn
python -m uvicorn app.main:app --host "$API_HOST" --port "$API_PORT" --reload
