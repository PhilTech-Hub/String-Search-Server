#!/bin/bash
#
# Installation script for String Search Server Linux Daemon
# Usage: sudo ./deploy/install.sh

set -e

echo "=================================================="
echo "String Search Server Linux Daemon Installation"
echo "=================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo $0"
    exit 1
fi

# Fix any broken packages first
echo "🔧 Checking system health..."
apt --fix-broken install -y >/dev/null 2>&1 || true

# Check Python availability
echo "🔍 Checking Python..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python3 not found. Installing..."
    apt update && apt install -y python3
fi

SERVER_USER="stringserver"
INSTALL_DIR="/opt/string_search_server"
SERVICE_FILE="string-search-server.service"
CONFIG_DIR="/etc/string_search_server"

echo "📦 Starting installation..."

# Create system user if doesn't exist
if ! id "$SERVER_USER" &>/dev/null; then
    echo "👤 Creating system user: $SERVER_USER"
    useradd --system --shell /bin/false --home-dir "$INSTALL_DIR" "$SERVER_USER"
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/data"
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/config"
mkdir -p "$CONFIG_DIR"

# Copy application files
echo "📄 Copying application files..."
cp -r server/ "$INSTALL_DIR/"
cp -r client/ "$INSTALL_DIR/" 2>/dev/null || true
cp requirements.txt "$INSTALL_DIR/"
cp README.md "$INSTALL_DIR/" 2>/dev/null || true
cp DEPLOYMENT.md "$INSTALL_DIR/" 2>/dev/null || true

# Create production configuration file
echo "⚙️  Creating production configuration..."
cat > "$INSTALL_DIR/config/server_config.conf" << 'EOF'
# =======================================================
# Production Configuration for String Search Server
# =======================================================

# -----------------------------
# Server network configuration
# -----------------------------
host=0.0.0.0
port=44445                 

# -----------------------------
# File handling
# -----------------------------
linuxpath=/opt/string_search_server/data/200k.txt    
REREAD_ON_QUERY=False         

# -----------------------------
# SSL configuration (optional)
# -----------------------------
SSL_ENABLED=False            
CERTFILE=config/cert.pem
KEYFILE=config/key.pem     
CAFILE=config/ca.pem    
PSK=supersecretkey123

# -----------------------------
# Performance settings
# -----------------------------
max_connections=1000
timeout=30
EOF

# Copy SSL certificates if they exist
if [ -f "config/cert.pem" ]; then
    echo "🔐 Copying SSL certificates..."
    cp config/cert.pem "$INSTALL_DIR/config/" 2>/dev/null || true
    cp config/key.pem "$INSTALL_DIR/config/" 2>/dev/null || true
    cp config/ca.pem "$INSTALL_DIR/config/" 2>/dev/null || true
fi

# Install Python dependencies - GRACEFUL APPROACH
echo "🐍 Setting up Python dependencies..."
if python3 -c "import pandas, matplotlib, reportlab" 2>/dev/null; then
    echo "✅ Required Python packages already installed"
else
    echo "📦 Attempting to install Python packages..."
    
    # Try pip3 first
    if command -v pip3 >/dev/null 2>&1; then
        echo "   Using pip3 to install dependencies..."
        pip3 install pandas matplotlib reportlab >/dev/null 2>&1 || {
            echo "⚠️  pip3 installation failed, trying alternative approach..."
        }
    fi
    
    # Try apt packages as alternative
    echo "   Trying system packages..."
    apt update >/dev/null 2>&1
    apt install -y python3-pandas python3-matplotlib python3-reportlab >/dev/null 2>&1 || {
        echo "⚠️  System package installation also failed"
        echo "📝 Note: Dependencies will need to be installed manually"
    }
fi

# Verify critical dependencies
echo "🔍 Verifying critical dependencies..."
if ! python3 -c "import socket, threading, ssl" 2>/dev/null; then
    echo "❌ Critical Python modules missing. Installing python3-full..."
    apt install -y python3-full
fi

# Create sample data file if it doesn't exist
if [ ! -f "$INSTALL_DIR/data/200k.txt" ]; then
    echo "📝 Creating sample data file..."
    cat > "$INSTALL_DIR/data/200k.txt" << 'DATAEOF'
sample_line_1
sample_line_2
test_string_123
hello_world
search_me
DATAEOF
    echo "   Created sample data with 5 test lines"
    echo "   Remember to replace with your actual 200k.txt file"
fi

# Set permissions
echo "🔐 Setting permissions..."
chown -R "$SERVER_USER:$SERVER_USER" "$INSTALL_DIR"
chmod 755 "$INSTALL_DIR"
chmod 644 "$INSTALL_DIR/config/"*
find "$INSTALL_DIR/server" -name "*.py" -exec chmod 644 {} \;
chmod 644 "$INSTALL_DIR/data/"*

# Install systemd service
echo "🔧 Installing systemd service..."
cp "deploy/$SERVICE_FILE" /etc/systemd/system/

# Reload systemd and enable service
echo "🔄 Configuring systemd..."
systemctl daemon-reload
systemctl enable "$SERVICE_FILE"

echo ""
echo "=================================================="
echo "✅ Installation Completed Successfully!"
echo "=================================================="
echo ""
echo "📋 Next steps:"
echo "   1. Add your 200k.txt file:"
echo "      sudo cp /path/to/your/200k.txt $INSTALL_DIR/data/"
echo "   2. Install missing dependencies if any:"
echo "      sudo apt install python3-pip python3-pandas python3-matplotlib python3-reportlab"
echo "   3. Start the service:"
echo "      sudo systemctl start string-search-server"
echo "   4. Check status:"
echo "      sudo systemctl status string-search-server"
echo ""
echo "🔧 Useful commands:"
echo "   Start:    sudo systemctl start string-search-server"
echo "   Stop:     sudo systemctl stop string-search-server"
echo "   Status:   sudo systemctl status string-search-server"
echo "   Logs:     sudo journalctl -u string-search-server -f"
echo ""