from django.db import models
from django.contrib.auth.models import User
from mutagen import File
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import os

class Playlist(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    songs = models.ManyToManyField('Song', related_name='playlists')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_playlists')
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    cover_image = models.ImageField(upload_to='playlist_covers/', null=True, blank=True)

    def __str__(self):
        return self.name

    def get_path(self):
        path = [self.name]
        current = self.parent
        while current:
            path.insert(0, current.name)
            current = current.parent
        return path

    def get_all_songs(self):
        songs = list(self.songs.all())
        for sub_playlist in self.sub_playlists.all():
            songs.extend(sub_playlist.get_all_songs())
        return songs

class Song(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='music/')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='songs')
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    cover = models.ImageField(upload_to='song_covers/', null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
