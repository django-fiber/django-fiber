from django.db.models import Q
from django.core.urlresolvers import reverse

from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.views import ListOrCreateModelView, InstanceModelView
from djangorestframework.mixins import PaginatorMixin
from djangorestframework.status import HTTP_400_BAD_REQUEST
from djangorestframework.response import ErrorResponse
from djangorestframework.renderers import JSONRenderer, DocumentingHTMLRenderer

from fiber.models import Page, PageContentItem
from .forms import MovePageForm, MovePageContentItemForm
from fiber.app_settings import API_RENDER_HTML

API_RENDERERS = (JSONRenderer, )
if API_RENDER_HTML:
    API_RENDERERS = (JSONRenderer, DocumentingHTMLRenderer)


class ApiRoot(View):
    """
    The root view for the rest api.
    """

    permissions = (IsAuthenticated, )
    renderers = API_RENDERERS

    def get(self, request):
        return [
            {'name': 'pages', 'url': reverse('page-resource-root')},
            {'name': 'page content items', 'url': reverse('page-content-item-resource-root')},
            {'name': 'content items', 'url': reverse('content-item-resource-root')},
            {'name': 'images', 'url': reverse('image-resource-root')},
            {'name': 'files', 'url': reverse('file-resource-root')},
        ]


class ListView(ListOrCreateModelView):

    permissions = (IsAuthenticated, )
    renderers = API_RENDERERS


class TreeListView(View):

    def get(self, request):
        return  Page.objects.create_jqtree_data()


class PaginatedListView(PaginatorMixin, ListView):

    limit = 5

    def check_fields(self, order_by):
        if order_by not in self.orderable_fields:
            raise ErrorResponse(status=HTTP_400_BAD_REQUEST, content="Can not order by the passed value.")


class FileListView(PaginatedListView):

    orderable_fields = ('filename', 'updated')

    def get_queryset(self, *args, **kwargs):
        qs = super(FileListView, self).get_queryset(*args, **kwargs)

        search = self.request.GET.get('search', None)
        if search:
            qs = qs.filter(file__icontains=search)

        order_by = self.request.GET.get('order_by', 'updated')
        self.check_fields(order_by)

        if order_by == 'filename':
            order_by = 'file'

        sort_order = self.request.GET.get('sortorder', 'asc')

        qs = qs.order_by('%s%s' % ('-' if sort_order != 'asc' else '', order_by))

        return qs


class ImageListView(PaginatedListView):

    orderable_fields = ('filename', 'size', 'updated')

    def get_queryset(self, *args, **kwargs):
        qs = super(ImageListView, self).get_queryset(*args, **kwargs)

        search = self.request.GET.get('search', None)
        if search:
            # TODO: image_icontains searches in the entire path, it should only search in the filename (use iregex for this?)
            qs = qs.filter(Q(image__icontains=search) | Q(title__icontains=search) | Q(width__icontains=search) | Q(height__icontains=search))

        order_by = self.request.GET.get('order_by', 'updated')
        self.check_fields(order_by)

        if order_by == 'filename':
            order_by = 'image'
        elif order_by == 'size':
            order_by = 'width'

        sort_order = self.request.GET.get('sortorder', 'asc')

        qs = qs.order_by('%s%s' % ('-' if sort_order != 'asc' else '', order_by))

        return qs


class InstanceView(InstanceModelView):

    permissions = (IsAuthenticated, )
    renderers = API_RENDERERS


class MovePageView(View):

    permissions = (IsAuthenticated, )
    renderers = API_RENDERERS

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
    renderers = API_RENDERERS

    form = MovePageContentItemForm

    def get(self, request, pk):
        return 'Exposes the `ContentItem.move` method'

    def put(self, request, pk):
        page_content_item = PageContentItem.objects.get(id=pk)
        before_page_content_item_id = self.CONTENT.get('before_page_content_item_id', None)
        block_name = self.CONTENT.get('block_name', None)
        page_content_item.move(before_page_content_item_id, block_name)
