from django.contrib import admin
from .models import Album, Photo, Post, Comment

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'album', 'user', 'created_at')
    list_filter = ('album', 'user')
    search_fields = ('title', 'description')

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'created_at')
    list_filter = ('post',)
    search_fields = ('post__title',)
    readonly_fields = ('thumbnail',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'text', 'created_at')
    list_filter = ('post', 'user')
    search_fields = ('text', 'user__username')
