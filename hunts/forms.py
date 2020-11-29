from django import forms


class HuntForm(forms.Form):
    name = forms.CharField(
        max_length=128,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Name of Hunt"}
        ),
    )
    url = forms.URLField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "URL"})
    )
