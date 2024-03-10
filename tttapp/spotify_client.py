from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import time
from django.conf import settings
from django.shortcuts import redirect

# -----------------------------------------

scope="user-library-read user-read-playback-state user-top-read"

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=scope
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
        print("Calling Spotify...")
        sp_oauth = get_spotify_oauth()
        print("OAuth object obtained")
        code = request.GET.get("code")

        if not code:
            print("No code in request")

        token_info = sp_oauth.get_access_token(code)
        request.session["token_info"] = token_info
        print("\nCallback token info saved to session")
        print("\nCallback token info: ", token_info)

        # Retrieve the stored URL or default to 'home' if not found
        redirect_url = request.session.get("pre_auth_url", "home")

    except Exception as e:
        print(f"Error in Spotify callback: {e}")
        redirect_url = "error"

    return redirect(redirect_url)


# -----------------------------------------

# Auto called on top_tracks load
def get_spotipy_client(request):
    token_info = request.session.get("token_info", {})
    if not token_info:
        print("No token info")
        return None

    current_time = time.time()
    expires_at = token_info.get("expires_at", 0)
    if current_time > expires_at:
        print("Refreshing token...")
        sp_oauth = get_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        print("Token info refreshed")

        request.session["token_info"] = token_info
        print("New token info saved to session")

        expires_at = token_info.get("expires_at", 0)
        print("New token expires at: ", expires_at)

    else:
        print("Token is still valid.")
        print("\nToken info: ", token_info)

    return Spotify(auth=token_info["access_token"])


# -----------------------------------------
