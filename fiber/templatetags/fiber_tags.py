import json
import operator

from copy import copy
from functools import reduce

from django import template
from django.contrib.auth.models import AnonymousUser
from django.template import TemplateSyntaxError
from django.utils.html import escape
from django.utils.safestring import mark_safe

import fiber
from fiber.app_settings import AUTO_CREATE_CONTENT_ITEMS, PERMISSION_CLASS
from fiber.models import ContentItem, Page
from fiber.utils.import_util import load_class
from fiber.utils.urls import get_admin_change_url

PERMISSIONS = load_class(PERMISSION_CLASS)

register = template.Library()


class MenuHelper:
    """
    Helper class for show_menu tag, for convenience/clarity
    """
    def __init__(self, context, menu_name, min_level=1, max_level=999, expand=None):
        self.context = copy(context)
        self.menu_name = menu_name
        self.min_level = min_level
        self.max_level = max_level
        self.expand = expand
        self.menu_parent = None

    def filter_min_level(self, tree):
        """
        Remove pages that are below the minimum_level
        """
        return (p for p in tree if p.level >= self.min_level)

    def filter_for_user(self, tree):
        """
        Remove pages that shouldn't be in the menu for the current user
        """
        user = self.context.get('user', AnonymousUser())
        return (p for p in tree if (p.is_public_for_user(user) and p.show_in_menu))

    def get_context_data(self):
        return {
            'Page': Page,
            'fiber_menu_pages': self.get_menu(),
            'fiber_menu_parent_page': self.menu_parent,
            'fiber_menu_args': {
                'menu_name': self.menu_name,
                'min_level': self.min_level,
                'max_level': self.max_level,
                'expand': self.expand
            }
        }

    def get_root(self):
        """
        Get the root page for this menu
        """
        try:
            return Page.objects.get(title=self.menu_name, parent=None)
        except Page.DoesNotExist:
            raise Page.DoesNotExist("Menu does not exist.\nNo top-level page found with the title '%s'." % self.menu_name)

    def get_tree(self, root):
        """
        Get a page tree from the root page, limited to max_level
        """
        # Page.get_absolute_url() accesses self.parent recursively to build URLs (assuming relative URLs).
        # To render any menu item, we need all the ancestors up to the root.
        # Therefore it's more efficient to fetch the entire tree, and apply min_level manually later.
        return root.get_descendants(include_self=True).filter(level__lte=self.max_level)

    def get_tree_for_page(self, root, page):
        """
        Get a tree, taking a specific page into account
        """
        if not page or not page.is_child_of(root):
            if self.min_level == 1:
                # The current page is not part of the menu tree.
                # Only show first level menus.
                return self.get_tree(root).filter(level__lte=1)
            else:
                # The current page is not part of the menu tree, so it can't have a sub menu
                return []
        if page.level + 1 < self.min_level:
            return []  # The current page is below the threshold, so no menu should be shown
        else:
            tree = self.get_tree(root)

            # We need the 'route' to the current page, the 'sibling' nodes and the children
            route = tree.filter(lft__lt=page.lft, rght__gt=page.rght)

            # We show any siblings of anything in the route to the current page.
            # The logic here is that if the user drills down, menu items
            # shown previously should not disappear.

            # The following assumes that accessing .parent is cheap, which
            # it can be if current_page was loaded correctly.
            p = page
            sibling_qs = []
            while p.parent_id is not None:
                sibling_qs.append(tree.filter(level=p.level, lft__gt=p.parent.lft, rght__lt=p.parent.rght))
                p = p.parent
            route_siblings = reduce(operator.or_, sibling_qs)

            children = tree.filter(lft__gt=page.lft, rght__lt=page.rght)
            if self.expand != 'all_descendants':
                # only want immediate children:
                children = children.filter(level=page.level + 1)

            return route | route_siblings | children

    def get_menu(self):
        """
        Get the menu tree
        """
        root = self.get_root()
        current = self.context.get('fiber_page')
        if self.expand == 'all':
            # Unfiltered sitemap like tree
            tree = self.get_tree(root)
        else:
            # (sub) menus, expanding/collapsing based on current page
            tree = self.get_tree_for_page(root, current)

        tree = Page.objects.link_parent_objects(tree)
        tree = self.filter_min_level(tree)
        tree = self.filter_for_user(tree)

        # Order menu_pages for use with tree_info template tag.
        tree = sorted(tree, key=operator.attrgetter('lft'))

        self.menu_parent = None
        if tree and self.min_level > 1:
            self.menu_parent = tree[0].parent
        elif self.min_level == 1:
            self.menu_parent = root
        return tree


