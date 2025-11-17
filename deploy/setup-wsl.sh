#!/bin/bash
#
# WSL Setup script for String Search Server
# Usage: ./deploy/setup-wsl.sh

set -e

echo "=================================================="
echo "String Search Server - WSL Setup"
echo "=================================================="

PROJECT_DIR="$(pwd)"
echo "📁 Project directory: $PROJECT_DIR"

# Create WSL-specific management script in the current project
echo "🔧 Creating WSL management scripts..."

# Create main startup script
cat > "start-server-wsl.sh" << 'STARTEOF'
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
STARTEOF

chmod +x "start-server-wsl.sh"

# Create management script
cat > "manage-server-wsl.sh" << 'MANAGEEOF'
#!/bin/bash
#
# String Search Server Management - WSL

show_usage() {
    echo "String Search Server - WSL Management"
    echo "Usage: $0 [start|stop|status|test|info]"
    echo ""
    echo "Commands:"
    echo "  start    - Start server in foreground"
    echo "  stop     - Stop server"
    echo "  status   - Check if server is running"
    echo "  test     - Test server connection"
    echo "  info     - Show server information"
    echo ""
}

check_running() {
    if pgrep -f "python3 -m server.server" > /dev/null; then
        PID=$(pgrep -f "python3 -m server.server")
        echo "✅ Server is running (PID: $PID)"
        echo "🌐 Access: localhost:44445"
        return 0
    else
        echo "❌ Server is not running"
        return 1
    fi
}

case "$1" in
    start)
        echo "🚀 Starting String Search Server..."
        echo "📁 Directory: $(pwd)"
        echo "🔧 Config: config/server_config.conf"
        echo "🌐 Available at: localhost:44445"
        echo ""
        echo "Press Ctrl+C to stop the server"
        echo ""
        exec python3 -m server.server
        ;;
    stop)
        echo "🛑 Stopping String Search Server..."
        if pkill -f "python3 -m server.server"; then
            echo "✅ Server stopped"
        else
            echo "⚠️  No running server found"
        fi
        ;;
    status)
        check_running
        ;;
    test)
        echo "🧪 Testing server..."
        if check_running; then
            echo ""
            echo "Testing with sample search..."
            if [ -f "client/client.py" ]; then
                python3 client/client.py "test_string_123"
            else
                echo "📝 Manual test: Connect to localhost:44445 and send: test_string_123"
            fi
        else
            echo "❌ Server not running. Start with: $0 start"
        fi
        ;;
    info)
        echo "🔍 String Search Server Information"
        echo "==================================="
        echo "Project: $(pwd)"
        echo "Python: $(python3 --version)"
        echo "Config: config/server_config.conf"
        echo "Data: data/200k.txt"
        echo ""
        check_running
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
MANAGEEOF

chmod +x "manage-server-wsl.sh"

# Create a simple data file if it doesn't exist
if [ ! -f "data/200k.txt" ]; then
    echo "📝 Creating sample data file..."
    mkdir -p data
    cat > "data/200k.txt" << 'DATAEOF'
sample_line_1
sample_line_2
test_string_123
hello_world
search_me
wsl_deployment_test
DATAEOF
fi

# Update config for WSL if needed
if [ -f "config/server_config.conf" ]; then
    echo "⚙️  Current configuration: config/server_config.conf"
    echo "   (Using existing configuration)"
else
    echo "⚙️  Creating default configuration..."
    mkdir -p config
    cat > "config/server_config.conf" << 'CONFIGEOF'
host=0.0.0.0
port=44445
linuxpath=data/200k.txt
REREAD_ON_QUERY=False
SSL_ENABLED=False
CONFIGEOF
fi

echo ""
echo "=================================================="
echo "✅ WSL Setup Completed Successfully!"
echo "=================================================="
echo ""
echo "🚀 Quick Start:"
echo "   ./manage-server-wsl.sh start"
echo ""
echo "🔧 Management Commands:"
echo "   ./manage-server-wsl.sh start     # Start server"
echo "   ./manage-server-wsl.sh status    # Check status"
echo "   ./manage-server-wsl.sh stop      # Stop server"
echo "   ./manage-server-wsl.sh test      # Test connection"
echo "   ./manage-server-wsl.sh info      # Show info"
echo ""
echo "🌐 Server Access:"
echo "   From WSL: localhost:44445"
echo "   From Windows: 127.0.0.1:44445"
echo ""
echo "📝 Usage:"
echo "   1. Start server: ./manage-server-wsl.sh start"
echo "   2. In another terminal, test: ./manage-server-wsl.sh test"
echo "   3. Or use client: python3 client/client.py 'search_string'"
echo ""
