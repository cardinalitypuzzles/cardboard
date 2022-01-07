from django.contrib import admin
from .models import Hunt, HuntSettings


class HuntSettingsInline(admin.StackedInline):
    model = HuntSettings


class HuntAdmin(admin.ModelAdmin):
    inlines = [
        HuntSettingsInline,
    ]


admin.site.register(Hunt, HuntAdmin)
