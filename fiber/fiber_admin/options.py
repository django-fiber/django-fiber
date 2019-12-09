from django.contrib.admin import ModelAdmin as DjangoModelAdmin

from mptt.admin import MPTTModelAdmin as DjangoMPTTModelAdmin


class ModelAdmin(DjangoModelAdmin):

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # Set is_multipart() to return True to fix fiber_admin requests
        context['adminform'].form.is_multipart = lambda: True
        return super().render_change_form(request, context, add, change, form_url, obj)


class MPTTModelAdmin(DjangoMPTTModelAdmin):
    pass
