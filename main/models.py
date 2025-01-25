from django.contrib.auth.models import User
from django.db import models


class GoogleDriveFolder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    folder_name = models.CharField(max_length=255)
    folder_id = models.CharField(max_length=255, unique=True)
    event_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(
        max_length=255,
        default="Captivating Moments in Every Frame",
        null=True,
        blank=True,
    )
    background_image = models.ImageField(
        upload_to="gallaryimage/", default="gallaryimage/defaultbackground.jpg"
    )

    def __str__(self):
        return self.folder_name
