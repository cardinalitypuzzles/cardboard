from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Puzzler

class PuzzlerCreationForm(UserCreationForm):
    class Meta:
        model = Puzzler
        fields = ('username', 'email')

class PuzzlerChangeForm(UserChangeForm):
    class Meta:
        model = Puzzler
        fields = ('username', 'email')
