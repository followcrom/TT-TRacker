from django.db import models


class TrendingTracks(models.Model):
    """
    TrendingTracks is a Django model.

    This model stores information about tracks that users mark as 'trending' in the application.
    It is used to keep a record of popular or frequently played tracks based on user interaction.

    Attributes:
        artist
        song
        album
        release_year
        popularity
        uri
        genres
        energy
        key
        valence
        mood
        tempo
        artist_uri

    The 'uri' field is particularly important as it provides a unique identifier for each track, enabling easy reference to the specific track on Spotify.
    """

    artist = models.CharField(max_length=200)
    song = models.CharField(max_length=200)
    album = models.CharField(max_length=200)
    release_year = models.CharField(max_length=200)
    popularity = models.CharField(max_length=200)
    uri = models.CharField(max_length=200)
    genres = models.CharField(max_length=200)
    energy = models.CharField(max_length=200)
    key = models.CharField(max_length=200)
    valence = models.CharField(max_length=200)
    mood = models.CharField(max_length=200)
    tempo = models.CharField(max_length=200)
    artist_uri = models.CharField(max_length=200)
