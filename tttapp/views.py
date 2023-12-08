# views.py

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


from django.shortcuts import redirect, render
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .models import TrendingTracks

import time

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

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
    sp_oauth = get_spotify_oauth()
    code = request.GET.get("code")
    print("Code: ", code)
    token_info = sp_oauth.get_access_token(code)
    request.session["token_info"] = token_info  # Store token info in the session
    return redirect("home")


# -----------------------------------------


def get_spotipy_client(request):
    token_info = request.session.get("token_info", {})
    if not token_info:
        print("No token info")
        return None

    if time.time() > token_info["expires_at"]:
        sp_oauth = get_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        print("Refresh token: ", token_info)
        request.session["token_info"] = token_info

    return Spotify(auth=token_info["access_token"])


# -----------------------------------------

from .spotify_utils import fetch_top_tracks


def top_tracks(request, time_range, name, offset=0):
    sp = get_spotipy_client(request)
    if not sp:
        return redirect("spotify_auth")

    offset = int(offset)
    tracks = fetch_top_tracks(sp, time_range, limit=4, offset=offset)
    print("Tracks in")

    return render(
        request,
        "top_tracks.html",
        {
            "name": name,
            "tracks": tracks,
            "next_offset": offset + 10,
            "time_range": time_range,
        },
    )


# -----------------------------------------


def top_tracks_short_term(request):
    offset = request.GET.get("offset", 0)
    return top_tracks(request, "short_term", "Top 10 Short Term", offset)


# -----------------------------------------


def top_tracks_medium_term(request):
    offset = request.GET.get("offset", 0)
    return top_tracks(request, "medium_term", "Top 10 Medium Term", offset)


# -----------------------------------------


def top_tracks_long_term(request):
    offset = request.GET.get("offset", 0)
    return top_tracks(request, "long_term", "Top 10 Long Term", offset)


# -----------------------------------------


@login_required
def home(request):
    name = "Welcome to Top Track Tracker"
    return render(request, "home.html", {"name": name})


# -----------------------------------------


def add_to_trending(request):
    if request.method == "POST":
        artist_name = request.POST.get("artist")
        song_name = request.POST.get("song")
        uri = request.POST.get("uri")
        release_year = request.POST.get("release_year")
        popularity = request.POST.get("popularity")
        album = request.POST.get("album")
        genres = request.POST.get("genres")
        energy = request.POST.get("energy")
        key = request.POST.get("key")
        valence = request.POST.get("valence")
        mood = request.POST.get("mood")
        tempo = request.POST.get("tempo")
        artist_uri = request.POST.get("artist_uri")

        # Check if the entry with the same URI already exists
        if TrendingTracks.objects.filter(uri=uri).exists():
            return JsonResponse({"success": False, "message": "Already added"})
        else:
            TrendingTracks.objects.create(
                artist=artist_name,
                song=song_name,
                uri=uri,
                release_year=release_year,
                popularity=popularity,
                album=album,
                genres=genres,
                energy=energy,
                key=key,
                valence=valence,
                mood=mood,
                tempo=tempo,
                artist_uri=artist_uri,
            )
            return JsonResponse({"success": True, "message": "Added track"})

    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)


# -----------------------------------------


def view_trending_tracks(request):
    trending_tracks = TrendingTracks.objects.all().order_by("-id")
    # trending_tracks = TrendingTracks.objects.all()

    name = "Trending Tracks"
    return render(
        request,
        "trending_tracks.html",
        {"trending_tracks": trending_tracks, "name": name},
    )


# -----------------------------------------


@require_POST  # This view should only accept POST requests
def delete_trending_track(request, track_id):
    try:
        track = TrendingTracks.objects.get(id=track_id)
        track.delete()
    except TrendingTracks.DoesNotExist:
        pass

    return redirect("view_trending_tracks")


# -----------------------------------------
from django.urls import reverse


@require_POST  # This view should only accept POST requests
def delete_all_trending_tracks(request):
    # Delete all tracks
    TrendingTracks.objects.all().delete()

    return redirect(reverse("view_trending_tracks"))


# -----------------------------------------
import csv
from django.http import HttpResponse
from datetime import datetime


def export_trending_tracks(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type="text/csv")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="trending_tracks_{datetime.now().strftime("%Y-%m-%d")}.csv"'

    writer = csv.writer(response)
    # Write the headers to the CSV file.
    writer.writerow(
        [
            "Artist",
            "Song",
            "Album",
            "Release Year",
            "Popularity",
            "URI",
            "Genres",
            "Energy",
            "Key",
            "Valence",
            "Mood",
            "Tempo",
            "Artist URI",
        ]
    )

    # Fetch the TrendingTracks data and write to the CSV
    for track in TrendingTracks.objects.all():
        writer.writerow(
            [
                track.artist,
                track.song,
                track.album,
                track.release_year,
                track.popularity,
                track.uri,
                track.genres,
                track.energy,
                track.key,
                track.valence,
                track.mood,
                track.tempo,
                track.artist_uri,
            ]
        )

    return response


# -----------------------------------------


# def start_spotify_playback(request):
#     try:
#         # Get a list of available devices
#         devices = sp.devices()
#         device_list = devices["devices"]
#         device_id = device_list[0]["id"] if device_list else None

#         if device_id:
#             # Retrieve the URIs from TrendingTracks
#             trending_tracks = TrendingTracks.objects.all()
#             track_uris = [track.uri for track in trending_tracks]

#             # Reverse the order of track_uris
#             track_uris.reverse()

#             sp.start_playback(device_id=device_id, uris=track_uris)
#             return JsonResponse(
#                 {"success": True, "message": "Spotify playback started successfully."}
#             )
#         else:
#             return JsonResponse(
#                 {"success": False, "message": "No available devices found."}
#             )
#     except Exception as e:
#         return JsonResponse({"success": False, "message": str(e)})


def start_spotify_playback(request):
    sp = get_spotipy_client(request)
    if not sp:
        # Redirect to Spotify auth or handle the lack of a valid token
        return redirect("spotify_auth")

    device_id = None

    try:
        # Retrieve the URIs from TrendingTracks
        trending_tracks = TrendingTracks.objects.all()
        track_uris = [track.uri for track in trending_tracks]

        # Reverse the order of track_uris
        track_uris.reverse()

        offset = {"position": 0}
        position_ms = 0

        sp.start_playback(
            device_id=device_id, uris=track_uris, offset=offset, position_ms=position_ms
        )
        return JsonResponse(
            {
                "success": True,
                "message": "Spotify playback started successfully (views)",
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
