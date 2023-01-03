"""Cardboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),
    path("hunts/", include("hunts.urls")),
    path("answers/", include("answers.urls")),
    path("api/", include("api.urls")),
    path("puzzles/", include("puzzles.urls")),
    path("tools", views.tools, name="tools"),
    path("privacy", views.privacy, name="privacy"),
    path("", views.home, name="home"),
    path("", include("social_django.urls", namespace="social")),
]
