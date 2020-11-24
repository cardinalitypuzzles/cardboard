from django.db import models
from django.contrib.auth.models import AbstractUser


class Puzzler(AbstractUser):
    def __str__(self):
        return self.first_name + " " + self.last_name
