from django.db.models.signals import pre_save, post_save, pre_delete, m2m_changed
from django.dispatch import receiver
from puzzles.models import Puzzle
from puzzles.puzzle_tag import PuzzleTag

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
        )

        for p in puzzles_needing_new_tag:
            p.tags.add(new_tag)

    else:
        PuzzleTag.objects.filter(name=instance.name).filter(is_meta=True).delete()


@receiver(post_save, sender=Puzzle)
def update_tags_post_save(sender, instance, created, **kwargs):
    # make sure puzzles that already had tag now get assigned the meta
    # this has to happen post save, since instance has to exist first
    if instance.is_meta:
        puzzles_with_tag = Puzzle.objects.filter(
            tags__name__in=[instance.name]
        ).exclude(name=instance.name)
        for p in puzzles_with_tag:
            p.metas.add(instance)
            p.save()

        if created:
            instance.tags.add(PuzzleTag.objects.get(name=instance.name))


@receiver(pre_delete, sender=Puzzle)
def update_tags_pre_delete(sender, instance, **kwargs):
    if instance.is_meta:
        PuzzleTag.objects.filter(name=instance.name).delete()


@receiver(m2m_changed, sender=Puzzle.metas.through)
def update_tags_m2m(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "post_add":
        for pk in pk_set:
            meta = Puzzle.objects.get(pk=pk)
            instance.tags.add(meta.name)
    elif action == "post_remove":
        for pk in pk_set:
            meta = Puzzle.objects.get(pk=pk)
            instance.tags.remove(meta.name)
    elif action == "post_clear":
        instance.tags.filter(is_meta=True).exclude(name=instance.name).remove()
