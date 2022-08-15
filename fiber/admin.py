from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.utils import model_ngettext
from django.utils.translation import gettext_lazy as _
from django.db.models.deletion import ProtectedError
from django.core.exceptions import PermissionDenied

from mptt.admin import MPTTModelAdmin

from . import admin_forms as forms
from . import fiber_admin
from .app_settings import TEMPLATE_CHOICES, CONTENT_TEMPLATE_CHOICES, PERMISSION_CLASS, IMAGE_PREVIEW
from .editor import get_editor_field_name
from .models import Page, ContentItem, PageContentItem, Image, File
from .utils.import_util import load_class
from .utils.widgets import AdminImageWidgetWithPreview

perms = load_class(PERMISSION_CLASS)


class UserPermissionMixin:

    def has_change_permission(self, request, obj=None):
        """
        Overrides Django's ModelAdmin method.
        """
        if obj:  # obj can be None for list views
            return perms.can_edit(request.user, obj)
        return super().has_change_permission(request)

    def has_delete_permission(self, request, obj=None):
        """
        Override Django's ModelAdmin method.
        Handles both instance-delete and bulk-delete views.
        """
        if obj:  # instance-delete action
            return perms.can_edit(request.user, obj)
        pks = request.POST.getlist('_selected_action')  # bulk delete action
        if any(not isinstance(x, int) for x in pks):
            # Handling of non-Fiber models that might use non-integer primary keys.
            # TODO: should this code even be running for non-Fiber models? See issue 261.
            return
        qs = self.model.objects.filter(pk__in=pks)
        editables_qs = perms.filter_objects(request.user, self.model.objects.all())
        if len(set(qs) & set(editables_qs)) != len(qs):
            return False
        return True

    def save_model(self, request, obj, form, change):
        """
        Notifies the PERMISSION_CLASS that an `obj` was created by `user`.
        """
        super().save_model(request, obj, form, change)
        perms.object_created(request.user, obj)


class FileAdmin(UserPermissionMixin, admin.ModelAdmin):
    list_display = ('__str__', 'title', 'updated',)
    date_hierarchy = 'updated'
    search_fields = ('title',)
    actions = ['really_delete_selected']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions[
                'delete_selected']  # the original delete selected action doesn't remove associated files, because .delete() is never called
        return actions

    def really_delete_selected(self, request, queryset):
        deleted_count = 0
        protected_count = 0

        # Check that the user has delete permission for the actual model
        if not self.has_delete_permission(request):
            raise PermissionDenied

        for obj in queryset:
            try:
                obj.delete()
                deleted_count += 1
            except ProtectedError:
                protected_count += 1

        if deleted_count:
            messages.add_message(request, messages.INFO, _("Successfully deleted %(count)d %(items)s.") % {
                "count": deleted_count, "items": model_ngettext(self.opts, deleted_count)
            })

        if protected_count:
            # TODO More informative feedback, possibly with an intermediate screen. Compare messages on trying to delete one object.
            messages.add_message(request, messages.ERROR, _(
                "%(count)d %(items)s not deleted, because that would require deleting protected related objects.") % {
                                     "count": protected_count, "items": model_ngettext(self.opts, protected_count)
                                 })

    really_delete_selected.short_description = _('Delete selected files')


class ImageAdmin(FileAdmin):
    list_display = ('__str__', 'title', 'get_size', 'updated',)
    fieldsets = (
        (None, {'fields': ('image', 'title',)}),
        (_('Size'), {'classes': ('collapse',), 'fields': ('width', 'height',)}),
    )


class ImageAdminWithPreview(ImageAdmin):
    list_display = ('preview', '__str__', 'title', 'get_size', 'updated',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'image':
            request = kwargs.pop("request", None)
            kwargs['widget'] = AdminImageWidgetWithPreview
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, **kwargs)


class ContentItemAdmin(UserPermissionMixin, admin.ModelAdmin):
    list_display = ('__str__', 'unused')
    form = forms.ContentItemAdminForm
    fieldsets = (
        (None, {'fields': ('name', get_editor_field_name('content_html'),)}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('template_name', 'protected',)}),
        (_('Metadata'), {'classes': ('collapse',), 'fields': ('metadata',)}),
    )
    date_hierarchy = 'updated'
    search_fields = ('name', get_editor_field_name('content_html'))

    def unused(self, obj):
        if obj.used_on_pages_data is None:
            return True
        return False

    unused.boolean = True


class PageContentItemInline(UserPermissionMixin, admin.TabularInline):
    model = PageContentItem
    extra = 1


