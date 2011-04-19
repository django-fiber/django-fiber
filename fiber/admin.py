from django import forms
from django.contrib import admin

from mptt.admin import MPTTModelAdmin
from mptt.forms import TreeNodeChoiceField

from fiber.editor import get_editor_field_name

from models import Page, ContentItem, PageContentItem, Image, File
from utils.urls import get_named_url_from_quoted_url, is_quoted_url

class FiberAdminSite(admin.AdminSite):
    pass

fiber_admin_site = FiberAdminSite(name='fiber_admin')


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
        (None, {'fields': ('parent', 'title', 'url', 'redirect_page', 'template_name',)}),
        ('Advanced options', {'classes': ('collapse',), 'fields': ('mark_current_regexes', 'show_in_menu', 'protected', 'metadata',)}),
    )
    inlines = (PageContentItemInline,)
    list_display = ('title', 'url', 'redirect_page','get_absolute_url', 'move_links',)
    list_per_page = 1000
    search_fields = ('title', 'url', 'redirect_page')

    def move_links(self, object):
        move_up = u'\u2007'
        move_down = u'\u2007'

        # first child cannot be moved up
        if (not object.is_first_child()):
            move_up = u'<a href="%s/move_up">\u2191</a>' % object.pk

        # last child cannot be moved down
        if (not object.is_last_child()):
            move_down = u'<a href="%s/move_down">\u2193</a>' % object.pk

        return move_up + move_down

    move_links.short_description = 'Move'
    move_links.allow_tags = True


admin.site.register(Page, PageAdmin)


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


fiber_admin_site.register(Page, FiberAdminPageAdmin)


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
