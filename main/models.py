from django.db import models
from django.contrib.auth.models import User


class GoogleDriveFolder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    folder_name = models.CharField(max_length=255)
    folder_id = models.CharField(max_length=255, unique=True)
    event_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, default='Captivating Moments in Every Frame', null=True, blank=True)
    background_image = models.ImageField(upload_to='uploads/gallaryimage/', default="uploads/gallaryimage/defaultbackground.jpg", null=True, blank=True)

    def __str__(self):
        return self.folder_name


