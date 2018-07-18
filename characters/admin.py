from django.contrib.admin import ModelAdmin, register
from characters.models import Character

# Register your models here.
@register(Character)
class CharacterAdmin(ModelAdmin):
    list_display = ('name', 'role')
    list_filter = ('role',)