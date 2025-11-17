# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                      String Search Server - Linux Daemon Deployment Guide
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 📋 Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Manual Installation](#manual-installation)
- [Service Management](#service-management)
- [Configuration](#configuration)
- [Security Features](#security-features)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)
- [FAQ](#faq)

## Overview

This guide provides complete instructions for deploying the String Search Server as a production-ready Linux daemon using systemd. The deployment includes security hardening, automated installation, and professional service management.

## Quick Start

### One-Command Installation
# Make scripts executable
chmod +x deploy/*.sh

# Install as system service
sudo ./deploy/install.sh

# Start the service
sudo systemctl start string-search-server

# Verify it's running
sudo systemctl status string-search-server

## Service Management (Easy)
# Use the management script (no sudo needed for most commands)
./deploy/manage-server.sh start      # Start service
./deploy/manage-server.sh stop       # Stop service  
./deploy/manage-server.sh status     # Check status
./deploy/manage-server.sh logs       # View real-time logs
./deploy/manage-server.sh restart    # Restart service

## Prerequisites
## System Requirements
OS: Ubuntu 18.04+ or other systemd-based Linux distribution
Python: 3.8 or higher
Permissions: Root/sudo access for installation
Storage: ~100MB free space

## Verify System
# Check Python
python3 --version

# Check systemd
systemctl --version

# Check user (should be root/sudo)
whoami

### Manual Installation
## Step 1: Create System User
sudo useradd --system --shell /bin/false \
    --home-dir /opt/string_search_server \
    --comment "String Search Server Service Account" \
    stringserver

## Step 2: Create Directory Structure
sudo mkdir -p /opt/string_search_server
sudo mkdir -p /opt/string_search_server/{data,logs,config}

## Step 3: Copy Application Files
# Copy server code
sudo cp -r server/ /opt/string_search_server/

# Copy configuration
sudo cp config/server_config.conf /opt/string_search_server/config/
sudo cp config/server.crt /opt/string_search_server/config/ 2>/dev/null || true
sudo cp config/server.key /opt/string_search_server/config/ 2>/dev/null || true

# Copy requirements
sudo cp requirements.txt /opt/string_search_server/

## Step 4: Set Up Python Environment
cd /opt/string_search_server

# Create virtual environment
sudo python3 -m venv venv

# Install dependencies
sudo ./venv/bin/pip install --upgrade pip
sudo ./venv/bin/pip install -r requirements.txt

## Step 5: Install Systemd Service
# Copy service file
sudo cp deploy/string-search-server.service /etc/systemd/system/

# Set permissions
sudo chmod 644 /etc/systemd/system/string-search-server.service

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable string-search-server

## Step 6: Set Permissions
sudo chown -R stringserver:stringserver /opt/string_search_server
sudo chmod 755 /opt/string_search_server
sudo chmod 644 /opt/string_search_server/config/*
sudo find /opt/string_search_server/server -name "*.py" -exec chmod 644 {} \;

### Service Management
## Using Management Script (Recommended)
The deploy/manage-server.sh script provides a user-friendly interface:
# Start the service
./deploy/manage-server.sh start

# Stop the service
./deploy/manage-server.sh stop

# Restart the service (useful after configuration changes)
./deploy/manage-server.sh restart

# Check service status
./deploy/manage-server.sh status

# View real-time logs (Ctrl+C to exit)
./deploy/manage-server.sh logs

# Enable auto-start on boot
./deploy/manage-server.sh enable

# Disable auto-start on boot
./deploy/manage-server.sh disable

### Using Systemctl Directly
# Basic service control
sudo systemctl start string-search-server
sudo systemctl stop string-search-server
sudo systemctl restart string-search-server
sudo systemctl status string-search-server

# Enable/disable auto-start
sudo systemctl enable string-search-server
sudo systemctl disable string-search-server

# Check if enabled
sudo systemctl is-enabled string-search-server

### Log Management
# View all logs
sudo journalctl -u string-search-server

# View recent logs (last 50 lines)
sudo journalctl -u string-search-server -n 50

# Follow logs in real-time
sudo journalctl -u string-search-server -f

# View logs with timestamps
sudo journalctl -u string-search-server --since "1 hour ago"

# View error logs only
sudo journalctl -u string-search-server -p err

## Configuration
# Service Configuration
--> Service File: /etc/systemd/system/string-search-server.service
--> Working Directory: /opt/string_search_server
--> User: stringserver
--> Group: stringserver

## Application Configuration
# Edit the configuration file:
sudo nano /opt/string_search_server/config/server_config.conf
Example configuration:
# File path (update this to your data file location)
linuxpath=/opt/string_search_server/data/200k.txt

# Network settings
port=44445
host=0.0.0.0  # Listen on all interfaces

# Operation mode
REREAD_ON_QUERY=True  

# SSL settings
use_ssl=True
cert_path=config/cert.pem
key_path=config/key.pem

# Performance settings
max_connections=1000
timeout=30

# Data File Setup
# Copy your data file to the server
sudo cp /path/to/your/200k.txt /opt/string_search_server/data/

# Set correct permissions
sudo chown stringserver:stringserver /opt/string_search_server/data/200k.txt
sudo chmod 644 /opt/string_search_server/data/200k.txt

### Security Features
## Service Security
# The daemon runs with enhanced security measures:
Non-root user: Service runs as dedicated stringserver user
File system isolation: Restricted to necessary directories only
Resource limits: Memory and file descriptor limits enforced
No privilege escalation: Service cannot gain elevated privileges
Private temporary files: Isolated from system temp directories

## Network Security
# Verify service is listening only on configured ports
sudo netstat -tlnp | grep stringserver

# Check firewall rules (if using UFW)
sudo ufw status

# Example: Allow specific port
sudo ufw allow 44445/tcp

#### SSL/TLS Configuration (Production)
### For production use with SSL:
## Generate or obtain certificates:
# Self-signed (development)
openssl req -x509 -nodes -newkey rsa:2048 \
  -keyout /opt/string_search_server/config/server.key \
  -out /opt/string_search_server/config/server.crt \
  -days 365 -subj "/CN=localhost"

# Update configuration:
use_ssl=True
cert_path=config/cert.pem
key_path=config/key.pem

# Set proper permissions:
sudo chown stringserver:stringserver /opt/string_search_server/config/server.*
sudo chmod 600 /opt/string_search_server/config/server.key

#### Troubleshooting
### Common Issues and Solutions
## Service Won't Start
# Check service status for error messages
sudo systemctl status string-search-server

# Check systemd logs
sudo journalctl -u string-search-server -n 20

# Verify configuration syntax
sudo systemctl cat string-search-server

## Permission Issues
# Check file ownership
sudo ls -la /opt/string_search_server/

# Fix permissions if needed
sudo chown -R stringserver:stringserver /opt/string_search_server

## Port Already in Use
# Check what's using the port
sudo lsof -i :44445

# Kill the process if necessary
sudo kill -9 <PID>

## Configuration Problems
# Test configuration loading
sudo -u stringserver /opt/string_search_server/venv/bin/python -c "
from server.config import load_config
config = load_config()
print('Config loaded successfully')
print(config)
"

## Diagnostic Commands
# Verify service user exists
id stringserver

# Check disk space
df -h /opt/string_search_server

# Check memory usage
free -h

# Verify Python environment
sudo -u stringserver /opt/string_search_server/venv/bin/python --version

# Test basic server functionality
sudo -u stringserver /opt/string_search_server/venv/bin/python -m server.config

## Log Analysis
# Common log patterns and their meanings:
"Permission denied" - Check file permissions and ownership
"Address already in use" - Port conflict, change port or stop conflicting service
"File not found" - Check data file path in configuration
"Connection refused" - Service not running or firewall blocking

### Uninstallation
## Complete Removal
# Run the uninstallation script
sudo ./deploy/uninstall.sh

## Manual Removal
If you need to remove manually:
# Stop and disable service
sudo systemctl stop string-search-server
sudo systemctl disable string-search-server

# Remove service file
sudo rm -f /etc/systemd/system/string-search-server.service
sudo systemctl daemon-reload

# Remove application files
sudo rm -rf /opt/string_search_server

# Remove configuration
sudo rm -rf /etc/string_search_server

# Remove user (optional)
sudo userdel stringserver 2>/dev/null || true

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##                                                                            WSL (Windows Subsystem for Linux) Deployment
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Quick WSL Installation
./deploy/install-wsl.sh
cd ~/string_search_server
./manage-server.sh start

### WSL-Specific Notes
No systemd: WSL doesn't use systemd, so we use foreground processes
Network access: Server binds to 0.0.0.0 so Windows can connect to 127.0.0.1:44445
File paths: Use Linux-style paths within WSL
Background operation: Use nohup for background operation

## WSL Management
# Start in foreground (recommended for testing)
./manage-server.sh start

# Start in background
nohup ./string-search-server.sh > logs/server.log 2>&1 &

# Check status
./manage-server.sh status

# View logs
./manage-server.sh logs

# Stop server
./manage-server.sh stop
text

### **3. Run WSL Installation**
# Make executable and run
chmod +x deploy/install-wsl.sh
./deploy/install-wsl.sh

# Test the installation
cd ~/string_search_server
./manage-server.sh info
./manage-server.sh start

## WSL Deployment (Development)
For WSL environments where systemd is not available:

# Setup WSL deployment
./deploy/setup-wsl.sh

# Start server
./manage-server-wsl.sh start

# Test connection
./manage-server-wsl.sh test
WSL Management
./manage-server-wsl.sh start - Start server in foreground
./manage-server-wsl.sh status - Check if running
./manage-server-wsl.sh stop - Stop server
./manage-server-wsl.sh test - Test connection
./manage-server-wsl.sh info - Show information

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                                  ❓ FAQ
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Q: Can I run multiple instances of the server?
A: Yes, but you need to:
Create separate service files with different names
Use different ports in configuration
Use different installation directories

Q: How do I update the server?
A:
# Stop service
sudo systemctl stop string-search-server

# Update files
sudo cp -r server/ /opt/string_search_server/

# Restart service
sudo systemctl start string-search-server

Q: How to change the server port?
A:
Edit /opt/string_search_server/config/server_config.conf
Change the port value
Restart service: sudo systemctl restart string-search-server

Q: How to monitor server performance?
A:
# Monitor connections
sudo netstat -tlnp | grep 44445

# Monitor resource usage
sudo systemctl status string-search-server

# Monitor logs in real-time
sudo journalctl -u string-search-server -f

Q: The service starts but clients can't connect
A: Check:
Firewall rules: sudo ufw status
Port listening: sudo ss -tlnp | grep 44445
Network connectivity
SSL configuration if using encryption

Q: How to backup the server configuration?
A:
# Backup configuration
sudo tar -czf string-search-server-backup-$(date +%Y%m%d).tar.gz \
  /opt/string_search_server/config/ \
  /etc/systemd/system/string-search-server.service

#### 📞 Support
If you encounter issues not covered in this guide:
Check logs: sudo journalctl -u string-search-server
Verify configuration: Review all settings in config file
Test manually: Run server outside of systemd for debugging
Check permissions: Ensure all files are owned by stringserver user
For additional help, refer to the main README.md or check the project documentation.

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                             End of documentation
<!-- 
                                                                            Last Updated: Nov 1, 2025
                                                              String Search Server - Production Deployment Guide -->
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------