from django.db import models
from django.contrib.auth.models import AbstractUser


class Puzzler(AbstractUser):
    last_accessed_hunt = models.ForeignKey(
        "hunts.Hunt", null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.first_name + " " + self.last_name
