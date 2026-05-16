from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    slug = models.SlugField(unique=True, help_text="Sizning shaxsiy havola nomingiz (masalan: alimov)")
    logo = models.ImageField(upload_to='profile_logos/', blank=True, null=True)
    title = models.CharField(max_length=100, help_text="Sahifa sarlavhasi (Brand nomi)")
    description = models.TextField(blank=True, null=True, help_text="Qisqacha tavsif matni")
    background_image = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    theme_color = models.CharField(max_length=30, default="rgba(143, 113, 56, 0.65)")

    def __str__(self):
        return f"{self.user.username} - {self.title}"