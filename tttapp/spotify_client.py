from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import time
from django.conf import settings
from django.shortcuts import redirect

# -----------------------------------------


def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-library-read user-read-playback-state",
    )


# -----------------------------------------


def spotify_auth(request):
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print("Auth URL: ", auth_url)
    return redirect(auth_url)


# -----------------------------------------


def spotify_callback(request):
    print("Callback")
    sp_oauth = get_spotify_oauth()
    code = request.GET.get("code")
    print("Code:", code)
    token_info = sp_oauth.get_access_token(code)

    # Logging token info before saving to session
    print("Token info before saving to session: ", token_info)

    request.session["token_info"] = token_info

    # Verify if token_info is correctly saved in session
    saved_token_info = request.session.get("token_info", {})
    print("Token info after saving to session: ", saved_token_info)

    return redirect("home")


# -----------------------------------------


def get_spotipy_client(request):
    token_info = request.session.get("token_info", {})

    # Logging token info retrieved from session
    print("Retrieved token info from session: ", token_info)

    if not token_info:
        print("No token info")
        return None

    current_time = time.time()
    expires_at = token_info.get("expires_at", 0)

    if current_time > expires_at:
        print("Refreshing token...")
        sp_oauth = get_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])

        # Logging token info after refresh
        print("Refreshed token info: ", token_info)

        request.session["token_info"] = token_info

        # Verify if refreshed token_info is correctly saved in session
        updated_token_info = request.session.get("token_info", {})
        print("Token info in session after refresh: ", updated_token_info)
    else:
        print("Token is still valid.")

    return Spotify(auth=token_info["access_token"])


# -----------------------------------------
