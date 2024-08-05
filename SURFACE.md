# Top Track Tracker on SURFACE

`free -h` before:

                    total        used        free      shared  buff/cache   available
     Mem:           7.5Gi       1.4Gi       5.5Gi       3.0Mi       592Mi       6.0Gi
     Swap:          2.0Gi          0B       2.0Gi


Git clone the files from the repository and install the dependencies.

`free -h` after:

                    total        used        free      shared  buff/cache   available
     Mem:           7.5Gi       1.4Gi       5.4Gi       3.0Mi       279Mi       5.6Gi
     Swap:          2.0Gi          0B       2.0Gi

(These values change.)

# Local setup

Create a Virtual Environment

```bash
python3 -m venv .venv
```

Activate the Virtual Environment

```bash
source .venv/bin/activate
```

Install the dependencies

```bash
pip install -r requirements.txt
```

# Database

`py manage.py migrate` (I have set up the alias `py` for `python3` on Surface WSL2.)

NOTE: When you run `manage.py migrate`, it applies the database schema changes (e.g., creating tables, modifying columns) based on the Django app's models (models.py). However, it doesn't migrate data, such as user accounts or trending tracks. If you need this data on the new machine you have to copy the SQLite database itself.

### Local db.sqlite3

I copied the SQlite3 database from DESKTOP to SURFACE. On logging into the admin backend - `http://127.0.0.1:8000/admin/` - I noticed that I only had the **local** user account in the DB. (The local user has superuser status.) I hadn’t backed-up the DB from AWS before terminating the LightSail instance.

### Remote db.sqlite3

At some point an empty DB was created on the Droplet. If you run a setup script or deployment script, it might create a new database as part of the setup process. When you run Django management commands like `python manage.py migrate`, Django creates or updates the SQLite database based on the migration files.

## Users

You don’t need to create a superuser before you can create other users in Django. A superuser is typically used for administrative purposes and to access the Django admin interface.

1. Creating a Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to set a username, email, and password.

2. Creating Regular Users

If you have created a superuser and have access to the Django admin site (/admin), you can create users through the Django admin interface.

I have a script to create users using command-line arguments. You can run the script and provide arguments directly. It runs on the VM in `/var/www/ttt/`.

```python
python create_users.py newuser securepassword

# Or with an email:
python create_users.py newuser securepassword newuser@example.com

# In Django, the email field for a user is optional by default. This means you do not have to provide an email address when creating a regular user if you don’t need it.
```

### List Users

Option 1: Visit `http://127.0.0.1:8000/admin/auth/user/`

You need to be logged in as a superuser to access the Django admin interface.

Option 2: `py display_users.py`

### Read Trending Tracks

This will read the DB on whichever machine it is run. 

```bash
python access_trending_tracks.py
```

# Local Development

Switch between dev and production in `settings.py`:

1. In development, set `DEBUG = True`. In production, set `DEBUG = False`.

2. Change the **SPOTIFY_REDIRECT_URI**.


### Start the Dev server

```bash
python manage.py runserver
```
Visit the site at: http://127.0.0.1:8000/

If the default port (8000) is already in use, you can specify a different port:

```bash
python manage.py runserver 8080
```

<br>

# Launching on Digital Ocean

**Step 1**: Create a Digital Ocean Droplet

**Step 2**: Use SSH to connect to new droplet. I'm using the SSH key pair I created for the domdom project.

```bash
ssh -i ~/.ssh/digiocean root@188.166.155.230
```

**Step 3**: Update and Upgrade the system

```bash
apt update && apt upgrade -y
```

**Step 4**: Install Python and Nginx

```bash
apt install python3 python3-pip python3-venv nginx -y
```

On the D.O. Ubuntu 22.04 droplet, I had to reboot at this stage : `reboot`

**Step 5**: Create a Directory for the App

```bash
mkdir /var/www/ttt
cd /var/www/ttt
```

Note: /var/www/ is the standard location for web applications.

**Step 6**: Clone Git Repository

```bash
git clone https://github.com/followcrom/TopTrackTracker.git ttt/
```

Specifying the directory name `ttt/` defines the name of the directory to be created rather than using the name of the repository.

**Step 6**: Transfer the .env file, which is not in the repository.

```bash
scp -i ~/.ssh/digiocean .env root@188.166.155.230:/var/www/ttt/tttracker
```

**Step 7**: Set Up a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Step 8**: Install Dependencies:

```bash
pip install -r requirements.txt
```

**Step 9**: Run Migrations:

```bash
python manage.py migrate
```
DO NOT RUN Collect Static! This will overwrite the static files in the S3 bucket.

**Step 10**: Install Gunicorn (WSGI server)

```bash
pip install gunicorn
```

