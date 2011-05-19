from django import forms
from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from mptt.admin import MPTTModelAdmin
from mptt.forms import TreeNodeChoiceField

from fiber.editor import get_editor_field_name

from app_settings import TEMPLATE_CHOICES
from models import Page, ContentItem, PageContentItem, Image, File
from utils.urls import get_named_url_from_quoted_url, is_quoted_url


class FiberAdminSite(admin.AdminSite):
    pass

fiber_admin_site = FiberAdminSite(name='fiber_admin')


class PageForm(forms.ModelForm):

    parent = TreeNodeChoiceField(queryset=Page.tree.all(), level_indicator=3*unichr(160), empty_label='---------', required=False)
    url = forms.RegexField(label=_('URL'), required=False, max_length=100, regex=r'^[-\w/\.\:"]+$',
        help_text = _("""Example: '/section-1/products' or 'products' or '"some_named_url"'"""),
        error_message = _('This value must contain only letters, numbers, underscores, dashes or slashes.'))
    redirect_page = TreeNodeChoiceField(label=_('Redirect page'), queryset=Page.objects.filter(redirect_page__isnull=True), level_indicator=3*unichr(160), empty_label='---------', required=False)

    class Meta:
        model = Page

    def clean_url(self):
        if is_quoted_url(self.cleaned_data['url']) and not get_named_url_from_quoted_url(self.cleaned_data['url']):
            raise forms.ValidationError(_('No reverse match found for the named url'))
        return self.cleaned_data['url']

    def clean_redirect_page(self):
        if self.cleaned_data['redirect_page']:
            try:
                if self.cleaned_data['url'] and is_quoted_url(self.cleaned_data['url']):
                    raise forms.ValidationError(_('A named url can\'t be combined with a redirect page'))
            except KeyError:
                pass
        return self.cleaned_data['redirect_page']


class PageContentItemInline(admin.TabularInline):
    model = PageContentItem
    extra = 1


class PageAdmin(MPTTModelAdmin):

    form = PageForm
    fieldsets = (
        (None, {'fields': ('parent', 'title', 'url', 'redirect_page', 'template_name')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('mark_current_regexes', 'show_in_menu', 'protected', 'metadata',)}),
    )

    inlines = (PageContentItemInline,)
    list_display = ('title', 'view_on_site', 'url', 'redirect_page','get_absolute_url', 'action_links',)
    list_per_page = 1000
    search_fields = ('title', 'url', 'redirect_page')
    
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

        return actions

    action_links.short_description = _('Actions')
    action_links.allow_tags = True


admin.site.register(Page, PageAdmin)


class FiberAdminPageForm(PageForm):
    template_name = forms.ChoiceField(choices=TEMPLATE_CHOICES, required=False, label=_('Template'))


class FiberAdminPageAdmin(MPTTModelAdmin):

    form = FiberAdminPageForm

    def __init__(self, *args, **kwargs):
        super(FiberAdminPageAdmin, self).__init__(*args, **kwargs)

        # remove template choices if there are no choices
        if len(TEMPLATE_CHOICES) == 0:
            self.fieldsets = (
                (None, {'fields': ('title', 'url', 'redirect_page')}),
            )
        else:
            self.fieldsets = (
                (None, {'fields': ('title', 'url', 'template_name', 'redirect_page')}),
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


fiber_admin_site.register(Page, FiberAdminPageAdmin)


class ContentItemAdminForm(forms.ModelForm):

    class Meta:
        model = ContentItem


class ContentItemAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    form = ContentItemAdminForm
    fieldsets = (
        (None, {'fields': ('name', get_editor_field_name('content_html'))}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('protected', 'metadata',)}),
    )

admin.site.register(ContentItem, ContentItemAdmin)


class FiberAdminContentItemAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    form = ContentItemAdminForm
    fieldsets = (
        (None, {'classes': ('hide-label',), 'fields': (get_editor_field_name('content_html'),)}),
    )
fiber_admin_site.register(ContentItem, FiberAdminContentItemAdmin)


admin.site.register(Image)


admin.site.register(File)
