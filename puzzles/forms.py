from django import forms

class PuzzleForm(forms.Form):
    name = forms.CharField(
        max_length=128,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Name of Puzzle"
        })
    )
    url = forms.URLField()