#!/bin/bash
#
# String Search Server - WSL Startup

echo "🚀 Starting String Search Server in WSL..."
echo "📁 Directory: $(pwd)"
echo "🔧 Config: config/server_config.conf"
echo "🌐 Server will be available at: localhost:44445"
echo ""

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python3 not found"
    exit 1
fi

# Start the server
echo "✅ Starting server..."
exec python3 -m server.server
