# views.py


from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages

# from django.conf import settings
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit

from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.http import HttpResponse

from .models import TrendingTracks

# import time

# from spotipy import Spotify
# from spotipy.oauth2 import SpotifyOAuth

# -----------------------------------------
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import time
from django.conf import settings
from django.shortcuts import redirect


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
    print("Code: ", code)
    token_info = sp_oauth.get_access_token(code)
    request.session["token_info"] = token_info
    print("Token info: ", token_info)
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

from .spotify_client import (
    get_spotipy_client,
    get_spotify_oauth,
    spotify_auth,
    spotify_callback,
)
from .spotify_utils import fetch_top_tracks
from .user_utils import user_or_ip, rate


# @ratelimit(key="user_or_ip", rate=rate, block=True)


def custom_ratelimit(*args, **kwargs):
    def decorator(func):
        @ratelimit(*args, **kwargs)
        def _wrapped_view(request, *args, **kwargs):
            if getattr(request, "limited", False):
                print("Rate limit exceeded")
                return HttpResponse(
                    "Rate limit exceeded. Please try again later.", status=429
                )
            return func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


@custom_ratelimit(key="user_or_ip", rate=rate)
def top_tracks(request, time_range, name, context):
    sp = get_spotipy_client(request)
    if not sp:
        print("No spotipy client")
        return redirect("spotify_auth")

    offset = int(context["offset"])
    tracks = fetch_top_tracks(sp, time_range, limit=2, offset=offset)
    print("Tracks in")

    return render(
        request,
        "top_tracks.html",
        {
            "name": name,
            "tracks": tracks,
            "next_offset": context["next_offset"],
            "back_offset": offset - 10 if offset > 0 else 0,
            "show_back": context["show_back"],
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


@login_required
def home(request):
    name = "Welcome to the Top Track Tracker"

    lastfm_api_key = settings.LASTFM_API_KEY
    lastfm_username = settings.LASTFM_USERNAME

    lastfm = lastfm_play_count(lastfm_username, lastfm_api_key)
    print("Play counts: ", len(lastfm))
    if lastfm:  # Check if there are tracks in the list
        print("Example track name: ", lastfm[20]["name"])

    return render(request, "home.html", {"name": name, "lastfm": lastfm})


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
            return JsonResponse({"success": False, "message": "\u2717 Already exists"})
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
            return JsonResponse(
                {"success": True, "message": "\u2713 Added to trending"}
            )

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

from io import TextIOWrapper


from django.db import transaction


@require_POST  # This view should only accept POST requests
def upload_trending_tracks(request):
    new_records = []
    existing_uris = set()
    # records_added = 0

    # using the @require_POST decorator makes the check if request.method == "POST" redundant.
    # if request.method == "POST" and request.FILES.get("csv_file"):

    if request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "\u2717 Error: Not a CSV file")
            messages.add_message(request, messages.INFO, "Please try again")
            return redirect("view_trending_tracks")

        csv_file = TextIOWrapper(csv_file.file, encoding="utf-8")
        reader = csv.reader(csv_file)

        # Skip the header row
        next(reader, None)

        # Process the CSV data
        for row in reader:
            uri = row[5]
            new_records.append(
                TrendingTracks(
                    uri=uri,
                    artist=row[0],
                    song=row[1],
                    album=row[2],
                    release_year=row[3],
                    popularity=row[4],
                    genres=row[6],
                    energy=row[7],
                    key=row[8],
                    valence=row[9],
                    mood=row[10],
                    tempo=row[11],
                    artist_uri=row[12],
                )
            )
            existing_uris.add(uri)

        # Check which records already exist
        existing_records = TrendingTracks.objects.filter(
            uri__in=existing_uris
        ).values_list("uri", flat=True)
        existing_uris = set(existing_records)

        # Exclude existing records
        new_records_to_add = [
            record for record in new_records if record.uri not in existing_uris
        ]
        records_to_add_count = len(new_records_to_add)

        # Use bulk_create to add all new records at once
        with transaction.atomic():
            TrendingTracks.objects.bulk_create(new_records_to_add)
            records_added = records_to_add_count

        # Add success message with feedback
        messages.success(request, f"\u2713 CSV processed: {records_added} tracks added")
        messages.add_message(request, messages.WARNING, "Duplicates were ignored")

        return redirect("view_trending_tracks")

    else:
        messages.error(request, "Error: Invalid request or no file uploaded")
        return redirect("view_trending_tracks")


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

    # devices = sp.devices()
    # print("Devices: ", devices)
    # device_id = "23519aa963a0f6387f210264535162664dca6a1f"
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
            device_id=device_id,
            uris=track_uris,
            offset=offset,
            position_ms=position_ms,
        )
        return JsonResponse(
            {
                "success": True,
                "message": "Spotify playback started successfully (views)",
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


# -----------------------------------------

import requests


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

    return lastfm_info


# get play counts from last.fm
# def lastfm_play_count(username, api_key):
#     play_count_lst = []

#     try:
#         # Define the API endpoint for getting user's top tracks
#         endpoint = f"http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={username}&api_key={api_key}&format=json"

#         # Send a GET request to the Last.fm API
#         response = requests.get(endpoint)

#         # Check if the request was successful
#         if response.status_code == 200:
#             data = response.json()
#             top_tracks = data["toptracks"]["track"]

#             if top_tracks:
#                 for track in top_tracks:
#                     play_count_lst.append(track["playcount"])

#     except Exception as e:
#         print(f"An error occurred: {e}")

#     return play_count_lst
