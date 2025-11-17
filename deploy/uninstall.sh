#!/bin/bash
#
# Uninstallation script for String Search Server Linux Daemon
# Usage: sudo ./deploy/uninstall.sh

set -e

echo "=================================================="
echo "String Search Server Linux Daemon Uninstallation"
echo "=================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo $0"
    exit 1
fi

SERVER_USER="stringserver"
INSTALL_DIR="/opt/string_search_server"
SERVICE_FILE="string-search-server.service"

echo "🗑️  Starting uninstallation..."

# Stop and disable service
echo "🛑 Stopping service..."
systemctl stop "$SERVICE_FILE" 2>/dev/null || true
systemctl disable "$SERVICE_FILE" 2>/dev/null || true

# Remove systemd service
echo "🔧 Removing systemd service..."
rm -f "/etc/systemd/system/$SERVICE_FILE"
systemctl daemon-reload
systemctl reset-failed

# Remove application files
echo "📁 Removing application files..."
rm -rf "$INSTALL_DIR"

# Remove configuration directory
echo "⚙️  Removing configuration..."
rm -rf "/etc/string_search_server"

# Remove user if exists and no other processes
if id "$SERVER_USER" &>/dev/null; then
    echo "👤 Checking if we can remove user: $SERVER_USER"
    if ! pgrep -u "$SERVER_USER" > /dev/null 2>&1; then
        userdel "$SERVER_USER" 2>/dev/null || true
        echo "   User $SERVER_USER removed"
    else
        echo "   ⚠️  User $SERVER_USER has running processes, skipping removal"
    fi
fi

echo ""
echo "=================================================="
echo "✅ Uninstallation Completed Successfully!"
echo "=================================================="
echo ""
echo "📝 Summary of removed items:"
echo "   - Service: /etc/systemd/system/$SERVICE_FILE"
echo "   - Application: $INSTALL_DIR"
echo "   - Configuration: /etc/string_search_server"
echo "   - User: $SERVER_USER (if no running processes)"
echo ""
echo "🔍 To verify:"
echo "   systemctl status string-search-server  # Should show 'not found'"
echo "   ls $INSTALL_DIR  # Should show 'No such file or directory'"
echo ""