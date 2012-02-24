import datetime
import re

from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

from mptt.managers import TreeManager

from fiber import editor
from fiber.utils.urls import get_named_url_from_quoted_url


class ContentItemManager(models.Manager):

    def get_content_groups(self):
        """
        Get content groups data which is suitable for jqtree.

        Groups:
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

        for content_item in self.get_query_set().annotate(num_pages=models.Count('page')):
            content_item_info = dict(
                label=unicode(content_item),
                id=content_item.id,
                change_url=content_item.get_change_url(),
                used_on_pages=content_item.used_on_pages_data
            )
            count = content_item.num_pages

            if not count:
                unused.append(content_item_info)
            elif count == 1:
                once.append(content_item_info)
            else:
                multiple.append(content_item_info)

            if content_item.updated.date() == today:
                recently_changed.append(content_item_info)

        result = []

        def add_group(label, slug, children):
            if children:
                # Use ugettext instead of ugettext_lazy because result must be serializable.
                result.append(
                    dict(
                        label=ugettext(label),
                        children=children,
                        id=slug
                    )
                )

        add_group(_('used more than once'), 'multiple', multiple)
        add_group(_('unused'), 'unused', unused)
        add_group(_('used once'), 'once', once)
        add_group(_('recently changed'), 'recently_changed', recently_changed)

        return result

    def rename_url(self, old_url, new_url):
        """
        Change the urls in all content pages. Also changes the urls that begin with this url.
        """

        def rename_html(html):
            return re.sub(
                r"""(\s)href=(["'])%s""" % old_url,
                r'\1href=\2%s' % new_url,
                html,
            )

        def rename_markup(markup):
            if not 'rename_url_expressions' in editor.editor:
                return markup
            else:
                expressions = editor.editor['rename_url_expressions']
                return re.sub(
                    expressions[0] % old_url,
                    expressions[1] % new_url,
                    content_item.content_markup,
                )

        for content_item in self.get_query_set():
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
            item.page.get_content_for_block(block_name).exclude(id=item.id),
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


class PageManager(TreeManager):

    def link_parent_objects(self, pages):
        """
        Given an iterable of page objects which includes all ancestors
        of any contained pages, unifies the 'parent' objects
        using items in the iterable.
        """
        pages = list(pages)
        page_dict = {}
        for p in pages:
            page_dict[p.id] = p
        for p in pages:
            if p.parent_id is None:
                p.parent = None
            else:
                p.parent = page_dict[p.parent_id]
            p._ancestors_retrieved = True
        return pages

    def get_by_url(self, url):
        """
        Retrieve a page that matches the given URL.
        """
        # We need to check against get_absolute_url(). Typically this will
        # recursively access .parent, so we retrieve the ancestors at the same time
        # for efficiency.
        qs = self.get_query_set()

        # First check if there is a Page whose `url` matches the requested URL.
        try:
            return qs.get(url__exact=url)
        except self.model.DoesNotExist:
            pass

        # If no Page has been found, check a subset of Pages (whose `url` or
        # `relative_url` contain the rightmost part of the requested URL), to see
        # if their `get_absolute_url()` matches the requested URL entirely.

        # Since get_absolute_url() accesses .parent recursively, we
        # load the ancestors efficiently in one query first

        last_url_part = url.rstrip('/').rsplit('/', 1)[-1]
        if last_url_part:
            page_candidates = qs.exclude(url__exact='', ).filter(url__icontains=last_url_part)

            # We need all the ancestors of all the candidates. We can do this in
            # two queries - one for candidates, one for ancestors:
            route_pages = self.model.objects.none()
            for p in page_candidates:
                route_pages = route_pages | qs.filter(lft__lte=p.lft,
                                                      rght__gte=p.rght)
            route_pages = self.link_parent_objects(route_pages)
            # Use page_candidates that have parent objects attached
            page_candidates = [p for p in route_pages if last_url_part in p.url]

            for page in page_candidates:
                if page.get_absolute_url() == url:
                    return page

        # If no Page has been found, try to find a Page by matching the
        # requested URL with reversed `named_url`s.
        page_candidates = qs.filter(url__startswith='"', url__endswith='"')
        for page in page_candidates:
            if get_named_url_from_quoted_url(page.url) == url:
                return page

    def create_jqtree_data(self):
        """
        Create a page tree suitable for the jqtree. The result is a recursive list of dicts.

        Example:
            [
                {
                    'label': 'menu1',
                    'children': [
                        { 'label': page1' }
                    ]
                },
                {
                    'label': 'menu2',
                }
            ]
        """
        data = []
        page_dict = dict()  # maps page id to page info

        # The queryset contains all pages in correct order
        queryset = self.model.tree.get_query_set()

        for page in queryset:
            page_info = dict(
                label=page.title,
                id=page.id,
            )

            url=page.get_absolute_url()
            if url:
                page_info['url'] = url
                page_info['change_url'] = page.get_change_url()
                page_info['add_url'] = page.get_add_url()

                page_info['show_in_menu'] = page.show_in_menu
                page_info['is_public'] = page.is_public
                page_info['is_redirect'] = bool(page.redirect_page)

            if not page.parent:
                # Root element
                data.append(page_info)
            else:
                parent_info = page_dict.get(page.parent_id)
                if not 'children' in parent_info:
                    parent_info['children'] = []

                parent_info['children'].append(page_info)

            page_dict[page.id] = page_info

        return data

