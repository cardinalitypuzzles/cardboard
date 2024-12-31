from django.contrib import admin
from django_softdelete.admin import hard_delete_selected_items

from answers.models import Answer

from .models import DeletedPuzzle, Puzzle, PuzzleActivity, PuzzleTag


class AnswerInline(admin.TabularInline):
    model = Answer


class PuzzleAdmin(admin.ModelAdmin):
    list_display = ["name", "is_meta", "hunt", "status", "answer"]
    list_filter = ["hunt", "is_meta"]
    inlines = [
        AnswerInline,
    ]


class PuzzleTagAdmin(admin.ModelAdmin):
    list_display = ["hunt", "name", "color", "is_meta"]
    list_filter = ["hunt", "is_meta"]


class PuzzleActivityAdmin(admin.ModelAdmin):
    list_display = ["user", "puzzle", "last_edit_time", "num_edits"]
    list_filter = ["puzzle__hunt__name", "user", "puzzle"]

    ordering = ("-last_edit_time", "-num_edits")


@admin.action(description="Restore selected items")
def nonstrict_restore_selected_items(modeladmin, request, queryset):
    queryset.restore(strict=False)


class DeletedPuzzlesAdmin(admin.ModelAdmin):
    # this is a duplicate of SoftDeletedModelAdmin but with strict = False for restores
    def get_queryset(self, request):
        super().get_queryset(request)
        qs = self.model.deleted_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    actions = [
        *admin.ModelAdmin.actions,
        hard_delete_selected_items,
        nonstrict_restore_selected_items,
    ]


admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(DeletedPuzzle, DeletedPuzzlesAdmin)
admin.site.register(PuzzleTag, PuzzleTagAdmin)
admin.site.register(PuzzleActivity, PuzzleActivityAdmin)
