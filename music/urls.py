from django.urls import path
from . import views

app_name = 'music'

urlpatterns = [
    path('', views.index, name='index'),
    path('playlist/<int:pk>/', views.playlist_detail, name='playlist_detail'),
    path('playlist/<int:pk>/update/', views.PlaylistUpdateView.as_view(), name='playlist_update'),
    path('playlist/<int:pk>/delete/', views.PlaylistDeleteView.as_view(), name='playlist_delete'),
    path('playlist/<int:pk>/play-all/', views.play_all, name='play_all'),
    path('playlist/create/', views.create_playlist, name='create_playlist'),
    path('playlist/<int:parent_pk>/create/', views.create_playlist, name='create_sub_playlist'),
    path('playlist/<int:playlist_pk>/upload/', views.upload_song, name='upload_song'),
    path('song/<int:pk>/delete/', views.SongDeleteView.as_view(), name='song_delete'),
    path('play/<int:pk>/', views.play_song, name='play_song'),
] 