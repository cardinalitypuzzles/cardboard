from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from hunts.views import LastAccessedHuntRedirectView


def privacy(request):
    return render(request, "privacy.html")


@login_required(login_url="/")
def tools(request):
    return render(request, "tools.html")


def home(request):
    if request.user.is_authenticated:
        return LastAccessedHuntRedirectView.as_view()(request)
    else:
        return render(request, "home.html")
