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
    try:
        print("Callback")
        sp_oauth = get_spotify_oauth()
        print("OAuth object obtained")

        code = request.GET.get("code")
        print("Code:", code)

        if not code:
            print("No code in request")

        token_info = sp_oauth.get_access_token(code)
        print("Token info before saving to session: ", token_info)

        request.session["token_info"] = token_info
        saved_token_info = request.session.get("token_info", {})
        print("Token info after saving to session: ", saved_token_info)

    except Exception as e:
        print(f"Error in spotify_callback: {e}")

    return redirect("home")


# -----------------------------------------


def get_spotipy_client(request):
    token_info = request.session.get("token_info", {})

    # Logging token info retrieved from session
    print("Token info in session 1: ", token_info)

    if not token_info:
        print("No token info")
        return None

    current_time = time.time()
    expires_at = token_info.get("expires_at", 0)
    print("Expires at: ", expires_at)

    if current_time > expires_at:
        print("Refreshing token...")
        sp_oauth = get_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])

        # Logging token info after refresh
        print("Token info refreshed.")

        request.session["token_info"] = token_info

        # Verify if refreshed token_info is correctly saved in session
        print("Token info in session 2 : ", token_info)
    else:
        print("Token is still valid.")

    return Spotify(auth=token_info["access_token"])


# -----------------------------------------
