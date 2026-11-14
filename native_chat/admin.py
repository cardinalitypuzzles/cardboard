from django.contrib import admin

from .models import CardboardNativeChatMessage


class CardboardNativeChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "puzzle", "user", "text", "image_content_type", "created_on")
    exclude = ["image"]


admin.site.register(CardboardNativeChatMessage, CardboardNativeChatMessageAdmin)
