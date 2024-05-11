# views.py

from django.shortcuts import redirect, render

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django_ratelimit.decorators import ratelimit

from django.views.decorators.http import require_POST


# -----------------------------------------

from .spotify_client import get_spotipy_client
from .spotify_utils import fetch_top_tracks
from .user_utils import rate


@ratelimit(key="user", rate=rate, block=True)
def top_tracks(request, time_range, name, context):
    request.session["pre_auth_url"] = request.get_full_path()
    print(f"Session pre_auth_url set to: {request.session['pre_auth_url']}")
    request.session.modified = True

    sp = get_spotipy_client(request)

    if not sp:
        print("No spotipy client. Running spotify_callback()")
        return redirect("spotify_auth")

    offset = int(context["offset"])
    limit = 10
    total_tracks = 50
    show_forward = True

    if offset + limit <= total_tracks:
        tracks = fetch_top_tracks(sp, time_range, limit=limit, offset=offset)
        print("Tracks in.")

        if offset >= 40:
            show_forward = False

    else:
        tracks = []
        show_forward = False

    return render(
        request,
        "top_tracks.html",
        {
            "name": name,
            "tracks": tracks if tracks else [],
            "next_offset": context["next_offset"],
            "back_offset": offset - 10 if offset > 0 else 0,
            "show_back": context["show_back"],
            "show_forward": show_forward,
            "time_range": time_range,
        },
    )

# -----------------------------------------


def top_tracks_short_term(request):
    offset = int(request.GET.get("offset", 0))
    limit = 10

    next_offset = offset + limit

    show_back = offset > 0

    context = {
        "offset": offset,
        "next_offset": next_offset,
        "show_back": show_back,
    }

    return top_tracks(request, "short_term", "Top 10 Short Term", context)


# -----------------------------------------


def top_tracks_medium_term(request):
    offset = int(request.GET.get("offset", 0))
    limit = 10

    next_offset = offset + limit

    show_back = offset > 0

    context = {
        "offset": offset,
        "next_offset": next_offset,
        "show_back": show_back,
    }

    return top_tracks(request, "medium_term", "Top 10 Medium Term", context)


# -----------------------------------------


def top_tracks_long_term(request):
    offset = int(request.GET.get("offset", 0))
    limit = 10

    next_offset = offset + limit

    show_back = offset > 0

    context = {
        "offset": offset,
        "next_offset": next_offset,
        "show_back": show_back,
    }

    return top_tracks(request, "long_term", "Top 10 Long Term", context)


# -----------------------------------------
from django.conf import settings

# @login_required
def home(request):
    welcome = "Welcome to the Top Track Tracker"

    lastfm_api_key = settings.LASTFM_API_KEY
    lastfm_username = settings.LASTFM_USERNAME

    lastfm = lastfm_play_count(lastfm_username, lastfm_api_key)

    return render(request, "home.html", {"welcome": welcome, "lastfm": lastfm})

# -----------------------------------------

import requests
import logging


def lastfm_play_count(username, api_key):
    lastfm_info = []

    try:
        # Define the API endpoint for getting user's top tracks
        endpoint = f"http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={username}&api_key={api_key}&format=json"

        # Send a GET request to the Last.fm API
        response = requests.get(endpoint)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            top_tracks = data["toptracks"]["track"]

            # Extract the desired information for each track
            for track in top_tracks:
                track_info = {
                    "name": track.get("name", ""),
                    "artist": track.get("artist", {}).get("name", ""),
                    "playcount": track.get("playcount", "0"),
                }
                lastfm_info.append(track_info)

    except Exception as e:
        print(f"An error occurred: {e}")
        # Log the error to the console
        logging.error(f"An error occurred: {e}")

    return lastfm_info
