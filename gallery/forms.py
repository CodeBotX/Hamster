from django import forms
from .models import Album, Photo, Post, Comment

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['name', 'description', 'cover_photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'cover_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.album = kwargs.pop('album', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.album:
            self.instance.album = self.album
        if self.user:
            self.instance.user = self.user

class PhotoForm(forms.ModelForm):
    image = MultipleFileField(
        widget=MultipleFileInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Photo
        fields = ['image']

    def __init__(self, *args, **kwargs):
        self.album = kwargs.pop('album', None)
        super().__init__(*args, **kwargs)
        if self.album:
            self.instance.album = self.album

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
        } 