**Step 11**: Create a Systemd Service File for Gunicorn

```bash
nano /etc/systemd/system/gunicorn.service
```

Add the following content:

```ini
[Unit]
Description=gunicorn daemon for ttt
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/ttt
ExecStart=/var/www/ttt/.venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/ttt/tttracker.sock tttracker.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Step 12**: Ensure that the web server user (www-data for Nginx) has the appropriate permissions to access your project directory.

```bash
chown -R www-data:www-data /var/www/ttt
chmod -R 755 /var/www/ttt
```

[Troubleshoot interaction between Nginx and the backend application (Gunicorn)](#interaction-between-nginx-and-the-backend-application-gunicorn)

**Step 13**: Start and Enable Gunicorn:

- (systemctl daemon-reload) # Reload the systemd manager configuration if necessary
- systemctl start gunicorn
- systemctl enable gunicorn
- systemctl status gunicorn

**Step 14**: Create an Nginx Configuration File:

`nano /etc/nginx/sites-available/ttt`

Add the following content:

```nginx
server {
    listen 80;
    server_name www.ttt.followcrom.online ttt.followcrom.online 188.166.155.230;  # can handle both requests to a bare IP address and domain names

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/ttt/tttracker.sock;
    }

    location /static/ {
        alias /var/www/ttt/static/;
    }
}
```

Ensure that your Django ALLOWED_HOSTS setting includes your domain names and IP address. Django will return a 400 Bad Request if the request's Host header doesn't match any entry in ALLOWED_HOSTS.

**Step 15**: Create a Symlink

In `/etc/nginx/` there is both a `sites-available` and `sites-enabled` dir. Create a symlink to sites-enabled:

```bash
ln -s /etc/nginx/sites-available/ttt /etc/nginx/sites-enabled`
```

**Step 16**: Test Nginx Configuration

```bash
nginx -t
```

**Step 17**: Reload Nginx to Apply the changes:

```bash
systemctl reload nginx
```

#### Reload vs. Restart

Reload: This tells Nginx to reload its configuration files without stopping the service. This is generally less disruptive as it doesn’t interrupt active connections.

Restart: This stops and then starts the Nginx service, which can interrupt active connections but ensures that all configuration changes are applied. (`sudo systemctl restart nginx`.)

**Step 18**: Configure the Firewall

```bash
ufw allow 'Nginx Full'
ufw allow OpenSSH
ufw enable
ufw status verbose
```

**Step 19**: Verify and Launch the Services (if necessary)

```bash
systemctl restart gunicorn
systemctl status gunicorn

systemctl restart nginx
systemctl status nginx
```

**Step 20**: Access Your Application

Open your web browser and go to your droplet's IP address or domain name.

## Design 🎨

### Locally

In `settings.py` ensure that Local static settings are uncommented and S3 static settings are commented out.

Once you have made your changes, uncomment the S3 static settings. LEAVE the Local static settings uncommented, then run the following command:

`python manage.py collectstatic`

This will prompt you to confirm the upload of your static files to the S3 bucket. Type yes to proceed.

### On Digital Ocean

Once the static files have been uploaded to the S3 bucket, you can comment out the Local static settings to use the S3 static files.

## Troubleshooting

### Check Logs:

```bash
tail -f /var/log/nginx/error.log

tail -20 /var/log/nginx/access.log

journalctl -u gunicorn -f
```

### Ensure all the domain names and IP addresses are added to the ALLOWED_HOSTS in settings.py

Django will return a 400 Bad Request if the request's Host header doesn't match any entry in ALLOWED_HOSTS.

### Verify that both services are running without errors:

```bash
systemctl status gunicorn
systemctl status nginx
```

### Interaction between Nginx and the backend application (Gunicorn)

Run Gunicorn manually for debugging purposes:

```bash
/var/www/ttt/.venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/ttt/tttracker.sock tttracker.wsgi:application
```

On running `ls -l /var/www/ttt/tttracker.sock` I saw that the Gunicorn socket file (`/var/www/ttt/tttracker.sock`) did not exist. Nginx needs to be able to access this socket file. Step 12 (above and below) seemed to fix this, but in case GPT also suggests running the following:

```bash
chown www-data:www-data /var/www/ttt/tttracker.sock
```

Step 12 reminder:

```bash
chown -R www-data:www-data /var/www/ttt
chmod -R 755 /var/www/ttt
```

Ensure the socket file exists and is writable by Nginx (usually under www-data user). Adjust permissions if necessary:

```bash
ls -l /var/www/ttt/tttracker.sock

# returns:
srwxrwxrwx 1 root www-data 0 Aug  5 00:16 /var/www/ttt/tttracker.sock
```