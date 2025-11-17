#!/bin/bash
#
# Management script for String Search Server
# Usage: ./deploy/manage-server.sh [start|stop|restart|status|logs|enable|disable|config|info]

SERVICE_NAME="string-search-server"
INSTALL_DIR="/opt/string_search_server"
CONFIG_FILE="$INSTALL_DIR/config/server_config.conf"

show_usage() {
    echo "Usage: $0 [start|stop|restart|status|logs|enable|disable|config|info]"
    echo ""
    echo "Commands:"
    echo "  start    - Start the service"
    echo "  stop     - Stop the service"
    echo "  restart  - Restart the service"
    echo "  status   - Show service status"
    echo "  logs     - Follow service logs"
    echo "  enable   - Enable service to start on boot"
    echo "  disable  - Disable service from starting on boot"
    echo "  config   - Show current configuration"
    echo "  info     - Show service information"
    echo ""
}

check_installed() {
    if [ ! -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
        echo "❌ Service not installed. Run: sudo ./deploy/install.sh"
        exit 1
    fi
}

show_info() {
    echo "🔍 Service Information:"
    echo "========================"
    echo "Service Name: $SERVICE_NAME"
    echo "Install Directory: $INSTALL_DIR"
    echo "Config File: $CONFIG_FILE"
    echo "Service User: stringserver"
    echo ""
    
    if [ -f "$CONFIG_FILE" ]; then
        echo "📄 Current Configuration:"
        grep -E '^(host|port|linuxpath|REREAD_ON_QUERY|SSL_ENABLED)=' "$CONFIG_FILE" | while read line; do
            echo "   $line"
        done
    else
        echo "⚠️  Configuration file not found: $CONFIG_FILE"
    fi
}

show_config() {
    if [ -f "$CONFIG_FILE" ]; then
        echo "📄 Current Configuration ($CONFIG_FILE):"
        echo "========================================"
        cat "$CONFIG_FILE"
    else
        echo "❌ Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
}

case "$1" in
    start)
        echo "🚀 Starting $SERVICE_NAME..."
        check_installed
        sudo systemctl start "$SERVICE_NAME"
        sleep 2
        sudo systemctl status "$SERVICE_NAME" --no-pager -l
        ;;
    stop)
        echo "🛑 Stopping $SERVICE_NAME..."
        check_installed
        sudo systemctl stop "$SERVICE_NAME"
        echo "✅ Service stopped"
        ;;
    restart)
        echo "🔄 Restarting $SERVICE_NAME..."
        check_installed
        sudo systemctl restart "$SERVICE_NAME"
        sleep 2
        sudo systemctl status "$SERVICE_NAME" --no-pager -l
        ;;
    status)
        echo "📊 Status of $SERVICE_NAME:"
        check_installed
        sudo systemctl status "$SERVICE_NAME" --no-pager -l
        ;;
    logs)
        echo "📋 Showing logs for $SERVICE_NAME (Ctrl+C to exit):"
        check_installed
        sudo journalctl -u "$SERVICE_NAME" -f
        ;;
    enable)
        echo "✅ Enabling $SERVICE_NAME to start on boot..."
        check_installed
        sudo systemctl enable "$SERVICE_NAME"
        ;;
    disable)
        echo "❌ Disabling $SERVICE_NAME from starting on boot..."
        check_installed
        sudo systemctl disable "$SERVICE_NAME"
        ;;
    config)
        show_config
        ;;
    info)
        show_info
        ;;
    *)
        show_usage
        exit 1
        ;;
esac