import uuid
from django.db import models

class PublicVideo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    letter = models.TextField()
    video_filename = models.CharField(max_length=255)
    preview_filename = models.CharField(max_length=255)
    author = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.author} — {self.video_filename}'