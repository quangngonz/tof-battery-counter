#!/bin/bash
# Script to set up and start the battery-counter service

SERVICE_FILE="battery-counter.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_FILE"
PROJECT_DIR=$(pwd)  # Use the current working directory

# Copy the service file to the systemd directory
sudo cp "$PROJECT_DIR/$SERVICE_FILE" "$SERVICE_PATH"

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable "$SERVICE_FILE"

# Start the service
sudo systemctl start "$SERVICE_FILE"

echo "Service $SERVICE_FILE has been set up and started."
