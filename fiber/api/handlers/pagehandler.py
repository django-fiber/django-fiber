from fiber.models import Page
from piston.handler import BaseHandler


class PageHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    fields = ('data', 'children', 'show_in_menu')
    model = Page

    @classmethod
    def data(cls, page):
        return {
            'title': page.title,
            'attr': {
                'data-fiber-data': '{"type": "page", "id": %d}' % page.id,
                'href': page.get_absolute_url(),
            }
        }

    @classmethod
    def children(cls, page):
        return page.get_children()

    def read(self, request, id=None):
        if id:
            return self.read_page(id)
        else:
            return self.read_trees()

    def read_trees(self):
        return Page.objects.filter(level=0).order_by('tree_id')

    def read_page(self, page_id):
        page = Page.objects.get(id=page_id)

        # Do not include the data of the child pages.
        page.children = None
        return page

    def create(self, request):
        """
        Creates a new Page, either placed in the same level before or after a certain Page,
        or as last child below a certain parent Page.
        """
        attrs = self.flatten_dict(request.POST)

        try:
            page_title = attrs['title']
            page_relative_url = attrs['relative_url']
        except KeyError:
            return rc.BAD_REQUEST

        page = Page(title=page_title, relative_url=page_relative_url)

        if 'before_page_id' in attrs:
            before_page = Page.objects.get(pk=int(attrs['before_page_id']))
            page.parent = before_page.parent
            page.insert_at(before_page, position='left', save=False)
        elif 'below_page_id' in attrs:
            below_page = Page.objects.get(pk=int(attrs['below_page_id']))
            page.parent = below_page
            page.insert_at(below_page, position='last-child', save=False)

        page.save()
        return rc.CREATED

    def update(self, request, id):
        data = request.data

        if data.get('action') == 'move':
            self._move(
                int(id),
                int(data['parent_id']),
                int(data['left_id']),
            )
        else:
            # TODO: check if this situation occurs
            raise Exception('Unsupported action')

    def delete(self, request, id):
        page = Page.objects.get(pk=id)
        page.delete()

        return rc.DELETED

    def _move(self, page_id, parent_id, left_id):
        """
        Moves the node. Parameters:
        - page_id: the page to move
        - parent_id: the new parent
        - left_id: the node to the left (0 if it does not exist)
        """
        page = Page.objects.get(pk=page_id)
        page.move_page(
            parent_id,
            left_id,
        )
