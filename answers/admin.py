from django.contrib import admin
from .models import Answer


class AnswerAdmin(admin.ModelAdmin):
    list_display = ["text", "puzzle", "status", "response"]
    list_filter = ["puzzle__hunt", "status"]


admin.site.register(Answer, AnswerAdmin)
