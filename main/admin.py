from django.contrib import admin
from .models import Global


# Register your models here.
@admin.register(Global)
class GlobalAdmin(admin.ModelAdmin):
    list_display = ['order', 'key', 'value', 'description']
    list_editable = ['value']
    ordering = ['order']
    list_display_links = ['order']

