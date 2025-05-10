from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Song, Playlist
from .forms import SongForm, PlaylistForm, SongCoverForm
from django.views.decorators.http import require_http_methods

def index(request):
    playlists = Playlist.objects.filter(user=request.user, parent=None)
    return render(request, 'music/index.html', {
        'playlists': playlists
    })

def song_detail(request, pk):
    song = get_object_or_404(Song, pk=pk)
    if not song.is_public and request.user != song.user:
        messages.error(request, 'You do not have permission to view this song.')
        return redirect('music:index')
    return render(request, 'music/song_detail.html', {'song': song})

def playlist_detail(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    if not playlist.is_public and request.user != playlist.user:
        messages.error(request, 'You do not have permission to view this playlist.')
        return redirect('music:index')
    
    sub_playlists = playlist.sub_playlists.all()
    songs = playlist.songs.all()
    return render(request, 'music/playlist_detail.html', {
        'playlist': playlist,
        'sub_playlists': sub_playlists,
        'songs': songs
    })

@login_required
def upload_song(request, playlist_pk=None):
    playlist = None
    if playlist_pk:
        playlist = get_object_or_404(Playlist, pk=playlist_pk, user=request.user)
    
    if request.method == 'POST':
        form = SongForm(request.POST, request.FILES)
        if form.is_valid():
            song = form.save(commit=False)
            song.user = request.user
            song.save()
            if playlist:
                playlist.songs.add(song)
            messages.success(request, 'Song uploaded successfully!')
            return redirect('music:playlist_detail', pk=playlist_pk) if playlist else redirect('music:index')
    else:
        form = SongForm()
    return render(request, 'music/upload_song.html', {
        'form': form,
        'playlist': playlist
    })

@login_required
def create_playlist(request, parent_pk=None):
    parent = None
    if parent_pk:
        parent = get_object_or_404(Playlist, pk=parent_pk, user=request.user)
    
    if request.method == 'POST':
        form = PlaylistForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.parent = parent
            playlist.save()
            messages.success(request, 'Playlist created successfully!')
            return redirect('music:playlist_detail', pk=parent_pk) if parent else redirect('music:index')
    else:
        form = PlaylistForm(request.user)
    return render(request, 'music/create_playlist.html', {
        'form': form,
        'parent': parent
    })

@login_required
def play_all(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    if not playlist.is_public and request.user != playlist.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    songs = playlist.get_all_songs()
    song_data = [{
        'title': song.title,
        'url': song.file.url
    } for song in songs]
    
    return JsonResponse({'songs': song_data})

@login_required
def play_song(request, pk):
    song = get_object_or_404(Song, pk=pk)
    if not song.is_public and request.user != song.user:
        messages.error(request, 'You do not have permission to view this song.')
        return redirect('music:index')
    if request.method == 'POST':
        form = SongCoverForm(request.POST, request.FILES, instance=song)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cover updated successfully!')
            return redirect('music:play_song', pk=song.pk)
    else:
        form = SongCoverForm(instance=song)
    return render(request, 'music/play_song.html', {'song': song, 'cover_form': form})

class SongUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Song
    form_class = SongForm
    template_name = 'music/upload_song.html'
    success_url = reverse_lazy('music:index')

    def test_func(self):
        song = self.get_object()
        return self.request.user == song.user

class SongDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Song
    success_url = reverse_lazy('music:index')
    template_name = 'music/song_confirm_delete.html'

    def test_func(self):
        song = self.get_object()
        return self.request.user == song.user

class PlaylistUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Playlist
    form_class = PlaylistForm
    template_name = 'music/create_playlist.html'
    success_url = reverse_lazy('music:index')

    def test_func(self):
        playlist = self.get_object()
        return self.request.user == playlist.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class PlaylistDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Playlist
    success_url = reverse_lazy('music:index')
    template_name = 'music/playlist_confirm_delete.html'

    def test_func(self):
        playlist = self.get_object()
        return self.request.user == playlist.user
