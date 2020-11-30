from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def privacy(request):
    return render(request, "privacy.html")


@login_required(login_url="/accounts/login/")
def tools(request):
    return render(request, "tools.html")
