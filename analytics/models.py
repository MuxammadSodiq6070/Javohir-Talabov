from django.db import models
from links.models import Link

class LinkClick(models.Model):  # <-- Mana shu klass nomi aniq LinkClick bo'lishi kerak
    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='clicks')
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.link.title} - {self.clicked_at}"