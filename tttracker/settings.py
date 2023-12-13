# settings.py

"""
Top Track Tracker is a web app built in the Django framework. It uses the Spotify API to retrieve:

1. the user's top tracks across three time ranges: [short_term, medium_term, long_term]
(user-top-read: https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks)

2. audio features for each track (Get Tracks' Audio Features: https://developer.spotify.com/documentation/web-api/reference/get-several-audio-features)

It also uses the Spotify API to start playback of the user's top tracks. (Scope: user-modify-playback-state, https://developer.spotify.com/documentation/web-api/reference/start-a-users-playback)

The Spotipy library is used to interact with the Spotify API.

Get Track: https://developer.spotify.com/documentation/web-api/reference/get-track

Top Track Tracker utilizes a SQLite database to store selected tracks. The `add_to_trending` function adds a track to the database. The `view_trending_tracks` function retrieves all tracks from the database and renders them using a template. The `delete_trending_track` function deletes a track from the database. `start_spotify_playback` uses the Spotipy library with the `user-modify-playback-state` scope to start playback of the tracks in the database.

OAuth 2.0 is required for authenticating all API requests.
"""

from pathlib import Path
import os
import dj_database_url

from dotenv import load_dotenv

load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ENVIROMENTAL VARIABLES
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
# SPOTIFY_REDIRECT_URI = "https://toptracktracker.onrender.com/callback/"

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = "static-ttt"
AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
AWS_DEFAULT_ACL = "public-read"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY")
LASTFM_USERNAME = os.environ.get("LASTFM_USERNAME")


# DEV / PRODUCTION
DEBUG = False


# DEVELOPMENT_MODE = os.environ.get("DEVELOPMENT_MODE", "True") == "True"
DEVELOPMENT_MODE = False


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"

if DEVELOPMENT_MODE:
    SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8000/callback/"

    # Local static settings
    STATIC_URL = "/static/"
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

    ALLOWED_HOSTS = [
        "localhost",
        "127.0.0.1",
    ]
else:
    SPOTIFY_REDIRECT_URI = "https://toptracktracker.onrender.com/callback/"

    # S3 Static settings
    STATIC_URL = "/static/"
    STATIC_LOCATION = "static"
    AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
    STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, STATIC_LOCATION)
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

    ALLOWED_HOSTS = [
        "toptracktracker.onrender.com",
        "www.toptracktracker.onrender.com",
    ]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tttapp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tttracker.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "tttracker.wsgi.application"

# Default setting for session engine
SESSION_ENGINE = "django.contrib.sessions.backends.db"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

DATABASES = {"default": dj_database_url.config(default=os.environ.get("DATABASE_URL"))}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True
