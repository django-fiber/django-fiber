from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.files.images import get_image_dimensions
from django.db import models
from django.utils.html import strip_tags
from django.utils import simplejson
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from mptt.managers import TreeManager
from mptt.models import MPTTModel

from app_settings import IMAGES_DIR, FILES_DIR, METADATA_PAGE_SCHEMA, METADATA_CONTENT_SCHEMA
import managers
from utils.fields import FiberURLField, FiberMarkupField, FiberHTMLField
from utils.json import JSONField
from utils.urls import get_named_url_from_quoted_url, is_quoted_url


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

    objects = managers.ContentItemManager()

    class Meta:
        verbose_name = _('content item')
        verbose_name_plural = _('content items')

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            contents = ' '.join(strip_tags(self.content_html).strip().split())
            if len(contents) > 50:
                contents = contents[:50] + '...'
            return contents or ugettext('[ EMPTY ]') # TODO: find out why ugettext_lazy doesn't work here

    @classmethod
    def get_add_url(cls):
        named_url = 'fiber_admin:%s_%s_add' % (cls._meta.app_label, cls._meta.object_name.lower())
        return reverse(named_url)

    def get_change_url(self):
        named_url = 'fiber_admin:%s_%s_change' % (self._meta.app_label, self._meta.object_name.lower())
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

        return simplejson.dumps(self.used_on_pages_data)


class Page(MPTTModel):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='subpages', verbose_name=_('parent'))
    # TODO: add keywords, description (as meta?)
    title = models.CharField(_('title'), blank=True, max_length=255)
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

    tree = TreeManager()
    objects = managers.PageManager()

    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')
        ordering = ('tree_id', 'lft')

    def __unicode__(self):
        return self.title

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
                    return '%s/%s/' % (self.parent.get_absolute_url().rstrip('/'), self.url.strip('/'))
                else:
                    return '' # TODO: make sure this can never happen (in model.save()?)

    @classmethod
    def get_add_url(cls):
        named_url = 'fiber_admin:%s_%s_add' % (cls._meta.app_label, cls._meta.object_name.lower())
        return reverse(named_url)

    def get_change_url(self):
        named_url = 'fiber_admin:%s_%s_change' % (self._meta.app_label, self._meta.object_name.lower())
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

    def get_ancestors(self):
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
            return super(Page, self).get_ancestors()

    def get_ancestors_include_self(self):
        """
        This method is currently used because there is no include_self
        parameter in MPTTModel's get_ancestors() method. This will probably
        land in django-mptt 0.5
        """
        if self.is_root_node():
            return self._tree_manager.filter(pk=self.pk)

        opts = self._mptt_meta

        left = getattr(self, opts.left_attr)
        right = getattr(self, opts.right_attr)

        qs = self._tree_manager._mptt_filter(
            left__lte=left,
            right__gte=right,
            tree_id=self._mpttfield('tree_id'),
        )

        return qs.order_by(opts.left_attr)

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

    def is_public_for_user(self, user):
        return user.is_staff or self.is_public


class PageContentItem(models.Model):
    content_item = models.ForeignKey(ContentItem, related_name='page_content_items', verbose_name=_('content item'))
    page = models.ForeignKey(Page, related_name='page_content_items', verbose_name=_('page'))
    block_name = models.CharField(_('block name'), max_length=255)
    sort = models.IntegerField(_('sort'), blank=True, null=True)

    objects = managers.PageContentItemManager()

    def save(self, *args, **kwargs):
        super(PageContentItem, self).save(*args, **kwargs)
        self.content_item.set_used_on_pages_json()


class Image(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    image = models.ImageField(_('image'), upload_to=IMAGES_DIR, max_length=255)
    title = models.CharField(_('title'), max_length=255)
    width = models.IntegerField(_('width'), blank=True, null=True)
    height = models.IntegerField(_('height'), blank=True, null=True)

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')
        ordering = ('image', )

    def __unicode__(self):
        if self.image.path.startswith(settings.MEDIA_ROOT):
            return self.image.path[len(settings.MEDIA_ROOT):]
        return self.image.path

    def save(self, *args, **kwargs):
        self.get_image_information()
        super(Image, self).save(*args, **kwargs)

    def get_image_information(self):
        self.width, self.height = get_image_dimensions(self.image) or (0, 0)


class File(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    file = models.FileField(_('file'), upload_to=FILES_DIR, max_length=255)
    title = models.CharField(_('title'), max_length=255)

    class Meta:
        verbose_name = _('file')
        verbose_name_plural = _('files')
        ordering = ('file', )

    def __unicode__(self):
        if self.file.path.startswith(settings.MEDIA_ROOT):
            return self.file.path[len(settings.MEDIA_ROOT):]
        return self.file.path
