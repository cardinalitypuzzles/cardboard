from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import PuzzlerChangeForm, PuzzlerCreationForm
from .models import Puzzler


class PuzzlerAdmin(UserAdmin):
    add_form = PuzzlerCreationForm
    form = PuzzlerChangeForm
    model = Puzzler
    list_display = [
        "email",
        "username",
    ]


admin.site.register(Puzzler, PuzzlerAdmin)
