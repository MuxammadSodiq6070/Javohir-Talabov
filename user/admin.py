from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin # Unfold'dan import
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin): # Ikkalasini ham qo'shamiz
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Qo\'shimcha ma\'lumotlar', {'fields': ('phone_number',)}),
    )