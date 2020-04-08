from django.db import models
from django.utils import timezone


class Reminder(models.Model):
    chat_id = models.CharField(max_length=64, unique=True, db_index=True)
    hour = models.IntegerField(default=18, db_index=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
