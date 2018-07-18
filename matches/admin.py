from django.contrib.admin import ModelAdmin, register
from .models import Match

# Register your models here.
@register(Match)
class MatchAdmin(ModelAdmin):
    pass