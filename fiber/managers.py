import datetime
import re

from django.db import models
from django.utils.translation import ugettext_lazy as _

from fiber import editor


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

        for content_item in self.get_query_set().annotate(num_pages=models.Count('page')):
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


class PageManager(models.Manager):

    def visible_pages_for_user(self, user):
        visible_pages_qs = self.get_query_set()
        if not user.is_staff:
            visible_pages_qs = visible_pages_qs.filter(show_in_menu=True)

        return visible_pages_qs


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
