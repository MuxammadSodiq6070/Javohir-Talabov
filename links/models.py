from django.db import models
from profiles.models import Profile

class Link(models.Model):
    ICON_CHOICES = [
        ('phone', 'Call Center'),
        ('telegram', 'Telegram'),
        ('youtube', 'YouTube'),
        ('instagram', 'Instagram'),
        ('globe', 'Veb-sayt'),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links')
    title = models.CharField(max_length=100, help_text="Tugma matni")
    subtitle = models.CharField(max_length=150, blank=True, null=True, help_text="Ostki matn")
    url = models.URLField(help_text="O'tish havolasi")
    icon_type = models.CharField(max_length=20, choices=ICON_CHOICES, default='globe')
    order = models.PositiveIntegerField(default=0, help_text="Tartib raqami")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.profile.title} -> {self.title}"