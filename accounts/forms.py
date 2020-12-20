from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Puzzler


class PuzzlerCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(PuzzlerCreationForm, self).__init__(*args, **kwargs)

        for field_id in self.fields:
            self.fields[field_id].widget.attrs = {"class": "form-control"}

    class Meta:
        model = Puzzler
        fields = ("username", "email")


class PuzzlerChangeForm(UserChangeForm):
    class Meta:
        model = Puzzler
        fields = ("username", "email")
