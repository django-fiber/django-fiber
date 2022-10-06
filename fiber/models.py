import os
import json
import warnings

from django.core.files.images import get_image_dimensions
from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from mptt.managers import TreeManager
from mptt.models import MPTTModel

from .app_settings import (
    IMAGES_DIR, FILES_DIR, METADATA_PAGE_SCHEMA, METADATA_CONTENT_SCHEMA,
    PAGE_MANAGER, CONTENT_ITEM_MANAGER, LIST_THUMBNAIL_OPTIONS
)
from .utils.html import htmlentitydecode
from .utils.import_util import load_class
from .utils.fields import FiberURLField, FiberMarkupField, FiberHTMLField
from .utils.images import get_thumbnail, get_thumbnail_url, ThumbnailException
from .utils.json import JSONField
from .utils.urls import get_named_url_from_quoted_url, is_quoted_url


class ContentItem(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    name = models.CharField(_('name'), blank=True, max_length=255)
    content_markup = FiberMarkupField(verbose_name=_('Content'))
    content_html = FiberHTMLField(verbose_name=_('Content'))
    protected = models.BooleanField(_('protected'), default=False)
    metadata = JSONField(_('metadata'), blank=True, null=True, schema=METADATA_CONTENT_SCHEMA, prefill_from='fiber.models.ContentItem')
    template_name = models.CharField(_('template name'), blank=True, max_length=70)
    used_on_pages_data = JSONField(_('used on pages'), blank=True, null=True)

    objects = load_class(CONTENT_ITEM_MANAGER)

    class Meta:
        verbose_name = _('content item')
        verbose_name_plural = _('content items')

    def __str__(self):
        if self.name:
            return self.name
        else:
            contents = ' '.join(htmlentitydecode(strip_tags(self.content_html)).strip().split())
            if len(contents) > 50:
                contents = contents[:50] + '...'
            return contents or gettext('[ EMPTY ]')  # TODO: find out why gettext_lazy doesn't work here

    @classmethod
    def get_add_url(cls):
        named_url = f'fiber_admin:{cls._meta.app_label}_{cls._meta.object_name.lower()}_add'
        return reverse(named_url)

    def get_change_url(self):
        named_url = f'fiber_admin:{self._meta.app_label}_{self._meta.object_name.lower()}_change'
        return reverse(named_url, args=(self.id, ))

    def set_used_on_pages_json(self):
        json_pages = []
        for page_content_item in self.page_content_items.all():
            json_pages.append({
                'title': page_content_item.page.title,
                'url': page_content_item.page.get_absolute_url(),
            })
        self.used_on_pages_data = json_pages
        self.save()

    def get_used_on_pages_json(self):
        if self.used_on_pages_data is None:
            self.set_used_on_pages_json()

        return json.dumps(self.used_on_pages_data, sort_keys=True)


class Page(MPTTModel):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='subpages', verbose_name=_('parent'), on_delete=models.CASCADE)
    meta_description = models.CharField(max_length=255, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    title = models.CharField(_('title'), max_length=255)
    doc_title = models.CharField(_('document title'), max_length=255, blank=True)
    url = FiberURLField(blank=True)
    redirect_page = models.ForeignKey('self', null=True, blank=True, related_name='redirected_pages', verbose_name=_('redirect page'), on_delete=models.SET_NULL)
    mark_current_regexes = models.TextField(_('mark current regexes'), blank=True)
    # TODO: add `alias_page` field
    template_name = models.CharField(_('template name'), blank=True, max_length=70)
    show_in_menu = models.BooleanField(_('show in menu'), default=True)
    is_public = models.BooleanField(_('is public'), default=True)
    protected = models.BooleanField(_('protected'), default=False)
    content_items = models.ManyToManyField(ContentItem, through='PageContentItem', verbose_name=_('content items'))
    metadata = JSONField(blank=True, null=True, schema=METADATA_PAGE_SCHEMA, prefill_from='fiber.models.Page')

    objects = load_class(PAGE_MANAGER)
    tree = TreeManager()

    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')
        ordering = ('tree_id', 'lft')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.id:
            old_url = Page.objects.get(id=self.id).get_absolute_url()
        else:
            old_url = ''

        super().save(*args, **kwargs)

        if old_url:
            new_url = self.get_absolute_url()
            if old_url != new_url:
                ContentItem.objects.rename_url(old_url, new_url)

    def get_absolute_url(self):
        if self.url == '':
            return ''
        if self.url.startswith('/'):
            return self.url
        elif self.url.startswith('http://') or self.url.startswith('https://'):
            return self.url
        else:
            # check if it's a named url
            if is_quoted_url(self.url):
                return get_named_url_from_quoted_url(self.url)
            else:
                # relative url
                if self.parent:
                    return '{}/{}/'.format(self.parent.get_absolute_url().rstrip('/'), self.url.strip('/'))
                else:
                    return ''  # TODO: make sure this can never happen (in model.save()?)

    @classmethod
    def get_add_url(cls):
        named_url = f'fiber_admin:{cls._meta.app_label}_{cls._meta.object_name.lower()}_add'
        return reverse(named_url)

    def get_change_url(self):
        named_url = f'fiber_admin:{self._meta.app_label}_{self._meta.object_name.lower()}_change'
        return reverse(named_url, args=(self.id, ))

    def get_content_for_block(self, block_name):
        """
        Return sorted content items for this block.
        """
        return self.page_content_items.filter(block_name=block_name).order_by('sort')

    def is_first_child(self):
        if self.is_root_node():
            return True
        return self.parent and (self.lft == self.parent.lft + 1)

    def is_last_child(self):
        if self.is_root_node():
            return True
        return self.parent and (self.rght + 1 == self.parent.rght)

    def is_child_of(self, node):
        """
        Returns True if this is a child of the given node.
        """
        return (self.tree_id == node.tree_id and
                self.lft > node.lft and
                self.rght < node.rght)

    def get_ancestors(self, *args, **kwargs):
        if getattr(self, '_ancestors_retrieved', False):
            # We have already retrieved the chain of parent objects, so can skip
            # a DB query for this.
            ancestors = []
            node = self
            while node.parent_id is not None:
                ancestors.insert(0, node.parent)
                node = node.parent
            return ancestors
        else:
            return super().get_ancestors(*args, **kwargs)

    def get_ancestors_include_self(self):
        warnings.warn("The `get_ancestors_include_self` method is deprecated,"
        "use MPPT's `get_ancestors(include_self=True)` instead", DeprecationWarning)

        return  self.get_ancestors(include_self=True)

    def move_page(self, target_id, position):
        """
        Moves the node. Parameters:
        - target_id: target page
        - position:
            - before: move the page before the target page
            - after: move the page after the target page
            - inside: move the page inside the target page (as the first child)
        """
        old_url = self.get_absolute_url()
        target_page = Page.tree.get(id=target_id)

        if position == 'before':
            self.move_to(target_page, 'left')
        elif position == 'after':
            self.move_to(target_page, 'right')
        elif position == 'inside':
            self.move_to(target_page)
        else:
            raise Exception('Unknown position')

        # change url in content items
        if old_url:
            new_url = self.get_absolute_url()
            if old_url != new_url:
                ContentItem.objects.rename_url(old_url, new_url)
                for page_content_item in self.page_content_items.all():
                    page_content_item.content_item.set_used_on_pages_json()

    def is_public_for_user(self, user):
        return user.is_staff or self.is_public

    def has_visible_children(self):
        visible_children = [page for page in self.get_children() if page.show_in_menu]
        if visible_children:
            return True
        else:
            return False


class PageContentItem(models.Model):
    content_item = models.ForeignKey(ContentItem, related_name='page_content_items', verbose_name=_('content item'), on_delete=models.CASCADE)
    page = models.ForeignKey(Page, related_name='page_content_items', verbose_name=_('page'), on_delete=models.CASCADE)
    block_name = models.CharField(_('block name'), max_length=255)
    sort = models.IntegerField(_('sort'), blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.content_item.set_used_on_pages_json()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.content_item.set_used_on_pages_json()

    def move(self, next_item_id=None, block_name=None):
        next_item = None
        if next_item_id:
            next_item = PageContentItem.objects.get(pk=next_item_id)
        if not block_name:
            if next_item:
                block_name = next_item.block_name
            else:
                block_name = self.block_name

        if self.block_name != block_name:
            self.block_name = block_name
            self.save()

        page_content_items = list(
            self.page.get_content_for_block(block_name).exclude(id=self.id),
        )

        def resort():
            for i, item in enumerate(page_content_items):
                item.sort = i
                item.save()

        if not next_item:
            page_content_items.append(self)
            resort()
        else:
            if next_item in page_content_items:
                next_index = page_content_items.index(next_item)
                page_content_items.insert(next_index, self)
                resort()


def images_directory(instance, filename):
    return os.path.join(IMAGES_DIR, filename)


class Image(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    image = models.ImageField(_('image'), upload_to=images_directory, max_length=255)
    title = models.CharField(_('title'), max_length=255)
    width = models.IntegerField(_('width'), blank=True, null=True)
    height = models.IntegerField(_('height'), blank=True, null=True)

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')
        ordering = ('-updated', )

    def __str__(self):
        return self.image.name

    def save(self, *args, **kwargs):
        # delete existing Image(s) with the same image.name - TODO: warn about this?
        existing_images = Image.objects.filter(image=os.path.join(IMAGES_DIR, self.image.name))
        for existing_image in existing_images:
            existing_image.delete()

        self.get_image_information()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.image.storage.delete(self.image.name)

    def get_image_information(self):
        self.width, self.height = get_image_dimensions(self.image) or (0, 0)

    def get_filename(self):
        return os.path.basename(self.image.name)

    def get_size(self):
        return '%s x %d' % (self.width, self.height)
    get_size.short_description = _('Size')

    def thumbnail(self):
        return get_thumbnail(self.image, thumbnail_options=LIST_THUMBNAIL_OPTIONS)

    def thumbnail_url(self):
        return get_thumbnail_url(self.image, thumbnail_options=LIST_THUMBNAIL_OPTIONS)

    def preview(self):
        try:
            thumbnail = get_thumbnail(self.image, thumbnail_options=LIST_THUMBNAIL_OPTIONS)
            if thumbnail:
                return mark_safe(f'<img src="{thumbnail.url}" width="{thumbnail.width}" height="{thumbnail.height}" />')
        except ThumbnailException as e:
            return str(e)
    preview.short_description = _('Preview')


def files_directory(instance, filename):
    return os.path.join(FILES_DIR, filename)


class File(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    file = models.FileField(_('file'), upload_to=files_directory, max_length=255)
    title = models.CharField(_('title'), max_length=255)

    class Meta:
        verbose_name = _('file')
        verbose_name_plural = _('files')
        ordering = ('-updated', )

    def __str__(self):
        return self.file.name

    def save(self, *args, **kwargs):
        # delete existing File(s) with the same file.name - TODO: warn about this?
        existing_files = File.objects.filter(file=os.path.join(FILES_DIR, self.file.name))
        for existing_file in existing_files:
            existing_file.delete()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.file.storage.delete(self.file.name)

    def get_filename(self):
        return os.path.basename(self.file.name)