@register.inclusion_tag('fiber/menu.html', takes_context=True)
def show_menu(context, menu_name, min_level, max_level, expand=None):
    context = copy(context)
    context.update(MenuHelper(context, menu_name, min_level, max_level, expand).get_context_data())
    return context


@register.inclusion_tag('fiber/content_item.html', takes_context=True)
def show_content(context, content_item_name):
    """
    Fetch and render a named content item. If FIBER_AUTO_CREATE_CONTENT_ITEMS = True and the content item does not
    yet exist, it will be created.

    {% show_content "block_name" %}
    """
    content_item = None
    try:
        content_item = ContentItem.objects.get(name__exact=content_item_name)
    except ContentItem.DoesNotExist:
        if AUTO_CREATE_CONTENT_ITEMS:
            content_item = ContentItem.objects.create(name=content_item_name)

    context = copy(context)
    context.update({'content_item': content_item})
    return context


@register.inclusion_tag('fiber/content_items.html', takes_context=True)
def show_page_content(context, page_or_block_name, block_name=None):
    """
    Fetch and render named content items for the current fiber page, or a given fiber page.

    {% show_page_content "block_name" %}              use fiber_page in context for content items lookup
    {% show_page_content other_page "block_name" %}   use other_page for content items lookup
    """
    page_or_block_name = page_or_block_name or None
    if isinstance(page_or_block_name, str) and block_name is None:
        # Single argument e.g. {% show_page_content 'main' %}
        block_name = page_or_block_name
        try:
            page = context['fiber_page']
        except KeyError:
            page = None
    elif (page_or_block_name is None or isinstance(page_or_block_name, Page)) and block_name:
        # Two arguments e.g. {% show_page_content other_page 'main' %}
        page = page_or_block_name
    else:
        # Bad arguments
        raise TemplateSyntaxError("'show_page_content' received invalid arguments")

    if page and block_name:
        page_content_items = page.page_content_items.filter(block_name=block_name).order_by('sort').select_related('content_item')
        content_items = []
        for page_content_item in page_content_items:
            content_item = page_content_item.content_item
            content_item.page_content_item = page_content_item
            content_items.append(content_item)

        context = copy(context)
        context.update({
            'fiber_page': page,
            'ContentItem': ContentItem,
            'fiber_block_name': block_name,
            'fiber_content_items': content_items
        })
        return context


@register.tag(name='captureas')
def do_captureas(parser, token):
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("'captureas' node requires a variable name.")

    nodelist = parser.parse(('endcaptureas',))
    parser.delete_first_token()

    return CaptureasNode(nodelist, args)


class CaptureasNode(template.Node):

    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        return ''


@register.simple_tag(takes_context=True)
def editable_attrs(context, obj):
    user = context.get('user')
    if obj and user and user.is_staff:
        if hasattr(obj, 'get_change_url'):
            change_url = obj.get_change_url()
        else:
            change_url = get_admin_change_url(obj)
        data = {
            'type': obj.__class__.__name__.lower(),
            'url': change_url,
            'can_edit': PERMISSIONS.can_edit(user, obj)
        }
        return mark_safe(' data-fiber-data="%s"' % escape(json.dumps(data, sort_keys=True)))
    return ''


@register.filter
def can_edit(obj, user):
    return PERMISSIONS.can_edit(user, obj)


@register.simple_tag
def fiber_version():
    return fiber.__version__
