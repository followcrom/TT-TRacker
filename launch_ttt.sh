#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Install necessary packages
echo "Installing Top Track Tracker..."

# Update package lists and install Python3, pip, and virtual environment support
apt update && apt install python3 python3-pip python3-venv -y

# Create the directory for the Django app
mkdir -p /var/www/ttt
cd /var/www/ttt

# Clone the repository (from DESKTOP branch)
git clone --depth 1 --branch DESKTOP https://github.com/followcrom/TopTrackTracker.git .

# Set up the Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the Python dependencies for the Django app
pip install --upgrade pip
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Install Gunicorn, which is a WSGI server for running Python web apps
pip install gunicorn

# Create a systemd service file for Gunicorn
cat > /etc/systemd/system/ttt.service <<EOF
[Unit]
Description=Gunicorn daemon for Top Track Tracker
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/ttt
ExecStart=/var/www/ttt/.venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/ttt/tttracker.sock tttracker.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd to recognize the new service file and start Gunicorn
systemctl daemon-reload
systemctl start ttt.service
systemctl enable ttt.service
systemctl status ttt.service --no-pager

# Ensure correct permissions for the app directory
chown -R www-data:www-data /var/www/ttt

# Set permissions for directories
find /var/www/ttt -type d -exec chmod 755 {} \;

# Set permissions for other files
# find /var/www/ttt -type f \( -name "*.py" -o -name "*.sqlite3" -o -name "*.md" -o -name "*.html" \) -exec chmod 644 {} \;

# Configure Nginx as a reverse proxy to forward requests to Gunicorn
cat > /etc/nginx/sites-available/ttt <<EOF
server {
    server_name www.ttt.followcrom.com ttt.followcrom.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/ttt/tttracker.sock;
    }
}
EOF

# Enable the Nginx site configuration by creating a symbolic link if it doesn't exist
if [ ! -L /etc/nginx/sites-enabled/ttt ]; then
    ln -s /etc/nginx/sites-available/ttt /etc/nginx/sites-enabled
fi

# Test Nginx configuration for syntax errors
if nginx -t; then
    echo "Nginx configuration syntax is okay."
    systemctl restart nginx
    echo "Nginx restarted successfully."
else
    echo "Error in Nginx configuration." >&2
    exit 1
fi

# Obtain an SSL certificate from Let's Encrypt via Certbot
certbot --nginx -d ttt.followcrom.com -d www.ttt.followcrom.com --agree-tos --email followcrom@gmail.com --non-interactive