class PageAdmin(UserPermissionMixin, MPTTModelAdmin):
    form = forms.PageForm
    fieldsets = (
        (None, {'fields': ('parent', 'title', 'url', 'redirect_page', 'template_name')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': (
            'meta_description', 'mark_current_regexes', 'show_in_menu', 'is_public', 'protected',)}),
        (_('Metadata'), {'classes': ('collapse',), 'fields': ('metadata',)}),
    )

    inlines = (PageContentItemInline,)
    list_display = ('title', 'view_on_site_link', 'url', 'redirect_page', 'get_absolute_url', 'action_links')
    list_per_page = 1000
    search_fields = ('title', 'url', 'redirect_page__title')

    def view_on_site_link(self, page):
        view_on_site = ''

        absolute_url = page.get_absolute_url()
        if absolute_url:
            view_on_site += '<a href="%s" title="%s" target="_blank"><img src="%sfiber/admin/images/world.gif" width="16" height="16" alt="%s" /></a>' % \
                            (absolute_url, _('View on site'), settings.STATIC_URL, _('View on site'))

        return view_on_site

    view_on_site_link.short_description = ''
    view_on_site_link.allow_tags = True

    def action_links(self, page):
        actions = ''

        # first child cannot be moved up, last child cannot be moved down
        if not page.is_first_child():
            actions += '<a href="{}/move_up" title="{}"><img src="{}fiber/admin/images/arrow_up.gif" width="16" height="16" alt="{}" /></a> '.format(
                page.pk, _('Move up'), settings.STATIC_URL, _('Move up'))
        else:
            actions += '<img src="{}fiber/admin/images/blank.gif" width="16" height="16" alt="" /> '.format(
                settings.STATIC_URL)

        if not page.is_last_child():
            actions += '<a href="{}/move_down" title="{}"><img src="{}fiber/admin/images/arrow_down.gif" width="16" height="16" alt="{}" /></a> '.format(
                page.pk, _('Move down'), settings.STATIC_URL, _('Move down'))
        else:
            actions += '<img src="{}fiber/admin/images/blank.gif" width="16" height="16" alt="" /> '.format(
                settings.STATIC_URL)

        # add subpage
        actions += '<a href="add/?%s=%s" title="%s"><img src="%sfiber/admin/images/page_new.gif" width="16" height="16" alt="%s" /></a> ' % \
                   (self.model._mptt_meta.parent_attr, page.pk, _('Add sub page'), settings.STATIC_URL,
                    _('Add sub page'))

        return f'<span class="nobr">{actions}</span>'

    action_links.short_description = _('Actions')
    action_links.allow_tags = True


class FiberAdminContentItemAdmin(UserPermissionMixin, fiber_admin.ModelAdmin):
    list_display = ('__str__',)
    form = forms.ContentItemAdminForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # remove content template choices if there are no choices
        if len(CONTENT_TEMPLATE_CHOICES) == 0:
            self.fieldsets = (
                (None, {'classes': ('hide-label',), 'fields': (get_editor_field_name('content_html'),)}),
            )
        else:
            self.fieldsets = (
                (None,
                 {'classes': ('hide-label',), 'fields': (get_editor_field_name('content_html'), 'template_name',)}),
            )


class FiberAdminPageAdmin(UserPermissionMixin, fiber_admin.MPTTModelAdmin):
    form = forms.PageForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # remove template choices if there are no choices
        if len(TEMPLATE_CHOICES) == 0:
            self.fieldsets = (
                (None, {'fields': ('title', 'url',)}),
                (_('Advanced options'), {'fields': ('redirect_page', 'show_in_menu', 'is_public',)}),
                (_('SEO'), {'fields': ('doc_title', 'meta_description', 'meta_keywords',)}),
            )
        else:
            self.fieldsets = (
                (None, {'fields': ('title', 'url',)}),
                (_('Advanced options'), {'fields': ('template_name', 'redirect_page', 'show_in_menu', 'is_public',)}),
                (_('SEO'), {'fields': ('doc_title', 'meta_description', 'meta_keywords',)}),
            )

    def save_model(self, request, obj, form, change):
        """
        - Optionally positions a Page `obj` before or beneath another page, based on POST data.
        - Notifies the PERMISSION_CLASS that a Page was created by `user`.
        """
        if 'before_page_id' in request.POST:
            before_page = Page.objects.get(pk=int(request.POST['before_page_id']))
            obj.parent = before_page.parent
            obj.insert_at(before_page, position='left', save=False)
        elif 'below_page_id' in request.POST:
            below_page = Page.objects.get(pk=int(request.POST['below_page_id']))
            obj.parent = below_page
            obj.insert_at(below_page, position='last-child', save=False)

        super().save_model(request, obj, form, change)


admin.site.register(ContentItem, ContentItemAdmin)

if IMAGE_PREVIEW:
    admin.site.register(Image, ImageAdminWithPreview)
else:
    admin.site.register(Image, ImageAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(Page, PageAdmin)

fiber_admin.site.register(ContentItem, FiberAdminContentItemAdmin)
fiber_admin.site.register(Page, FiberAdminPageAdmin)
