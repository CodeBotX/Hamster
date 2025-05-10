from django.contrib import admin
from .models import Song, Playlist

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'is_public')
    list_filter = ('user', 'is_public', 'created_at')
    search_fields = ('title',)

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'parent', 'created_at', 'is_public')
    list_filter = ('user', 'is_public', 'created_at')
    search_fields = ('name', 'description')
