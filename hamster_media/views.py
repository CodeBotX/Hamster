from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from gallery.models import Post, Comment
from django.core.cache import cache

@login_required
def like_post(request, post_id):
    if request.method == 'POST':
        # Create a unique key for this user and post
        cache_key = f'like_post_{request.user.id}_{post_id}'
        
        # Check if this request is already being processed
        if cache.get(cache_key):
            return JsonResponse({'error': 'Request already being processed'}, status=400)
            
        # Set the flag
        cache.set(cache_key, True, timeout=1)  # 1 second timeout
        
        try:
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
        finally:
            # Clear the flag
            cache.delete(cache_key)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        # Create a unique key for this user and post
        cache_key = f'add_comment_{request.user.id}_{post_id}'
        
        # Check if this request is already being processed
        if cache.get(cache_key):
            return JsonResponse({'error': 'Request already being processed'}, status=400)
            
        # Set the flag
        cache.set(cache_key, True, timeout=1)  # 1 second timeout
        
        try:
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
        finally:
            # Clear the flag
            cache.delete(cache_key)
    return JsonResponse({'error': 'Invalid request'}, status=400) 