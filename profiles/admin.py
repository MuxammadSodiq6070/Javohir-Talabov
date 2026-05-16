from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline # Unfold'dan import qilamiz
from .models import Profile
from links.models import Link

class LinkInline(TabularInline): # Unfold uslubidagi inline
    model = Link
    extra = 1
    fields = ('title', 'subtitle', 'url', 'icon_type', 'order', 'is_active')

@admin.register(Profile)
class ProfileAdmin(ModelAdmin): # Standart admin o'rniga Unfold ModelAdmin
    list_display = ('title', 'user', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LinkInline]