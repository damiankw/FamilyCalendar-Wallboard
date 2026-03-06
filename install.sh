#!/bin/bash
# Installer for Screen Scheduler

set -e

SCRIPT_NAME="screen_scheduler.py"
SERVICE_NAME="screen-scheduler.service"
CONFIG_DIR="/etc/screen-scheduler"
BIN_DIR="/usr/local/bin"

# Make sure running as sudo
if [[ $EUID -ne 0 ]]; then
   echo "This installer must be run with sudo"
   exit 1
fi

echo "Creating config directory..."
mkdir -p $CONFIG_DIR

echo "Copying script..."
cp $SCRIPT_NAME $BIN_DIR/
chmod +x $BIN_DIR/$SCRIPT_NAME

echo "Copying service file..."
cp $SERVICE_NAME /etc/systemd/system/

echo "Installing default config..."
if [ ! -f $CONFIG_DIR/config.json ]; then
    cat <<EOF > $CONFIG_DIR/config.json
{
  "output_name": "HDMI-A-1",
  "button_gpio": 17,
  "override_minutes": 30,
  "scheduler_interval": 15,
  "schedule": [
    ["06:00", "on"],
    ["10:00", "off"],
    ["17:00", "on"],
    ["19:00", "off"]
  ]
}
EOF
fi

echo "Reloading systemd..."
systemctl daemon-reload

echo "Enabling and starting service..."
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

echo "Installation complete."
