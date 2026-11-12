from django.contrib import admin

from .models import CardboardNativeChat, CardboardNativeChatMessage


class CardboardNativeChatAdmin(admin.ModelAdmin):
    list_display = ("id", "puzzle", "created_on")


class CardboardNativeChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "user", "text", "image_content_type", "created_on")
    exclude = ["image"]


admin.site.register(CardboardNativeChat, CardboardNativeChatAdmin)
admin.site.register(CardboardNativeChatMessage, CardboardNativeChatMessageAdmin)
