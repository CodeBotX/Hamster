from django import forms
from .models import Song, Playlist

class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'file', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'audio/*'}),
        }

class PlaylistForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['songs'].queryset = Song.objects.filter(user=user)

    class Meta:
        model = Playlist
        fields = ['name', 'description', 'songs', 'cover_image', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

class SongCoverForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['cover'] 