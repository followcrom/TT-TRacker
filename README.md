# followCrom's Top Track Tracker

![followCrom's Top Track Tracker](readme_img.png)

## Start the virtual environment locally 👨🏻‍💻

```bash
source .venv/bin/activate
```

#### Install the requirements

`pip install -r requirements.txt`

## Start the Dev server (default port 8000)

```bash
python manage.py runserver

# or

python manage.py runserver 8000
```

This starts Django's built-in development server.

## Run dev server on the AWS instance 👦

🆕 **Untested**

Stop the Apache server to free up the port for the Django development server.

```bash
sudo systemctl stop apache2
```

Then start your Django development server:

```bash
python manage.py runserver 0.0.0.0:8000
```


0.0.0.0 tells the development server to listen on all public IP addresses that the VM has. This makes the server accessible from outside the VM.
8000 specifies the port number on which the server will listen for requests.
Open your web browser and go to http://VM-Public-IP:8000

## Log into the app: 🔑

Login with AWS or Local account: **docs/users.txt**


## Debug Mode 🕵🏻‍♀️

Never run a production site in Debug mode as it can expose sensitive information and make your site vulnerable to attacks.

```python
settings.py
DEBUG = False
```

## Renew Secret Key 🔐

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

# Design 🎨

To edit the styles locally: in settings.py ensure that Local static settings are uncommented and S3 static settings are commented out.

Once you have made your changes, uncomment the S3 static settings. **LEAVE the Local static settings uncommented**, then run the following command:

```bash
python manage.py collectstatic
```

This will prompt you to confirm the upload of your static files to the S3 bucket. Type yes to proceed.

Once the static files have been uploaded to the S3 bucket, you can comment out the Local static settings to use the S3 static files.

# Apache 🐎

### Connect to LightSail instance

Security group rule means that only my IP can access the instance.

```bash
ssh -i ~/.ssh/ttt-lightsail.pem bitnami@18.171.147.94
```

# Logs 📝

### Access Logs:
```bash
sudo tail -n 20 /opt/bitnami/apache2/logs/access_log

cat /opt/bitnami/apache2/logs/access_log
```

### Error Logs:
```bash
sudo tail -n 20 /opt/bitnami/apache2/logs/error_log
```

or all:

`sudo cat /opt/bitnami/apache2/logs/error_log`

### Django files:
`head -n 20 settings.py`

<br>

## Fixing the .cache Issue 👷

There is a potential issue with writing session info to the Apache (LightSail) server. When I copied to the .`cache` file from local to LightSail, I began getting 500 errors when 'Calling Spotify...' from `spotify_client.py -> spotify_callback`.

Atempt to fix this by changing permissions for the .cache file on the Apache server. It should be in the `djangoapp` directory:

```bash
sudo chown -R www-data:www-data .cache

# Restart Apache:
sudo /opt/bitnami/ctlscript.sh restart apache
```

This resulted in: **-rw-r--r-- 1 www-data www-data    532 May 11 16:05 .cache**

I wonder if the server has to have permissions to write to the .cache file? Even after this I continued to the get _Couldn't write token to cache at: .cache_ in the error logs, but this was around the time the 500 errors were resolved, so it is worth noting.


```bash
# Config test:
sudo apachectl configtest

# Status:
sudo /opt/bitnami/ctlscript.sh status apache

# Restart Apache:
sudo /opt/bitnami/ctlscript.sh restart apache
```

## On Changing Spotify Password

I changed my Spotify password and then tried using the Spotify API but I kept getting hit with error: invalid_grant, error_description: Refresh token revoked. refresh token had been revoked by Spotify by a password change. I needed to mauanlly delete the .cache file and re-authenticate. Just delete the cache file at cache_path. That's where the token info is stored.

```bash
rm .cache
```

<br>

# Database 🛢

```bash
python manage.py makemigrations

python manage.py migrate
```

### Access the DB:

All saved records are stored in the TrendingTracks model. View, add and remove tracks via the console in the U.I.

For local database entry details run on the local machine. For the AWS instance, run on the server.

```python
python3 access_trending_tracks.py
```

Fields:
  - artist
  - song
  - album
  - release_year
  - popularity
  - uri
  - genres
  - energy
  - key
  - valence
  - mood
  - tempo
  - artist_uri

<br>

**Note**: In Django, every model automatically gets an id field: an auto-incrementing primary key for the model, identifying each record in the database table associated with your model. You don't need to define this field; Django takes care of it for you.

You can access the the auth_user table in your database via the Django admin interface at /admin/ or:

```bash
python display_users.py
```

<br>

# New Users 🧑‍💻

Credentials: **docs/users.txt**

### Create a Superuser

`python manage.py createsuperuser`

Follow the prompts to create the superuser.

### Create a new AWS user 

Navigate to https://tttapp.followcrom.online/admin/ and log in with the AWS superuser credentials. In the admin interface, "Add User".

### Create a new local user

Navigate to /admin/ in your browser and log in with the local superuser credentials.

### Exporting Users

You can export user data from your current database using Django's management commands or custom scripts.

```bash
python manage.py dumpdata auth.user --output users.json
```

<br>

# Fix Attempts if Necessary 👷

### Test the user-top-read endpoint

```bash
curl --request GET \
  --url 'https://api.spotify.com/v1/me/top/tracks?time_range=short_term&offset=0' \
  --header 'Authorization: Bearer xxx'
```

### Use curl to test the callback URL:

```bash
curl "https://tttapp.followcrom.online/callback/?code=<auth-code>"

# Here's an example of what the command might look like:
curl "http://localhost:8000/callback/?code=AQBx9dKc..."
```

### Clear the cache:

`rm .cache`

### Temporarily run Django app using the development server on AWS

```bash
sudo systemctl stop apache2

# Then start your Django development server:
python manage.py runserver 0.0.0.0:8000
```

### Overwrite file with a specific commit version

```bash
# Identify the Commit Hash:
git log

# Check Out the Specific File from the Commit:
git checkout <commit-hash> -- <path-to-file>
```

### CORS:

This may well not be necessary, but if you're having trouble with CORS, you can add the following to your Apache configuration file:

```bash
cd /opt/bitnami/apache2/conf/vhosts

sudo nano tttracker-vhost.conf
```

More secure:

```bash
<Directory /home/bitnami/djangoapp/tttracker>
    Header set Access-Control-Allow-Origin "https://tttapp.followcrom.online"
    <Files wsgi.py>
        Require all granted
    </Files>
</Directory>
```

Less secure:

```bash
    <Directory /home/bitnami/djangoapp/tttracker>
        Header set Access-Control-Allow-Origin "*"
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
```

Before these headers will work, ensure that the mod_headers module is enabled in Apache:

```bash
sudo a2enmod headers
sudo /opt/bitnami/ctlscript.sh restart apache
```
<br>

# FileZilla 🦖

**.pem keys** are in Edit -> Settings -> SFTP -> Add Key File