# spotify_utils.py


def fetch_top_tracks(sp, time_range, limit, offset):
    print("Fetching top tracks")
    results = sp.current_user_top_tracks(
        time_range=time_range, limit=limit, offset=offset
    )
    print("Fetched top tracks")
    tracks = process_spotify_results(sp, results)

    add_audio_features_to_tracks(sp, tracks)

    return tracks


# -----------------------------------------


def add_audio_features_to_tracks(sp, tracks):
    audio_features = sp.audio_features([track["uri"] for track in tracks])
    for i, track_info in enumerate(tracks):
        if audio_features[i]:
            valence, mood = valence_to_mood(audio_features[i]["valence"])
            energy = energy_to_category(audio_features[i]["energy"])
            track_info.update(
                {
                    "energy": energy,
                    "key": audio_features[i]["key"],
                    "valence": valence,
                    "mood": mood,
                    "tempo": round(audio_features[i]["tempo"], 1),
                }
            )


# -----------------------------------------


def energy_to_category(energy):
    if energy <= 0.2:
        return "Subdued"
    elif energy <= 0.4:
        return "Low Energy"
    elif energy <= 0.6:
        return "Middling"
    elif energy <= 0.8:
        return "Upbeat"
    else:
        return "High Energy"

    # -----------------------------------------


def valence_to_mood(valence):
    if valence <= 0.2:
        return (valence, "Depressed")
    elif valence <= 0.4:
        return (valence, "Sad")
    elif valence <= 0.6:
        return (valence, "Calm")
    elif valence <= 0.8:
        return (valence, "Happy")
    else:
        return (valence, "Energetic")


# -----------------------------------------


def get_artist_genres(sp, artist_id):
    # Fetch artist details
    artist_info = sp.artist(artist_id)

    # Get genres and convert each genre to title case
    genres = [genre.title() for genre in artist_info.get("genres", [])]

    return genres if genres else ["Not given"]


# -----------------------------------------


def process_spotify_results(sp, results):
    print("Processing results")
    list_of_results = results["items"]
    tracks = []
    print("Processing each result")

    for result in list_of_results:
        track_info = extract_track_info(sp, result)
        tracks.append(track_info)

    print("Processed results")
    return tracks


# -----------------------------------------


def extract_track_info(sp, result):
    release_year = (
        result["album"]["release_date"].split("-")[0]
        if result["album"]["release_date"]
        else "Unknown"
    )
    artist_id = result["artists"][0]["id"]
    genres = get_artist_genres(sp, artist_id)

    return {
        "artist": " & ".join(artist["name"] for artist in result["artists"]),
        "artist_uri": result["artists"][0]["uri"],
        "song": result["name"].title(),
        "uri": result["uri"],
        "release_year": release_year,
        "album": result["album"]["name"],
        "track_number": result["track_number"],
        "popularity": result["popularity"],
        "genres": " / ".join(genres),
    }


# -----------------------------------------
