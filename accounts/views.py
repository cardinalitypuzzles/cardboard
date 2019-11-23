from django.shortcuts import render
from .forms import PuzzlerCreationForm
from django.urls import reverse_lazy
from django.views import generic


class SignUp(generic.CreateView):
    form_class = PuzzlerCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'