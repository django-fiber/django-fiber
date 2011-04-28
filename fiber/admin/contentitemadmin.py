from django import forms
from django.contrib import admin
from fiber.editor import get_editor_field_name
from fiber.models import ContentItem


class ContentItemAdminForm(forms.ModelForm):
    class Meta:
        model = ContentItem


class ContentItemAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    form = ContentItemAdminForm
    fieldsets = (
        (None, {'fields': ('name', get_editor_field_name('content_html'))}),
        ('Advanced options', {'classes': ('collapse',), 'fields': ('protected', 'metadata',)}),
    )
