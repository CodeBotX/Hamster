from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
from .models import Album, Post, Photo, Comment
from .forms import AlbumForm, PostForm, PhotoForm, CommentForm

class HomeView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'home.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.select_related('user', 'album')\
            .prefetch_related('photos', 'likes', 'comments')\
            .filter(album__user__in=[self.request.user])\
            .order_by('-created_at')

class AlbumListView(LoginRequiredMixin, ListView):
    model = Album
    template_name = 'gallery/album_list.html'
    context_object_name = 'albums'
    paginate_by = 12

    def get_queryset(self):
        return Album.objects.filter(user=self.request.user).order_by('-created_at')

class AlbumDetailView(LoginRequiredMixin, DetailView):
    model = Album
    template_name = 'gallery/album_detail.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object.posts.select_related('user')\
            .prefetch_related('photos', 'likes', 'comments')\
            .order_by('-created_at')
        return context

class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = Album
    form_class = AlbumForm
    template_name = 'gallery/create_album.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Album created successfully!')
        return response

    def get_success_url(self):
        return reverse('gallery:album_detail', kwargs={'pk': self.object.pk})

@login_required
def create_post(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    if album.user != request.user:
        raise PermissionDenied("You can only create posts in your own albums.")

    if request.method == 'POST':
        post_form = PostForm(request.POST, album=album, user=request.user)
        photo_form = PhotoForm(request.POST, request.FILES)
        
        if post_form.is_valid():
            # Create post first
            post = post_form.save()
            
            # Handle multiple photo uploads
            files = request.FILES.getlist('image')
            if files:  # Only process photos if files were uploaded
                for index, file in enumerate(files):
                    Photo.objects.create(
                        image=file,
                        post=post,
                        position=index
                    )
            
            messages.success(request, 'Post created successfully!')
            return redirect('gallery:album_detail', pk=album.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        post_form = PostForm(album=album, user=request.user)
        photo_form = PhotoForm()

    return render(request, 'gallery/create_post.html', {
        'post_form': post_form,
        'photo_form': photo_form,
        'album': album
    })

@login_required
def like_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        
        return JsonResponse({
            'liked': liked,
            'like_count': post.likes.count()
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        text = request.POST.get('text', '').strip()
        
        if text:
            comment = Comment.objects.create(
                post=post,
                user=request.user,
                text=text
            )
            
            return JsonResponse({
                'success': True,
                'user': request.user.username,
                'comment_count': post.comments.count()
            })
        
        return JsonResponse({'error': 'Comment cannot be empty'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    
    def test_func(self):
        post = self.get_object()
        return post.user == self.request.user
    
    def get_success_url(self):
        return reverse('gallery:album_detail', kwargs={'pk': self.object.album.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Post deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def reorder_photos(request, post_id):
    if request.method == 'POST' and request.is_ajax():
        post = get_object_or_404(Post, pk=post_id)
        if post.user != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        photo_ids = request.POST.getlist('photo_ids[]')
        for index, photo_id in enumerate(photo_ids):
            Photo.objects.filter(pk=photo_id, post=post).update(position=index)
        
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def delete_album(request, pk):
    album = get_object_or_404(Album, pk=pk)
    if request.user != album.user:
        messages.error(request, "You don't have permission to delete this album.")
        return redirect('gallery:album_detail', pk=pk)
    
    if request.method == 'POST':
        album.delete()
        messages.success(request, "Album deleted successfully.")
        return redirect('gallery:album_list')
    
    return render(request, 'gallery/confirm_delete.html', {
        'object': album,
        'type': 'album'
    })

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.user:
        messages.error(request, "You don't have permission to delete this post.")
        return redirect('gallery:album_detail', pk=post.album.pk)
    
    if request.method == 'POST':
        album_pk = post.album.pk
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect('gallery:album_detail', pk=album_pk)
    
    return render(request, 'gallery/confirm_delete.html', {
        'object': post,
        'type': 'post'
    })

@login_required
def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    if request.user != photo.post.user:
        messages.error(request, "You don't have permission to delete this photo.")
        return redirect('gallery:album_detail', pk=photo.post.album.pk)
    
    if request.method == 'POST':
        post_pk = photo.post.pk
        photo.delete()
        messages.success(request, "Photo deleted successfully.")
        return redirect('gallery:post_detail', post_id=post_pk)
    
    return render(request, 'gallery/confirm_delete.html', {
        'object': photo,
        'type': 'photo'
    })

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.user:
        messages.error(request, "You don't have permission to delete this comment.")
        return redirect('gallery:album_detail', pk=comment.post.album.pk)
    
    if request.method == 'POST':
        post_pk = comment.post.pk
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
        return redirect('gallery:post_detail', post_id=post_pk)
    
    return render(request, 'gallery/confirm_delete.html', {
        'object': comment,
        'type': 'comment'
    })

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'gallery/post_detail.html', {'post': post})
