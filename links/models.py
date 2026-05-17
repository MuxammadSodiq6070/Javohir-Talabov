from django.db import models
from profiles.models import Profile

class Link(models.Model):
    ICON_CHOICES = [
        ('phone', 'Telefon'),
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('pubg', 'PUBG Mobile ID'),
        ('mlbb', 'Mobile Legends'),
        ('beelink', 'Beelink'),
        ('globe', 'Boshqa sayt'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links')
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=150, blank=True, null=True, help_text="Masalan: Nickname yoki o'yin ID raqami")
    url = models.URLField(blank=True, null=True, help_text="O'yin tugmalari uchun bo'sh qoldirsa ham bo'ladi")
    icon_type = models.CharField(max_length=20, choices=ICON_CHOICES, default='globe')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.profile.title} -> {self.title}"