import operator

from django import template
from django.utils import simplejson

from fiber.models import Page, ContentItem

from fiber.utils.urls import get_admin_change_url

register = template.Library()


def show_menu(context, menu_name, min_level, max_level, expand=None):

    menu_pages = []
    needed_pages = []

    try:
        root_page = Page.objects.get(title=menu_name, parent=None)
    except Page.DoesNotExist:
        raise Page.DoesNotExist("Menu does not exist.\nNo top-level page found with the title '%s'." % menu_name)

    # Page.get_absolute_url() accesses self.parent recursively to build URLs
    # (assuming relative URLs).
    # This means that to render any menu item, we need all the ancestors up to
    # the root. Therefore it is more efficient to pull back this tree, without
    # min_level applied, and apply it just to decide which items to render.

    current_page = None
    if 'fiber_page' in context:
        current_page = context['fiber_page']

    if current_page and current_page.is_child_of(root_page):
        tree = root_page.get_descendants(include_self=True).filter(level__lte=max_level)
        if expand == 'all':
            needed_pages = tree
        else:
            if current_page.level + 1 < min_level:
                # Nothing to do
                needed_pages = []
            else:
                # We need the 'route' nodes, the 'sibling' nodes and the children
                route = tree.filter(lft__lt=current_page.lft,
                                    rght__gt=current_page.rght)

                # We show any siblings of anything in the route to the current page.
                # The logic here is that if the user drills down, menu items
                # shown previously should not disappear.

                # The following assumes that accessing .parent is cheap, which
                # it can be if current_page was loaded correctly.
                p = current_page
                sibling_qs = []
                while p.parent_id is not None:
                    sibling_qs.append(tree.filter(level=p.level,
                                                  lft__gt=p.parent.lft,
                                                  rght__lt=p.parent.rght))
                    p = p.parent
                route_siblings = reduce(operator.or_, sibling_qs)

                children = tree.filter(lft__gt=current_page.lft,
                                       rght__lt=current_page.rght)
                if expand != 'all_descendants':
                    # only want immediate children:
                    children = children.filter(level=current_page.level + 1)

                needed_pages = route | route_siblings | children

    else:
        # Only show menus that start at the first level (min_level == 1)
        # when the current page is not in the menu tree.
        if min_level == 1:
            if not expand:
                needed_pages = Page.objects.filter(tree_id=root_page.tree_id).filter(level__lte=1)
            elif expand == 'all':
                needed_pages = Page.objects.filter(tree_id=root_page.tree_id).filter(level__lte=max_level)
            else:
                needed_pages = []

    needed_pages = Page.objects.link_parent_objects(needed_pages)

    # Now we need to do min_level filtering
    for p in needed_pages:
        if p.level >= min_level:
            menu_pages.append(p)

    # Remove pages that shouldn't be shown in the menu for the current user.
    user = context['user']
    menu_pages = [p for p in menu_pages if (p.is_public_for_user(user)
                                            and p.show_in_menu)]

    """
    Order menu_pages for use with tree_info template tag.
    """
    menu_pages = sorted(menu_pages, key=lambda menu_page: menu_page.lft)

    """
    Find parent page for this menu
    """
    menu_parent_page = None
    if menu_pages:
        menu_parent_page = menu_pages[0].parent
    elif min_level == 1:
        menu_parent_page = root_page

    context['Page'] = Page
    context['fiber_menu_pages'] = menu_pages
    context['fiber_menu_parent_page'] = menu_parent_page
    context['fiber_menu_args'] = {'menu_name': menu_name, 'min_level': min_level, 'max_level': max_level, 'expand': expand}
    return context

register.inclusion_tag('fiber/menu.html', takes_context=True)(show_menu)


def show_content(context, content_item_name):
    content_item = None
    try:
        content_item = ContentItem.objects.get(name__exact=content_item_name)
    except ContentItem.DoesNotExist:
        pass

    context['content_item'] = content_item

    return context

register.inclusion_tag('fiber/content_item.html', takes_context=True)(show_content)


@register.tag(name='show_page_content')
def do_show_page_content(parser, token):
    """
    {% show_page_content "block_name" %}              uses page in the context for content items lookup
    {% show_page_content other_page "block_name" %}   uses other_page for content items lookup
    """
    try:
        bits = token.split_contents()
        if len(bits) not in (2, 3):
            raise template.TemplateSyntaxError, "%r tag expects one or two arguments" % token.contents.split()[0]
        if len(bits) == 2:
            # split_contents() knows not to split quoted strings.
            tag_name, block_name = token.split_contents()
            page = 'fiber_page'
        elif len(bits) == 3:
            # split_contents() knows not to split quoted strings.
            tag_name, page, block_name = token.split_contents()

    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires one or two arguments" % token.contents.split()[0]

    if not (block_name[0] == block_name[-1] and block_name[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    return ShowPageContentNode(page, block_name[1:-1])


class ShowPageContentNode(template.Node):

    def __init__(self, page, block_name):
        self.page = template.Variable(page)
        self.block_name = block_name

    def render(self, context):
        try:
            page = self.page.resolve(context)
            page_content_items = page.page_content_items.filter(block_name=self.block_name).order_by('sort').select_related('content_item')

            content_items = []
            for page_content_item in page_content_items:
                content_item = page_content_item.content_item
                content_item.page_content_item = page_content_item
                content_items.append(content_item)

            context['ContentItem'] = ContentItem
            context['fiber_page'] = page
            context['fiber_block_name'] = self.block_name
            context['fiber_content_items'] = content_items
            t = template.loader.get_template('fiber/content_items.html')
            return t.render(context)

        except template.VariableDoesNotExist:
            # page does not exist in the context
            return ''


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


def get_editable_attrs(instance):
    data = {
        "url": get_admin_change_url(instance),
    }

    return "data-fiber-data='%s'" % simplejson.dumps(data)


class EditableAttrsNode(template.Node):

    def __init__(self, instance_var):
        self.instance_var = template.Variable(instance_var)

    def render(self, context):
        try:
            instance = self.instance_var.resolve(context)
            return get_editable_attrs(instance)
        except template.VariableDoesNotExist:
            return ''


@register.tag(name='editable_attrs')
def editable_attrs(parser, token):
    try:
        instance_var = token.split_contents()[1]
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires one argument" % token.contents.split()[0]

    return EditableAttrsNode(instance_var)


@register.filter(name='escape_json_for_html')
def escape_json_for_html(value):
    """
    Escapes valid JSON for use in HTML, e.g. convert single quote to HTML character entity
    """
    return value.replace("'", "&#39;")
