from django.db import models
from profiles.models import Profile

class VisitorAnalytics(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='analytics')
    app_source = models.CharField(max_length=50, default="Brauzer") # Telegram, Instagram, Chrome
    visited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.title} - Tashrif ({self.app_source})"

class LinkClickAnalytics(models.Model):
    # Qaysi tugma necha marta bosilganini sanash uchun
    link_id = models.IntegerField()
    clicked_at = models.DateTimeField(auto_now_add=True)