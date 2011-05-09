import datetime
import re

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.files.images import get_image_dimensions
from django.utils.html import strip_tags

from mptt.models import MPTTModel

from utils.fields import FiberMarkupField, FiberHTMLField

from fiber import editor

from app_settings import IMAGES_DIR, FILES_DIR

from utils.urls import get_named_url_from_quoted_url, is_quoted_url
from utils.json import JSONField


class ContentItemManager(models.Manager):

    def get_content_groups(self):
        """
        Get content groups:
         - recently changed
         - unused
         - used once
         - used more than once
        """
        unused = []
        once = []
        multiple = []
        recently_changed = []

        today = datetime.date.today()

        for content_item in ContentItem.objects.annotate(num_pages=models.Count('page')):
            count = content_item.num_pages

            if count == 0:
                unused.append(content_item)
            elif count == 1:
                once.append(content_item)
            else:
                multiple.append(content_item)

            if content_item.updated.date() == today:
                recently_changed.append(content_item)

        return [
            dict(title=_('used more than once'), content_items=multiple),
            dict(title=_('unused'), content_items=unused),
            dict(title=_('used once'), content_items=once),
            dict(title=_('recently changed'), content_items=recently_changed),
        ]

    def rename_url(self, old_url, new_url):
        """
        Change the urls in all content pages. Also changes the urls that begin with this url.
        """
        def rename_html(html):
            return re.sub(
                r"""(\s)href=(["'])%s""" % old_url,
                r'\1href=\2%s' % new_url,
                html
            )

        def rename_markup(markup):
            if not 'rename_url_expressions' in editor.editor:
                return markup
            else:
                expressions = editor.editor['rename_url_expressions'];
                return re.sub(
                    expressions[0] % old_url,
                    expressions[1] % new_url,
                    content_item.content_markup
                )

        for content_item in ContentItem.objects.all():
            if editor.renderer:
                markup = rename_markup(content_item.content_markup)

                if markup != content_item.content_markup:
                    content_item.content_markup = markup
                    content_item.save()
            else:
                html = rename_html(content_item.content_html)

                if html != content_item.content_html:
                    content_item.content_html = html
                    content_item.save()


