from django.contrib import admin
from django_softdelete.admin import GlobalObjectsModelAdmin

from .models import ChatRole, ChatRoom


class ChatRoleAdmin(admin.ModelAdmin):
    list_display = ["hunt", "name", "role_id"]
    list_filter = ["hunt"]


admin.site.register(ChatRoom, GlobalObjectsModelAdmin)
admin.site.register(ChatRole, ChatRoleAdmin)
