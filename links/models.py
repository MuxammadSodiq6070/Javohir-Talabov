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

    ACTION_CHOICES = [
        ('link', 'Havolaga o\'tish (Link)'),
        ('copy', 'Matnni nusxalash (Copy)'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links')
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=150, blank=True, null=True, help_text="Nusxalanadigan ID yoki kichik matn")
    url = models.URLField(blank=True, null=True, help_text="Havolaga o'tish rejimi uchun URL manzil")
    icon_type = models.CharField(max_length=20, choices=ICON_CHOICES, default='globe')
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES, default='link', help_text="Tugma bosilgandagi harakat turi")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.profile.title} -> {self.title} ({self.get_action_type_display()})"