from django.db import models
from profiles.models import Profile

class Link(models.Model):
    ICON_CHOICES = [
        # Aloqa va ijtimoiy tarmoqlar
        ('phone', 'Telefon'),
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('twitter', 'Twitter / X'),
        ('github', 'GitHub'),
        
        # O'yinlar
        ('pubg', 'PUBG Mobile ID'),
        ('mlbb', 'Mobile Legends ID'),
        ('freefire', 'Free Fire ID'),
        
        # Musiqa va do'konlar
        ('spotify', 'Spotify'),
        ('apple_music', 'Apple Music'),
        ('app_store', 'App Store'),
        ('play_market', 'Google Play Market'),
        
        # Umumiy
        ('beelink', 'Beelink'),
        ('globe', 'Boshqa veb-sayt havolasi'),
    ]

    ACTION_CHOICES = [
        ('link', 'Havolaga o\'tish (Link)'),
        ('copy', 'Matnni nusxalash (Copy)'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links')
    title = models.CharField(
        max_length=100, 
        verbose_name="Tugma nomi", 
        help_text="Masalan: Men bilan bog'lanish yoki PUBG ID raqamim"
    )
    url = models.CharField(
        max_length=500, 
        blank=True, 
        null=True, 
        verbose_name="Havola (Link) yoki Nusxa olinadigan ID", 
        help_text="Reja 'Link' bo'lsa sayt manzilini (http://...), 'Copy' bo'lsa nusxalanadigan ID yoki matnni yozing."
    )
    subtitle = models.CharField(
        max_length=150, 
        blank=True, 
        null=True, 
        verbose_name="Kichik matn (Ixtiyoriy)", 
        help_text="Tugma ostida kichik harflar bilan ko'rinadigan yozuv"
    )
    icon_type = models.CharField(
        max_length=20, 
        choices=ICON_CHOICES, 
        default='globe', 
        verbose_name="Belgi (Icon)"
    )
    action_type = models.CharField(
        max_length=10, 
        choices=ACTION_CHOICES, 
        default='link', 
        verbose_name="Tugma rejasi (Harakat turi)"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Tartibi")
    is_active = models.BooleanField(default=True, verbose_name="Aktivmi")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.profile.title} -> {self.title} ({self.get_action_type_display()})"