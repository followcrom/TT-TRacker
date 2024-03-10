from django.db import models


class TrendingTracks(models.Model):
    """

    This model stores information about tracks that are marked as 'Trending'.

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
