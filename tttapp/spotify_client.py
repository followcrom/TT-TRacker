from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import time
from django.conf import settings

# Global Spotipy client
sp = None


def get_spotipy_client(request):
    global sp

    if not sp:
        sp = Spotify()

    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-library-read user-read-playback-state",
        cache_path=None,
    )

    token_info = request.session.get("token_info", {})
    if token_info and time.time() < token_info.get("expires_at", 0):
        sp.auth = token_info["access_token"]
        print("Token: ", sp.auth)
    elif token_info.get("refresh_token"):
        new_token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        request.session["token_info"] = new_token_info
        sp.auth = new_token_info["access_token"]
        print("Refresh token: ", sp.auth)
    else:
        sp.auth = None
        print("No token: ", sp.auth)

    return sp


# sp = get_spotipy_client()
