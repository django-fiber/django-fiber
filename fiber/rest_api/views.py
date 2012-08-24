from django.db.models import Q
from django.core.urlresolvers import reverse

from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.views import ListOrCreateModelView, InstanceModelView
from djangorestframework.mixins import PaginatorMixin
from djangorestframework.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from djangorestframework.response import ErrorResponse
from djangorestframework.renderers import JSONRenderer, DocumentingHTMLRenderer

from fiber.models import Page, PageContentItem
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

    def post(self, request, *args, **kwargs):
        """
        Notify the Permissions class of a newly created object.
        """
        response = super(ListView, self).post(request, *args, **kwargs)
        PERMISSIONS.object_created(request.user, response.raw_content)  # raw_content is the Model instance
        return response


class TreeListView(View):

    def get(self, request):
        """
        Provide jqTree data for the PageSelect dialog.
        """
        return  Page.objects.create_jqtree_data(request.user)


class PaginatedListView(PaginatorMixin, ListView):

    limit = 5

    def check_fields(self, order_by):
        if order_by not in self.orderable_fields:
            raise ErrorResponse(status=HTTP_400_BAD_REQUEST, content="Can not order by the passed value.")

    def serialize_page_info(self, page):
        """
        simple-data-grid expects a total_pages key for a paginated view.
        """
        return {
            'total_pages': page.paginator.num_pages,
        }

    def filter_response(self, obj):
        """
        simple-data-grid expects rows instead of results (the Django REST framework default)
        """
        obj = super(PaginatedListView, self).filter_response(obj)
        if self.request.method.upper() == 'GET':
            obj['rows'] = obj['results']
            obj.pop('results')
        return obj


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


class InstanceView(InstanceModelView):

    permissions = (IsAuthenticated, )
    renderers = API_RENDERERS

    def delete(self, request, pk):
        if not PERMISSIONS.can_edit(self.request.user, self.resource.model.objects.get(id=pk)):
            raise _403_FORBIDDEN_RESPONSE
        super(InstanceView, self).delete(request, id=pk)


class MovePageView(View):

    permissions = (IsAuthenticated, )
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

    permissions = (IsAuthenticated, )
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
