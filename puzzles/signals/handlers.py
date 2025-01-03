from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import m2m_changed, post_save, pre_delete, pre_save
from django.dispatch import receiver
from django_softdelete.signals import post_restore, post_soft_delete

import chat.tasks
import google_api_lib.tasks
from puzzles.models import DeletedPuzzle, Puzzle
from puzzles.puzzle_tag import META_COLOR, PuzzleTag

from ..models import Puzzle

# Hooks for syncing metas and tags


@receiver(pre_save, sender=Puzzle)
def update_tags_pre_save(sender, instance, **kwargs):
    if instance.is_deleted:
        return

    if instance.is_meta:
        puzzles_needing_new_tag = []
        if instance.pk is not None:
            old_instance = Puzzle.global_objects.get(pk=instance.pk)
            if not old_instance.is_meta:
                puzzles_needing_new_tag = [instance]
            elif old_instance.name != instance.name:
                instance.tags.filter(name=old_instance.name).delete()
                puzzles_needing_new_tag = [instance] + list(instance.feeders.all())

        (new_tag, _) = PuzzleTag.objects.update_or_create(
            name=instance.name,
            defaults={"color": META_COLOR, "is_meta": True},
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


@receiver(post_soft_delete, sender=Puzzle)
def update_tags_post_delete(sender, instance, **kwargs):
    if instance.is_meta:
        PuzzleTag.objects.filter(name=instance.name, hunt=instance.hunt).delete()


@receiver(post_restore, sender=DeletedPuzzle)
def update_tags_post_restore(sender, instance, **kwargs):
    if instance.is_meta:
        # restore meta tag
        PuzzleTag.objects.update_or_create(
            name=instance.name,
            defaults={"color": META_COLOR, "is_meta": True},
            hunt=instance.hunt,
        )


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


@receiver(post_soft_delete, sender=Puzzle)
@receiver(post_restore, sender=DeletedPuzzle)
def update_sheets_post_delete(sender, instance, **kwargs):
    # Need to be careful with the closure here:
    # instance.metas.all() will be empty after the transaction commits,
    # so we need to copy the metas out in advance
    metas = [meta for meta in instance.metas.all()]

    def update_metas():
        for meta in metas:
            google_api_lib.tasks.update_meta_and_metameta_sheets_delayed(meta)

    if google_api_lib.enabled():
        transaction.on_commit(update_metas)

        if instance.sheet:
            name = (
                f"[DELETED] {instance.name}" if instance.is_deleted else instance.name
            )
            transaction.on_commit(
                lambda: google_api_lib.tasks.rename_sheet.delay(
                    sheet_url=instance.sheet, name=name
                )
            )


@receiver(pre_delete, sender=Puzzle)
def delete_chat_room(sender, instance, using, **kwargs):
    # has to be pre_delete or else instance.chat_room is None
    if instance.chat_room:
        chat.tasks.cleanup_puzzle_channels.apply_async(
            args=(instance.id,), countdown=1800  # clean up in 30 minutes
        )


@receiver(post_soft_delete, sender=Puzzle)
def clear_cache(sender, instance, using, **kwargs):
    drive_item_name = cache.get(instance.id)
    if drive_item_name:
        cache.delete(drive_item_name)
        cache.delete(instance.id)


@receiver(m2m_changed, sender=Puzzle.metas.through)
def update_meta_sheets_m2m(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "post_add" or action == "post_remove":

        def update_metas():
            for pk in pk_set:
                meta = Puzzle.objects.get(pk=pk)
                google_api_lib.tasks.update_meta_and_metameta_sheets_delayed(meta)

        if google_api_lib.enabled():
            transaction.on_commit(update_metas)


@receiver(m2m_changed, sender=Puzzle.metas.through)
def update_meta_chat_m2m(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "post_add" or action == "post_remove":
        if instance.chat_room:
            transaction.on_commit(
                lambda: chat.tasks.handle_puzzle_meta_change.delay(instance.id)
            )
