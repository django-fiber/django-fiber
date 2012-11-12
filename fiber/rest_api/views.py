from django.db.models import Q

from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.views import ListOrCreateModelView
from djangorestframework.mixins import PaginatorMixin
from djangorestframework.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from djangorestframework.response import ErrorResponse
from djangorestframework.renderers import JSONRenderer, DocumentingHTMLRenderer

from fiber.models import Page, PageContentItem, ContentItem, File, Image
from fiber.app_settings import API_RENDER_HTML, PERMISSION_CLASS
from fiber.utils import class_loader
from .forms import MovePageForm, MovePageContentItemForm

PERMISSIONS = class_loader.load_class(PERMISSION_CLASS)

API_RENDERERS = (JSONRenderer, )
if API_RENDER_HTML:
    API_RENDERERS = (JSONRenderer, DocumentingHTMLRenderer)

_403_FORBIDDEN_RESPONSE = ErrorResponse(
    HTTP_403_FORBIDDEN,
    {'detail': 'You do not have permission to access this resource. ' +
               'You may need to login or otherwise authenticate the request.'})


from rest_framework import generics, renderers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import views

from .serializers import PageSerializer, PageContentItemSerializer, ContentItemSerializer, FileSerializer, ImageSerializer, FiberPaginationSerializer


class FiberListCreateAPIView(generics.ListCreateAPIView):
    def create(self, request, *args, **kwargs):
        response = super(FiberListCreateAPIView, self).created(request, *args, **kwargs)
        PERMISSIONS.object_created(request.user, self.object)
        return response


class PageList(FiberListCreateAPIView):
    model = Page
    serializer_class = PageSerializer
    renderer_classes = (renderers.JSONRenderer, )


class PageDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Page
    serializer_class = PageSerializer
    renderer_classes = (renderers.JSONRenderer, )


class PageContentItemList(FiberListCreateAPIView):
    model = PageContentItem
    serializer_class = PageContentItemSerializer
    renderer_classes = (renderers.JSONRenderer, )


class PageContentItemDetail(generics.RetrieveUpdateDestroyAPIView):
    model = PageContentItem
    serializer_class = PageContentItemSerializer
    renderer_classes = (renderers.JSONRenderer, )


class ContentItemList(FiberListCreateAPIView):
    model = ContentItem
    serializer_class = ContentItemSerializer
    renderer_classes = (renderers.JSONRenderer, )


class ContentItemDetail(generics.RetrieveUpdateDestroyAPIView):
    model = ContentItem
    serializer_class = ContentItemSerializer
    renderer_classes = (renderers.JSONRenderer, )


class FileList(FiberListCreateAPIView):
    model = File
    serializer_class = FileSerializer
    renderer_classes = (renderers.JSONRenderer, )
    pagination_serializer_class = FiberPaginationSerializer
    paginate_by = 5


class FileDetail(generics.RetrieveUpdateDestroyAPIView):
    model = File
    serializer_class = FileSerializer
    renderer_classes = (renderers.JSONRenderer, )


class ImageList(FiberListCreateAPIView):
    model = Image
    serializer_class = ImageSerializer
    renderer_classes = (renderers.JSONRenderer, )
    pagination_serializer_class = FiberPaginationSerializer
    paginate_by = 5


class ImageDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Image
    serializer_class = ImageSerializer
    renderer_classes = (renderers.JSONRenderer, )


@api_view(('GET',))
def api_root(request, format='None'):
    """
    This is the entry point for the API.
    """
    return Response({
            'pages': reverse('page-list', request=request),
            'pagetree': reverse('pagetree', request=request),
            'page content items': reverse('pagecontentitem-list', request=request),
            'content items': reverse('contentitem-list', request=request),
            'images': reverse('image-list', request=request),
            'files': reverse('file-list', request=request),
    })


class PageTree(views.APIView):

    def get(self, request, format=None):
        """
        Provide jqTree data for the PageSelect dialog.
        """
        return Response(Page.objects.create_jqtree_data(request.user))


class ListView(ListOrCreateModelView):

    permissions = (IsAuthenticated, )
    renderers = API_RENDERERS


class PaginatedListView(PaginatorMixin, ListView):

    limit = 5

    def check_fields(self, order_by):
        if order_by not in self.orderable_fields:
            raise ErrorResponse(status=HTTP_400_BAD_REQUEST, content="Can not order by the passed value.")


class FileListView(PaginatedListView):

    orderable_fields = ('filename', 'updated')

    def get_queryset(self, *args, **kwargs):
        qs = super(FileListView, self).get_queryset(*args, **kwargs)
        qs = PERMISSIONS.filter_files(self.request.user, qs)
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
        qs = PERMISSIONS.filter_images(self.request.user, qs)
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


class MovePageView(View):

    permissions = (IsAdminUser, )
    renderers = API_RENDERERS

    form = MovePageForm

    def get(self, request, pk):
        if not PERMISSIONS.can_move_page(self.request.user, Page.objects.get(id=pk)):
            raise _403_FORBIDDEN_RESPONSE
        return 'Exposes the `Page.move_page` method'

    def put(self, request, pk):
        if not PERMISSIONS.can_move_page(self.request.user, Page.objects.get(id=pk)):
            raise _403_FORBIDDEN_RESPONSE
        position = self.CONTENT['position']
        target = self.CONTENT['target_node_id']
        page = Page.objects.get(id=pk)
        page.move_page(target, position)


class MovePageContentItemView(View):

    permissions = (IsAdminUser, )
    renderers = API_RENDERERS

    form = MovePageContentItemForm

    def get(self, request, pk):
        if not PERMISSIONS.can_edit(self.request.user, Page.objects.get(page_content_items__id=pk)):
            raise _403_FORBIDDEN_RESPONSE
        return 'Exposes the `PageContentItem.move` method'

    def put(self, request, pk):
        if not PERMISSIONS.can_edit(self.request.user, Page.objects.get(page_content_items__id=pk)):
            raise _403_FORBIDDEN_RESPONSE
        page_content_item = PageContentItem.objects.get(id=pk)
        before_page_content_item_id = self.CONTENT.get('before_page_content_item_id', None)
        block_name = self.CONTENT.get('block_name', None)
        page_content_item.move(before_page_content_item_id, block_name)
