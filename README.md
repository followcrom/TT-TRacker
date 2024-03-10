# Top Track Tracker

![Alt Text](readme_img.png)

## Start the virtual environment

```bash
$ source /.venv/bin/activate
```

(pip install -r requirements.txt)

## Start the Development Server (default port 8000)

`python manage.py runserver`

If you need to run the server on a different port, you can specify it as follows:

`python manage.py runserver 8080`

## Stop the Server

`Ctrl+C`

## Log into the app:

Login with AWS or Local account: **docs/users.txt**


## Login to the Apache server


### Connect to LightSail instance

```bash
ssh -i ~/.ssh/ttt-lightsail.pem bitnami@18.171.147.94
```

## Access the DB:

All saved records are stored in the TrendingTracks model. List, add and remove tracks via the console in the U.I.

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