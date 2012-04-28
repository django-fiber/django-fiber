from django.core.urlresolvers import reverse

from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.views import ListOrCreateModelView, InstanceModelView
from djangorestframework.mixins import PaginatorMixin

from forms import MovePageForm, MovePageContentItemForm

from fiber.models import Page, PageContentItem

class ApiRoot(View):
    """
    The root view for the rest api.
    """

    permissions = (IsAuthenticated, )
    
    def get(self, request):
        return [{'name': 'pages', 'url': reverse('page-resource-root')},
                {'name': 'page content items', 'url': reverse('page-content-item-resource-root')},
                {'name': 'content items', 'url': reverse('content-item-resource-root')},
                {'name': 'images', 'url': reverse('image-resource-root')},
                {'name': 'files', 'url': reverse('file-resource-root')},
                ]


class ListView(ListOrCreateModelView):
    #permissions = (IsAuthenticated, )
    pass

class ImageListView( PaginatorMixin, ListView):
    limit = 5

class InstanceView(InstanceModelView):
    #permissions = (IsAuthenticated, )
    pass

class MovePageView(View):

    permissions = (IsAuthenticated, )

    form = MovePageForm

    def get(self, request, pk):
        return 'Exposes the `Page.move_page` method'

    def put(self, request, pk):
        position = self.CONTENT['position']
        target = self.CONTENT['target_node_id']
        page = Page.objects.get(id=pk)
        page.move_page(target, position)


class MovePageContentItemView(View):

    permissions = (IsAuthenticated, )

    form = MovePageContentItemForm

    def get(self, request, pk):
        return 'Exposes the `ContentItem.move` method'

    def put(self, request, pk):
        page_content_item = PageContentItem.objects.get(id=pk)
        before_page_content_item_id = self.CONTENT.get('before_page_content_item_id', None)
        block_name = self.CONTENT['block_name']
        page_content_item.move(before_page_content_item_id, block_name)