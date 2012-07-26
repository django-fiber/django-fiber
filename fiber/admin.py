from django.contrib import admin
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mptt.admin import MPTTModelAdmin

from fiber.editor import get_editor_field_name
from app_settings import TEMPLATE_CHOICES, CONTENT_TEMPLATE_CHOICES
from models import Page, ContentItem, PageContentItem, Image, File
import admin_forms as forms

import fiber_admin


class FileAdmin(admin.ModelAdmin):
    list_display = ('title', '__unicode__')
    date_hierarchy = 'updated'
    search_fields = ('title', )


class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', '__unicode__')
    date_hierarchy = 'updated'
    search_fields = ('title', )


class ContentItemAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    form = forms.ContentItemAdminForm
    fieldsets = (
        (None, {'fields': ('name', get_editor_field_name('content_html'),)}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('template_name', 'protected',)}),
        (_('Metadata'), {'classes': ('collapse',), 'fields': ('metadata',)}),
    )
    date_hierarchy = 'updated'
    search_fields = ('name', get_editor_field_name('content_html'))


class PageContentItemInline(admin.TabularInline):
    model = PageContentItem
    extra = 1


class PageAdmin(MPTTModelAdmin):

    form = forms.PageForm
    fieldsets = (
        (None, {'fields': ('parent', 'title', 'url', 'redirect_page', 'template_name')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('mark_current_regexes', 'show_in_menu',
                                                                      'is_public', 'protected', 'content_type',)}),
        (_('Metadata'), {'classes': ('collapse',), 'fields': ('metadata',)}),
    )

    inlines = (PageContentItemInline,)
    list_display = ('title', 'view_on_site', 'url', 'redirect_page','get_absolute_url',  'action_links',
                    'content_type_name',)
    list_per_page = 1000
    search_fields = ('title', 'url', 'redirect_page')

    def content_type_name(self, instance):
        return instance.content_type.name

    def remove_old_reference(self, model_class, pk):
        """
        Remove the one-to-one reference of a subclass of Page without deleting the Page itself

        :param model_class: A subclass of Page
        :param pk:          The primary key of the reference to delete
        """
        class FakePageSubclass(models.Model):
            page_ptr = models.PositiveIntegerField(db_column="page_ptr_id", primary_key=True)
            class Meta:
                app_label = model_class._meta.app_label
                db_table = model_class._meta.db_table
                managed = False
        try:
            fake_obj = FakePageSubclass.objects.get(pk=pk)
            fake_obj.delete()
        except Exception:
            # It could be that there is no subclass since the page was already a Page object
            pass

    def save_model(self, request, obj, form, change):
        # Check if the content_type of the object changed
        if 'content_type' in form.changed_data:
            # If so, we need to modify the one-to-one relationship through the Django ORM
            # Remove the old reference (if exists), we must query the database to get the old value for content_type
            self.remove_old_reference(Page.objects.get(pk=obj.pk).content_type.model_class(), obj.pk)
            # Modify the __class__ of the object to be the new/right class
            obj.__class__ = obj.content_type.model_class()
            # Make the one-to-one relationship if the new class is a subclass of Page
            if not obj.__class__ is Page:
                obj.page_ptr = obj
            # Note that other fields of the subclass need to have a default values
        super(PageAdmin, self).save_model(request, obj, form, change)

    def view_on_site(self, page):
        view_on_site = ''

        absolute_url = page.get_absolute_url()
        if absolute_url:
            view_on_site += u'<a href="%s" title="%s" target="_blank"><img src="%sfiber/admin/images/world.gif" width="16" height="16" alt="%s" /></a>' % \
                       (absolute_url, _('View on site'), settings.STATIC_URL, _('View on site'))

        return view_on_site

    view_on_site.short_description = ''
    view_on_site.allow_tags = True

    def action_links(self, page):
        actions = ''

        # first child cannot be moved up, last child cannot be moved down
        if not page.is_first_child():
            actions += u'<a href="%s/move_up" title="%s"><img src="%sfiber/admin/images/arrow_up.gif" width="16" height="16" alt="%s" /></a> ' % (page.pk, _('Move up'), settings.STATIC_URL, _('Move up'))
        else:
            actions += u'<img src="%sfiber/admin/images/blank.gif" width="16" height="16" alt="" /> ' % (settings.STATIC_URL,)

        if not page.is_last_child():
            actions += u'<a href="%s/move_down" title="%s"><img src="%sfiber/admin/images/arrow_down.gif" width="16" height="16" alt="%s" /></a> ' % (page.pk, _('Move down'), settings.STATIC_URL, _('Move down'))
        else:
            actions += u'<img src="%sfiber/admin/images/blank.gif" width="16" height="16" alt="" /> ' % (settings.STATIC_URL,)

        # add subpage
        actions += u'<a href="add/?%s=%s" title="%s"><img src="%sfiber/admin/images/page_new.gif" width="16" height="16" alt="%s" /></a> ' % \
                   (self.model._mptt_meta.parent_attr, page.pk, _('Add sub page'), settings.STATIC_URL, _('Add sub page'))

        return u'<span class="nobr">%s</span>' % (actions,)

    action_links.short_description = _('Actions')
    action_links.allow_tags = True


class FiberAdminContentItemAdmin(fiber_admin.ModelAdmin):
    list_display = ('__unicode__',)
    form = forms.ContentItemAdminForm

    def __init__(self, *args, **kwargs):
        super(FiberAdminContentItemAdmin, self).__init__(*args, **kwargs)

        # remove content template choices if there are no choices
        if len(CONTENT_TEMPLATE_CHOICES) == 0:
            self.fieldsets = (
                (None, {'classes': ('hide-label',), 'fields': (get_editor_field_name('content_html'), )}),
            )
        else:
            self.fieldsets = (
                (None, {'classes': ('hide-label',), 'fields': (get_editor_field_name('content_html'), 'template_name', )}),
            )


class FiberAdminPageAdmin(fiber_admin.MPTTModelAdmin):

    form = forms.PageForm

    def __init__(self, *args, **kwargs):
        super(FiberAdminPageAdmin, self).__init__(*args, **kwargs)

        # remove template choices if there are no choices
        if len(TEMPLATE_CHOICES) == 0:
            self.fieldsets = (
                (None, {'fields': ('title', 'url', )}),
                (_('Advanced options'), {'fields': ('redirect_page', 'show_in_menu', 'is_public', )}),
            )
        else:
            self.fieldsets = (
                (None, {'fields': ('title', 'url', )}),
                (_('Advanced options'), {'fields': ('template_name', 'redirect_page', 'show_in_menu', 'is_public', )}),
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


admin.site.register(ContentItem, ContentItemAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(Page, PageAdmin)

fiber_admin.site.register(ContentItem, FiberAdminContentItemAdmin)
fiber_admin.site.register(Page, FiberAdminPageAdmin)
