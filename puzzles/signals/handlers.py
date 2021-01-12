from django.db import transaction
from django.db.models.signals import pre_save, post_save, pre_delete, m2m_changed
from django.dispatch import receiver
from puzzles.models import Puzzle
from puzzles.puzzle_tag import PuzzleTag
import google_api_lib.task

# Hooks for syncing metas and tags


@receiver(pre_save, sender=Puzzle)
def update_tags_pre_save(sender, instance, **kwargs):
    if instance.is_meta:
        puzzles_needing_new_tag = []
        if instance.pk is not None:
            old_instance = Puzzle.objects.get(pk=instance.pk)
            if not old_instance.is_meta:
                puzzles_needing_new_tag = [instance]
            elif old_instance.name != instance.name:
                instance.tags.filter(name=old_instance.name).delete()
                puzzles_needing_new_tag = [instance] + list(instance.feeders.all())

        (new_tag, _) = PuzzleTag.objects.update_or_create(
            name=instance.name,
            defaults={"color": PuzzleTag.BLACK, "is_meta": True},
            hunt=instance.hunt,
        )

        for p in puzzles_needing_new_tag:
            p.tags.add(new_tag)

    else:
        PuzzleTag.objects.filter(name=instance.name, hunt=instance.hunt).filter(
            is_meta=True
        ).delete()


@receiver(post_save, sender=Puzzle)
def update_tags_post_save(sender, instance, created, **kwargs):
    # make sure puzzles that already had tag now get assigned the meta
    # this has to happen post save, since instance has to exist first
    if instance.is_meta:
        puzzles_with_tag = Puzzle.objects.filter(
            hunt=instance.hunt, tags__name__in=[instance.name]
        ).exclude(name=instance.name)
        for p in puzzles_with_tag:
            p.metas.add(instance)
            p.save()

        if created:
            instance.tags.add(
                PuzzleTag.objects.get(name=instance.name, hunt=instance.hunt)
            )


@receiver(pre_delete, sender=Puzzle)
def update_tags_pre_delete(sender, instance, **kwargs):
    if instance.is_meta:
        PuzzleTag.objects.filter(name=instance.name, hunt=instance.hunt).delete()


@receiver(m2m_changed, sender=Puzzle.metas.through)
def update_tags_m2m(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "post_add":
        for pk in pk_set:
            meta = Puzzle.objects.get(pk=pk)
            meta_tag = PuzzleTag.objects.get(name=meta.name, hunt=meta.hunt)
            instance.tags.add(meta_tag)
    elif action == "post_remove":
        for pk in pk_set:
            meta = Puzzle.objects.get(pk=pk)
            meta_tag = PuzzleTag.objects.get(name=meta.name, hunt=meta.hunt)
            instance.tags.remove(meta_tag)
    elif action == "post_clear":
        instance.tags.filter(is_meta=True).exclude(name=instance.name).remove()


@receiver(pre_delete, sender=Puzzle)
def update_meta_sheets_pre_delete(sender, instance, **kwargs):
    # Need to be careful with the closure here:
    # instance.metas.all() will be empty after the transaction commits,
    # so we need to copy the metas out in advance
    metas = [meta for meta in instance.metas.all()]

    def update_metas():
        for meta in metas:
            google_api_lib.task.update_meta_sheet_feeders.delay(meta.id)

    if google_api_lib.enabled():
        transaction.on_commit(update_metas)

        if instance.sheet:
            transaction.on_commit(
                lambda: google_api_lib.task.rename_sheet.delay(
                    sheet_url=instance.sheet, name=f"[DELETED] {instance.name}"
                )
            )


@receiver(m2m_changed, sender=Puzzle.metas.through)
def update_meta_sheets_m2m(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "post_add" or action == "post_remove":

        def update_metas():
            for pk in pk_set:
                meta = Puzzle.objects.get(pk=pk)
                google_api_lib.task.update_meta_sheet_feeders.delay(meta.id)

        if google_api_lib.enabled():
            transaction.on_commit(update_metas)
