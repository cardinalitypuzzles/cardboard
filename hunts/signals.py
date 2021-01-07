from .models import Hunt
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta


@receiver(post_save, sender=Hunt, dispatch_uid="add_default_times")
def add_defaults(sender, instance, created, **kwargs):
    if created:
        # adds default start and end times if not provided
        if not instance.start_time:
            instance.start_time = instance.created_on
            instance.save(update_fields=["start_time"])
        if not instance.end_time:
            instance.end_time = instance.start_time + timedelta(days=3)
            instance.save(update_fields=["end_time"])
