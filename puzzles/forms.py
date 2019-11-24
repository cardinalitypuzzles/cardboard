from django import forms

class PuzzleForm(forms.Form):
    name = forms.CharField(
        max_length=128,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Name of Puzzle"
        })
    )
    url = forms.URLField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "URL"
        })
    )
    is_meta = forms.BooleanField(required=False)