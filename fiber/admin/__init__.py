from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from fiber.admin.contentitemadmin import ContentItemAdmin, ContentItemAdminForm
from fiber.admin.pageadmin import PageAdmin, PageForm
from fiber.editor import get_editor_field_name
from fiber.models import Page, ContentItem, Image, File

# Regular admin site
admin.site.register(Page, PageAdmin)
admin.site.register(ContentItem, ContentItemAdmin)
admin.site.register(Image)
admin.site.register(File)


# Separate fiber admin site
class FiberAdminSite(admin.AdminSite):
    pass


class FiberAdminPageAdmin(MPTTModelAdmin):
    form = PageForm
    fieldsets = (
        (None, {'fields': ('title', 'url', 'redirect_page')}),
    )

    def save_model(self, request, obj, form, change):
        if 'before_page_id' in request.POST:
            before_page = Page.objects.get(pk=int(request.POST['before_page_id']))
            obj.parent = before_page.parent
            obj.insert_at(before_page, position='left', save=False)
        elif 'below_page_id' in request.POST:
            below_page = Page.objects.get(pk=int(request.POST['below_page_id']))
            obj.parent = below_page
            obj.insert_at(below_page, position='last-child', save=False)

        super(FiberAdminPageAdmin, self).save_model(request, obj, form, change)


class FiberAdminContentItemAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    form = ContentItemAdminForm
    fieldsets = (
        (None, {'classes': ('hide-label',), 'fields': (get_editor_field_name('content_html'),)}),
    )


fiber_admin_site = FiberAdminSite(name='fiber_admin')
fiber_admin_site.register(Page, FiberAdminPageAdmin)
fiber_admin_site.register(ContentItem, FiberAdminContentItemAdmin)
