# followCrom's Top Track Tracker

![Alt Text](readme_img.png)

## Start the virtual environment

```bash
$ source /.venv/bin/activate

source venv/bin/activate
```

(pip install -r requirements.txt)

## Start the Dev server (default port 8000)

```python
python manage.py runserver
```
This starts Django's built-in development server.

If you need to run the server on a different port, you can specify it as follows:

```python
python manage.py runserver 8080
```

## Run dev server on the AWS instance

```bash
python manage.py runserver 0.0.0.0:8000
```


0.0.0.0 tells the development server to listen on all public IP addresses that the VM has. This makes the server accessible from outside the VM.
8000 specifies the port number on which the server will listen for requests.
Open your web browser and go to http://VM-Public-IP:8000

## Log into the app:

Login with AWS or Local account: **docs/users.txt**


## Login to the Apache server


### Connect to LightSail instance

```bash
ssh -i ~/.ssh/ttt-lightsail.pem bitnami@18.171.147.94
```

## Access the DB:

All saved records are stored in the TrendingTracks model. View, add and remove tracks via the console in the U.I.

For full database entry details:

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
        
**Note**: In Django, every model automatically gets an id field: an auto-incrementing primary key for the model, identifying each record in the database table associated with your model. You don't need to define this field; Django takes care of it for you.

## Debug Mode

Never run a production site in Debug mode as it can expose sensitive information and make your site vulnerable to attacks.

```python
settings.py
DEBUG = False
```

## Renew Secret Key

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```


## Upload Static Files

```bash
python manage.py collectstatic
```

This command will prompt you to confirm the upload of your static files to the S3 bucket. Type yes to proceed.

## Test the user-top-read endpoint

```bash
curl --request GET \
  --url 'https://api.spotify.com/v1/me/top/tracks?time_range=short_term&offset=0' \
  --header 'Authorization: Bearer xxx'
```
<br>

# Apache

## Config test:

`sudo apachectl configtest`

## Status:
`sudo /opt/bitnami/ctlscript.sh status apache`

## Restart Apache:
`sudo /opt/bitnami/ctlscript.sh restart apache`

# Logs

### Access Logs:
`sudo cat /opt/bitnami/apache2/logs/access_log`

### Error Logs:
```bash
sudo tail -n 20 /opt/bitnami/apache2/logs/error_log
```

or all:

`sudo cat /opt/bitnami/apache2/logs/error_log`

### Django files:
`head -n 20 settings.py`

# Fresh VM

### Connect to LightSail instance

```bash
ssh -i ~/.ssh/toptt-aws.pem bitnami@13.40.128.58
```

### cat top 100 lines of the error log

```bash
sudo tail -n 20 /opt/bitnami/apache2/logs/error_log
```

# FileZilla:

**.pem keys** are in Edit -> Settings -> SFTP -> Add Key File