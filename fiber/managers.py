import datetime
import re

from django.db import models
from django.utils.encoding import force_str
from django.utils.translation import gettext, gettext_lazy as _

from mptt.managers import TreeManager

from . import editor
from .utils.urls import get_named_url_from_quoted_url

from .utils.import_util import load_class
from .app_settings import PERMISSION_CLASS


class ContentItemManager(models.Manager):

    def get_content_groups(self, user=None):
        """
        Get content groups data which is suitable for jqtree.

        Groups:
         - recently changed
         - unused
         - used once
         - used more than once

        If `user` is provided the queryset is filtered so only the content items that `user` is allowed to edit are returned.
        """
        unused = []
        once = []
        multiple = []
        recently_changed = []

        today = datetime.date.today()

        queryset = self.get_queryset()

        #  Filter queryset through the permissions class
        if user:
            queryset = load_class(PERMISSION_CLASS).filter_objects(user, queryset)

        for content_item in queryset.annotate(num_pages=models.Count('page')):
            content_item_info = dict(
                label=force_str(content_item),
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
                # Use gettext instead of gettext_lazy because result must be serializable.
                result.append(
                    dict(
                        label=gettext(label),
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

        queryset = self.get_queryset()

        for content_item in queryset:
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

        queryset = self.get_queryset()

        # First check if there is a Page whose `url` matches the requested URL.
        try:
            return queryset.get(url__exact=url)
        except self.model.DoesNotExist:
            pass

        # If no Page has been found, check a subset of Pages (whose `url` or
        # `relative_url` contain the rightmost part of the requested URL), to see
        # if their `get_absolute_url()` matches the requested URL entirely.

        # Since get_absolute_url() accesses .parent recursively, we
        # load the ancestors efficiently in one query first

        last_url_part = url.rstrip('/').rsplit('/', 1)[-1]
        if last_url_part:
            page_candidates = queryset.exclude(url__exact='', ).filter(url__icontains=last_url_part)

            # We need all the ancestors of all the candidates. We can do this in
            # two queries - one for candidates, one for ancestors:
            route_pages = self.model.objects.none()
            for p in page_candidates:
                route_pages = route_pages | queryset.filter(lft__lte=p.lft,
                                                      rght__gte=p.rght)
            route_pages = self.link_parent_objects(route_pages)
            # Use page_candidates that have parent objects attached
            page_candidates = [p for p in route_pages if last_url_part in p.url]

            for page in page_candidates:
                if page.get_absolute_url() == url:
                    return page

        # If no Page has been found, try to find a Page by matching the
        # requested URL with reversed `named_url`s.
        page_candidates = queryset.filter(url__startswith='"', url__endswith='"')
        for page in page_candidates:
            if get_named_url_from_quoted_url(page.url) == url:
                return page

    def create_jqtree_data(self, user):
        """
        Create a page tree suitable for the jqtree. The result is a recursive list of dicts.

        If `user` is provided the tree is annotated to indicate editability of the pages.

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
        queryset = self.model.tree.get_queryset()

        # Filter queryset using the permissions class
        editables_queryset = load_class(PERMISSION_CLASS).filter_objects(user, queryset)

        for page in queryset:
            page_info = dict(
                label=page.title,
                id=page.id,
                editable=page in editables_queryset
            )

            url = page.get_absolute_url()
            if url:
                # normal pages
                page_info['url'] = url
                page_info['change_url'] = page.get_change_url()
                page_info['add_url'] = page.get_add_url()

                page_info['show_in_menu'] = page.show_in_menu
                page_info['is_public'] = page.is_public
                page_info['is_redirect'] = bool(page.redirect_page)
            else:
                # root nodes / menu 'pages'
                page_info['add_url'] = page.get_add_url()

            if not page.parent:
                # root node
                data.append(page_info)
            else:
                parent_info = page_dict.get(page.parent_id, {})
                if not 'children' in parent_info:
                    parent_info['children'] = []

                parent_info['children'].append(page_info)

            page_dict[page.id] = page_info
        return data
