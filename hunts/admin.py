from django.contrib import admin
from .models import Hunt, GoogleInfo


class HuntAdmin(admin.ModelAdmin):
    pass


class GoogleInfoAdmin(admin.ModelAdmin):
    pass


admin.site.register(Hunt, HuntAdmin)
admin.site.register(GoogleInfo, GoogleInfoAdmin)
