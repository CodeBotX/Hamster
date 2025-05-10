from django import forms
from .models import Song, Playlist

class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'file', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'audio/*'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PlaylistForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['songs'].queryset = Song.objects.filter(user=user)
        self.fields['songs'].widget = forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
        self.fields['songs'].required = False

    class Meta:
        model = Playlist
        fields = ['name', 'description', 'songs', 'cover_image', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('Playlist name is required.')
        return cleaned_data

class SongCoverForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['cover']
        widgets = {
            'cover': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        } 