class ContentItem(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    name = models.CharField(_('name'), blank=True, max_length=255)
    content_markup = FiberMarkupField(verbose_name=_('Content'))
    content_html = FiberHTMLField(verbose_name=_('Content'))
    protected = models.BooleanField(_('protected'), default=False)

    metadata = JSONField(_('metadata'), blank=True, null=True)

    objects = ContentItemManager()

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            contents = ' '.join(strip_tags(self.content_html).strip().split())
            if len(contents) > 50:
                contents = contents[:50] + '...'
            return contents or '[ EMPTY ]'

    @classmethod
    def get_add_url(cls):
        named_url = 'fiber_admin:%s_%s_add' % (cls._meta.app_label, cls._meta.object_name.lower())
        return reverse(named_url)

    def get_change_url(self):
        named_url = 'fiber_admin:%s_%s_change' % (self._meta.app_label, self._meta.object_name.lower())
        return reverse(named_url, args=(self.id, ))

    class Meta:
        verbose_name = _('content item')
        verbose_name_plural = _('content items')


class PageManager(models.Manager):

    def visible_pages_for_user(self, user):
        visible_pages_qs = self.get_query_set()

        return visible_pages_qs


class Page(MPTTModel):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    parent = models.ForeignKey('self', null=True, blank=True, related_name='subpages', verbose_name=_('parent'))

    # TODO: add keywords, description (as meta?)

    title = models.CharField(_('title'), blank=True, max_length=255)
    url = models.CharField(_('URL'), blank=True, max_length=255)
    redirect_page = models.ForeignKey('self', null=True, blank=True, related_name='redirected_pages', verbose_name=_('redirect page'))
    mark_current_regexes = models.TextField(_('mark current regexes'), blank=True)
    # TODO: add `alias_page` field
    template_name = models.CharField(_('template name'), blank=True, max_length=70)
    show_in_menu = models.BooleanField(_('show in menu'), default=True)
    protected = models.BooleanField(_('protected'), default=False)

    content_items = models.ManyToManyField(ContentItem, through='PageContentItem', verbose_name=_('content items'))

    metadata = JSONField(blank=True, null=True)

    objects = PageManager()

    def __unicode__(self):
        return self.title

    @classmethod
    def get_add_url(cls):
        named_url = 'fiber_admin:%s_%s_add' % (cls._meta.app_label, cls._meta.object_name.lower())
        return reverse(named_url)

    def get_change_url(self):
        named_url = 'fiber_admin:%s_%s_change' % (self._meta.app_label, self._meta.object_name.lower())
        return reverse(named_url, args=(self.id, ))

    def get_absolute_url(self):
        if self.url == '':
            return ''
        if self.url.startswith('/'):
            return '%s/' % self.url.rstrip('/')
        elif self.url.startswith('http://') or self.url.startswith('https://'):
            return self.url
        else:
            # check if it's a named url
            if is_quoted_url(self.url):
                return get_named_url_from_quoted_url(self.url)
            else:
                # relative url
                if self.parent:
                    return '%s/%s/' % (self.parent.get_absolute_url().rstrip('/'), self.url.strip('/'))
                else:
                    return '' # TODO: make sure this can never happen (in model.save()?)

    def is_first_child(self):
        if self.is_root_node():
            return True
        return self.parent and (self.lft == self.parent.lft + 1)

    def is_last_child(self):
        if self.is_root_node():
            return True
        return self.parent and (self.rght + 1 == self.parent.rght)

    def move_page(self, parent_id, left_id=0):
        """
        Moves the page.

        Parameters:
          - parent_id: the new parent
          - left_id: the page to the left (0 if it not applicable)
        """
        old_url = self.get_absolute_url()

        if left_id:
            # move the node to the right of the left node
            self.move_to(
                Page.objects.get(pk=left_id),
                'right',
            )
        else:
            # move the node to the first child of the parent
            self.move_to(
                Page.objects.get(pk=parent_id),
                'first-child',
            )

        # change url in content items
        if old_url:
            new_url = self.get_absolute_url()
            if old_url != new_url:
                ContentItem.objects.rename_url(old_url, new_url)

    def save(self, *args, **kwargs):
        if self.id:
            old_url = Page.objects.get(id=self.id).get_absolute_url()
        else:
            old_url = ''

        super(Page, self).save(*args, **kwargs)

        if old_url:
            new_url = self.get_absolute_url()
            if old_url != new_url:
                ContentItem.objects.rename_url(old_url, new_url)

    def get_content_for_block(self, block_name):
        """
        Return sorted content items for this block.
        """
        return self.page_content_items.filter(block_name=block_name).order_by('sort')

    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')
        ordering = ('tree_id', 'lft')


class PageContentItemManager(models.Manager):

    def move(self, item, next_item=None, block_name=None):
        if not block_name:
            if next_item:
                block_name = next_item.block_name
            else:
                block_name = item.block_name

        if item.block_name != block_name:
            item.block_name = block_name
            item.save()

        page_content_items = list(
            item.page.get_content_for_block(block_name).exclude(id=item.id)
        )

        def resort():
            for i, item in enumerate(page_content_items):
                item.sort = i
                item.save()

        if not next_item:
            page_content_items.append(item)
            resort()
        else:
            if next_item in page_content_items:
                next_index = page_content_items.index(next_item)
                page_content_items.insert(next_index, item)
                resort()


class PageContentItem(models.Model):
    content_item = models.ForeignKey(ContentItem, verbose_name=_('content item'))
    page = models.ForeignKey(Page, related_name='page_content_items', verbose_name=_('page'))
    block_name = models.CharField(_('block name'), max_length=255)
    sort = models.IntegerField(_('sort'), blank=True, null=True)

    objects = PageContentItemManager()


class Image(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    image = models.ImageField(_('image'), upload_to=IMAGES_DIR, max_length=255)
    title = models.CharField(_('title'), max_length=255)
    width = models.IntegerField(_('width'), blank=True, null=True)
    height = models.IntegerField(_('height'), blank=True, null=True)

    def save(self, *args, **kwargs):
        self.get_image_information()
        super(Image, self).save(*args, **kwargs)

    def get_image_information(self):
        self.width, self.height = get_image_dimensions(self.image) or (0, 0)

    def __unicode__(self):
        if self.image.path.startswith(settings.MEDIA_ROOT):
            return self.image.path[len(settings.MEDIA_ROOT):]
        return self.image.path

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')
        ordering = ('image', )


class File(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    file = models.FileField(_('file'), upload_to=FILES_DIR, max_length=255)
    title = models.CharField(_('title'), max_length=255)

    def __unicode__(self):
        if self.file.path.startswith(settings.MEDIA_ROOT):
            return self.file.path[len(settings.MEDIA_ROOT):]
        return self.file.path

    class Meta:
        verbose_name = _('file')
        verbose_name_plural = _('files')
        ordering = ('file', )
