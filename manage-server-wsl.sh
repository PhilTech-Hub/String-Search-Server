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
