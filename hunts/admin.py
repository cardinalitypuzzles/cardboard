from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Hunt, HuntSettings


class HuntSettingsInline(admin.StackedInline):
    model = HuntSettings


class HuntAdmin(GuardedModelAdmin):
    inlines = [
        HuntSettingsInline,
    ]


admin.site.register(Hunt, HuntAdmin)
