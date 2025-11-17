#!/bin/bash
#
# Installation script for Battery Counter on Raspberry Pi
# Run with: bash install.sh
#

set -e  # Exit on error

echo "=========================================="
echo "Battery Counter Installation Script"
echo "For Raspberry Pi 4 / Zero 2"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "Step 1: Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install system dependencies
echo ""
echo "Step 2: Installing system dependencies..."
sudo apt install -y python3-pip python3-dev python3-pil git

# Enable SPI
echo ""
echo "Step 3: Enabling SPI interface..."
if ! grep -q "dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    SPI_ENABLED=1
else
    echo "SPI already enabled"
    SPI_ENABLED=0
fi

# Install Python packages
echo ""
echo "Step 4: Installing Python packages..."
pip3 install -r requirements.txt

# Create cache directory
echo ""
echo "Step 5: Creating cache directory..."
sudo mkdir -p /var/local
sudo chown $USER:$USER /var/local

# Verify installation
echo ""
echo "Step 6: Verifying installation..."
if python3 -c "import RPi.GPIO, spidev, requests, PIL" 2>/dev/null; then
    echo "✓ All Python packages installed successfully"
else
    echo "✗ Package verification failed"
    exit 1
fi

# Add user to gpio group
echo ""
echo "Step 7: Configuring permissions..."
sudo usermod -a -G gpio $USER
echo "✓ Added user to gpio group"

# Create systemd service (optional)
echo ""
read -p "Install as systemd service (auto-start on boot)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    PROJECT_DIR=$(pwd)
    SERVICE_FILE=/etc/systemd/system/battery-counter.service
    
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Battery Counter Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 $PROJECT_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable battery-counter.service
    
    echo "✓ Systemd service installed"
    echo "  Start with: sudo systemctl start battery-counter.service"
    echo "  View logs: sudo journalctl -u battery-counter.service -f"
fi

# Final instructions
echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""

if [ $SPI_ENABLED -eq 1 ]; then
    echo "⚠️  IMPORTANT: SPI was just enabled."
    echo "   You must REBOOT for changes to take effect:"
    echo "   sudo reboot"
    echo ""
fi

echo "Next steps:"
echo "1. Edit config.py to set your device ID and pin configuration"
echo "2. Connect your hardware (IR sensor, LED, ST7789 display)"
echo "3. Run manually: python3 main.py"
echo "   OR"
echo "   Start service: sudo systemctl start battery-counter.service"
echo ""
echo "For detailed instructions, see README.md"
echo ""
