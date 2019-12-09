# MPTTModelAdmin is unused, but should stay since its import from here
# has been referenced in documentation.
from django.contrib import admin
from .options import ModelAdmin, MPTTModelAdmin


class FiberAdminSite(admin.AdminSite):

    def register(self, model_or_iterable, admin_class=None, **options):
        admin_class = admin_class or ModelAdmin
        return super().register(model_or_iterable, admin_class=admin_class, **options)


site = FiberAdminSite(name='fiber_admin')
