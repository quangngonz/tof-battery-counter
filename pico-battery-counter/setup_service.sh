#!/bin/bash
# Script to set up and start the battery-counter service

SERVICE_FILE="battery-counter.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_FILE"
PROJECT_DIR=$(pwd)  # Use the current working directory

echo "Setting up battery-counter service..."
echo "Project directory: $PROJECT_DIR"

# Update the service file with the current directory and user
CURRENT_USER=$(whoami)
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$PROJECT_DIR|g" "$PROJECT_DIR/$SERVICE_FILE"
sed -i "s|ExecStart=.*|ExecStart=/usr/bin/python3 $PROJECT_DIR/main.py|g" "$PROJECT_DIR/$SERVICE_FILE"
sed -i "s|User=.*|User=$CURRENT_USER|g" "$PROJECT_DIR/$SERVICE_FILE"

# Copy the service file to the systemd directory
sudo cp "$PROJECT_DIR/$SERVICE_FILE" "$SERVICE_PATH"

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable "$SERVICE_FILE"

# Start the service
sudo systemctl start "$SERVICE_FILE"

# Show service status
echo ""
echo "Service status:"
sudo systemctl status "$SERVICE_FILE" --no-pager

echo ""
echo "Service $SERVICE_FILE has been set up and started."
echo "To view logs: sudo journalctl -u $SERVICE_FILE -f"
