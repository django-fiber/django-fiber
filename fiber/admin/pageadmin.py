from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext as _
from fiber.utils.urls import is_quoted_url, get_named_url_from_quoted_url
from mptt.admin import MPTTModelAdmin
from mptt.forms import TreeNodeChoiceField
from fiber.models import PageContentItem, Page


class PageForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Page.tree.all(), level_indicator=3*unichr(160), empty_label='---------', required=False)
    url = forms.RegexField(label='URL', required=False, max_length=100, regex=r'^[-\w/\.\:"]+$',
        help_text = 'Example: \'/section-1/products\' or \'products\' or \'"some_named_url"\'',
        error_message = 'This value must contain only letters, numbers, underscores, dashes or slashes.')
    redirect_page = TreeNodeChoiceField(queryset=Page.objects.filter(redirect_page__isnull=True), level_indicator=3*unichr(160), empty_label='---------', required=False)

    class Meta:
        model = Page

    def clean_url(self):
        if is_quoted_url(self.cleaned_data['url']) and not get_named_url_from_quoted_url(self.cleaned_data['url']):
            raise forms.ValidationError('No reverse match found for the named url')
        return self.cleaned_data['url']

    def clean_redirect_page(self):
        if self.cleaned_data['redirect_page']:
            try:
                if self.cleaned_data['url'] and is_quoted_url(self.cleaned_data['url']):
                    raise forms.ValidationError('A named url can\'t be combined with a redirect page')
            except KeyError:
                pass
        return self.cleaned_data['redirect_page']


class PageContentItemInline(admin.TabularInline):
    model = PageContentItem
    extra = 1


class PageAdmin(MPTTModelAdmin):
    form = PageForm
    fieldsets = (
        (None, {
            'fields': ('parent', 'title', 'url', 'redirect_page', 'template_name',)
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('mark_current_regexes', 'show_in_menu', 'protected', 'metadata',)
        }),
    )
    inlines = (PageContentItemInline,)
    list_display = ('title', 'url', 'redirect_page', 'get_absolute_url', 'action_links',)
    list_per_page = 1000
    search_fields = ('title', 'url', 'redirect_page')

    def action_links(self, page):
        actions = ''

        # first child cannot be moved up, last child cannot be moved down
        actions += u'<a href="%s/move_up">\u2191</a> ' % page.pk if not page.is_first_child() else u'\u2007 '
        actions += u'<a href="%s/move_down">\u2193</a> ' % page.pk if not page.is_last_child() else u'\u2007 '

        # add subpage, view on site
        actions += u'<a href="add/?%s=%s" title="%s"><img src="%simg/admin/icon_addlink.gif" width="10" height="10" alt="%s" /></a> ' %\
                   (self.model._mptt_meta.parent_attr, page.pk, _('Add child'), settings.ADMIN_MEDIA_PREFIX, _('Add child'))

        url = page.get_absolute_url()
        if url:
            actions += u'<a href="%s" title="%s" target="_blank"><img src="%simg/admin/selector-search.gif" width="16" height="16" alt="%s" /></a>' %\
                       (url, _('View on site'), settings.ADMIN_MEDIA_PREFIX, _('View on site'))

        return actions

    action_links.short_description = 'Actions'
    action_links.allow_tags = True
