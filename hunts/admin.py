from django.contrib import admin
from .models import Hunt


class HuntAdmin(admin.ModelAdmin):
    pass


admin.site.register(Hunt, HuntAdmin)
