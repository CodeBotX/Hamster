from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    # Home and Album views
    path('', views.HomeView.as_view(), name='home'),
    path('albums/', views.AlbumListView.as_view(), name='album_list'),
    path('albums/create/', views.AlbumCreateView.as_view(), name='create_album'),
    path('albums/<int:pk>/', views.AlbumDetailView.as_view(), name='album_detail'),
    path('albums/<int:pk>/delete/', views.delete_album, name='delete_album'),
    
    # Post management
    path('albums/<int:album_id>/post/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    
    # Post interactions
    path('posts/<int:post_id>/like/', views.like_post, name='like_post'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/reorder/', views.reorder_photos, name='reorder_photos'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # Photo management
    path('posts/<int:post_id>/photos/<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),
] 