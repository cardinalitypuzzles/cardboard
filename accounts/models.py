from django.db import models
from django.contrib.auth.models import AbstractUser

class Puzzler(AbstractUser):

    def __str__(self):
        return self.email
