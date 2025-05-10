from django.db import models
from PIL import Image
import os
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.

class Album(models.Model):
    name = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField(blank=True)
    cover_photo = models.ImageField(upload_to='albums/covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        if self.name:
            return self.name
        return f"Album created on {self.created_at.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.name:
            super().save(*args, **kwargs)
            self.name = f"Album {self.created_at.strftime('%Y-%m-%d %H:%M')}"
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def get_post_count(self):
        return self.posts.count()

    def get_photo_count(self):
        return Photo.objects.filter(post__album=self).count()

class Post(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['album', '-created_at']),
        ]

    def __str__(self):
        return self.title

    def get_like_count(self):
        return self.likes.count()

    def get_comment_count(self):
        return self.comments.count()

    def get_photo_count(self):
        return self.photos.count()

    def clean(self):
        # Ensure the user creating the post owns the album
        if self.user != self.album.user:
            raise ValidationError("You can only create posts in your own albums.")

class Photo(models.Model):
    image = models.ImageField(upload_to='photos/%Y/%m/%d/')
    thumbnail = models.ImageField(upload_to='photos/thumbnails/%Y/%m/%d/', blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='photos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position', 'created_at']
        indexes = [
            models.Index(fields=['post', 'position']),
        ]

    def __str__(self):
        return f"Photo {self.id} in {self.post.title}"

    def save(self, *args, **kwargs):
        # Set position to last if not specified
        if not self.position and not Photo.objects.filter(post=self.post).exists():
            self.position = 0
        elif not self.position:
            self.position = Photo.objects.filter(post=self.post).order_by('-position').first().position + 1

        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Create thumbnail only for new photos
        if is_new and self.image:
            try:
                img = Image.open(self.image.path)
                
                # Create thumbnail
                if img.width > 800 or img.height > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size)
                    thumb_filename = f'thumb_{os.path.basename(self.image.name)}'
                    thumb_path = os.path.join('photos/thumbnails', 
                                            timezone.now().strftime('%Y/%m/%d'),
                                            thumb_filename)
                    full_thumb_path = os.path.join('media', thumb_path)
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(full_thumb_path), exist_ok=True)
                    
                    # Save thumbnail
                    img.save(full_thumb_path, quality=85, optimize=True)
                    self.thumbnail = thumb_path
                    super().save(update_fields=['thumbnail'])
                    
                # Update album cover if this is the first photo
                if not self.post.album.cover_photo:
                    self.post.album.cover_photo = self.image
                    self.post.album.save()
                    
            except Exception as e:
                print(f"Error processing image: {e}")

    def clean(self):
        # Ensure the user creating the photo owns the post
        if self.post.user != self.post.album.user:
            raise ValidationError("You can only add photos to your own posts.")

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.title}'

    def get_reply_count(self):
        return self.replies.count()
