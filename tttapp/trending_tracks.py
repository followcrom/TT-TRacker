from django.http import JsonResponse
from django.http import HttpResponse

from .models import TrendingTracks

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from .spotify_client import get_spotipy_client


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

    name = "Trending Tracks"
    return render(
        request,
        "trending_tracks.html",
        {"trending_tracks": trending_tracks, "name": name},
    )


# -----------------------------------------


@require_POST
def delete_trending_track(request, track_id):
    try:
        track = TrendingTracks.objects.get(id=track_id)
        track.delete()
    except TrendingTracks.DoesNotExist:
        pass

    return redirect("view_trending_tracks")


# -----------------------------------------
from django.urls import reverse


@require_POST
def delete_all_trending_tracks(request):
    TrendingTracks.objects.all().delete()

    return redirect("view_trending_tracks")


# -----------------------------------------
import csv
from django.http import HttpResponse
from datetime import datetime
import io


def export_trending_tracks(request):
    # Create a buffer to hold CSV data
    buffer = io.StringIO()
    print(type(buffer))

    writer = csv.writer(buffer)
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

    # Prepare the response
    response = HttpResponse(
        buffer.getvalue().encode("utf-8"),
        content_type="text/csv; charset=utf-8",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="trending_tracks_{datetime.now().strftime("%Y-%m-%d")}.csv"'
    )

    buffer.close()
    return response


# -----------------------------------------

from io import TextIOWrapper
from django.db import transaction

@require_POST
def upload_trending_tracks(request):
    uploads = []
    existing_uris = set(TrendingTracks.objects.values_list("uri", flat=True))

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

        for row in reader:
            uri = row[5]

            # Check if the URI is not already in the database
            if uri not in existing_uris:
                uploads.append(
                    TrendingTracks(
                        artist=row[0],
                        song=row[1],
                        album=row[2],
                        release_year=row[3],
                        popularity=row[4],
                        uri=uri,
                        genres=row[6],
                        energy=row[7],
                        key=row[8],
                        valence=row[9],
                        mood=row[10],
                        tempo=row[11],
                        artist_uri=row[12],
                    )
                )

        with transaction.atomic():
            TrendingTracks.objects.bulk_create(uploads)

        num_uploads = len(uploads)
        messages.success(request, f"\u2713 CSV processed: {num_uploads} tracks added")
        messages.add_message(request, messages.WARNING, "Duplicates were ignored")

    else:
        messages.error(request, "Error: Invalid request or no file uploaded")

    return redirect("view_trending_tracks")


# -----------------------------------------


def start_spotify_playback(request):
    sp = get_spotipy_client(request)
    if not sp:
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
                "message": "Spotify playback started successfully",
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})