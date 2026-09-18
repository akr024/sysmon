#!/bin/bash
set -e

PROJECT_DIR="/home/akr/projects/sysmon"
LOG_DIR="/var/log/sysmon"
SERVICE_USER="sysmon"

echo "=== sysmon installer ==="

echo "[1/9] Installing OS packages..."
sudo dnf install -y python3 python3-pip git policycoreutils-python-utils

echo "[2/9] Setting up Python virtual environment..."
cd "$PROJECT_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

echo "[3/9] Creating service user..."
id "$SERVICE_USER" &>/dev/null || sudo useradd --system --no-create-home --shell /usr/sbin/nologin "$SERVICE_USER"

echo "[4/9] Setting up log directory..."
sudo mkdir -p "$LOG_DIR"
sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$LOG_DIR"
sudo chmod 750 "$LOG_DIR"

echo "[5/9] Granting journal read access..."
sudo usermod -aG systemd-journal "$SERVICE_USER"

echo "[6/9] Fixing project directory ownership and traversal permissions..."
sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$PROJECT_DIR"
sudo chmod o+x "$(dirname "$PROJECT_DIR")" 2>/dev/null || true

echo "[7/9] Applying SELinux contexts..."
sudo semanage fcontext -a -t bin_t "$PROJECT_DIR/venv/bin(/.*)?" 2>/dev/null || true
sudo semanage fcontext -a -t admin_home_t "$PROJECT_DIR(/.*)?" 2>/dev/null || true
sudo restorecon -Rv "$PROJECT_DIR"

echo "[8/9] Installing systemd service..."
sudo cp "$PROJECT_DIR/deploy/sysmon.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now sysmon

echo "[9/9] Done."
echo ""
echo "Check status with: sudo systemctl status sysmon"
echo "Metrics log:        $LOG_DIR/sysmon.log"
echo "Alerts log:         $LOG_DIR/alerts.log"
echo "Live journal:       sudo journalctl -u sysmon -f"
