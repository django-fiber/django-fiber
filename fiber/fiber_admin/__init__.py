from django.contrib import admin
from options import ModelAdmin, MPTTModelAdmin


class FiberAdminSite(admin.AdminSite):

    def register(self, model_or_iterable, admin_class=None, **options):
        if not admin_class:
            admin_class = ModelAdmin
        return super(FiberAdminSite, self).register(model_or_iterable, admin_class=admin_class, **options)


site = FiberAdminSite(name='fiber_admin')
