from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _

from rest_framework import generics
from rest_framework import renderers
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import views
from rest_framework import status
from rest_framework import permissions

from fiber.models import Page, PageContentItem, ContentItem, File, Image
from fiber.app_settings import API_RENDER_HTML, PERMISSION_CLASS
from fiber.utils.import_util import load_class

from .serializers import PageSerializer, MovePageSerializer, PageContentItemSerializer, MovePageContentItemSerializer, ContentItemSerializer, FileSerializer, ImageSerializer, FiberPaginationSerializer

PERMISSIONS = load_class(PERMISSION_CLASS)

API_RENDERERS = (renderers.JSONRenderer, )
if API_RENDER_HTML:
    API_RENDERERS = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)

_403_FORBIDDEN_RESPONSE = Response(
    {
    'detail': 'You do not have permission to access this resource. ' +
    'You may need to login or otherwise authenticate the request.'
    },
    status.HTTP_403_FORBIDDEN)


class PlainText(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, media_type=None, renderer_context=None):
        if isinstance(data, str):
            return data
        return smart_str(data)


class IEUploadFixMixin:
    """
    A Mixin that fixes issues with IE 8 and IE 9 file uploads.
    Both user agents expect plain text responses when uploading files.

    See https://github.com/valums/file-uploader/blob/master/readme.md#internet-explorer-limitations
    """

    def get_renderers(self):
        user_agent = self.request._request.META['HTTP_USER_AGENT']
        if self.request.method == 'POST' and ('MSIE 8' in user_agent or 'MSIE 9' in user_agent):
            return [PlainText()]
        return super().get_renderers()


class FiberListCreateAPIView(generics.ListCreateAPIView):
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if hasattr(self, 'object'):
            PERMISSIONS.object_created(request.user, self.object)
        return response


class PageList(FiberListCreateAPIView):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    renderer_classes = API_RENDERERS
    permission_classes = (permissions.IsAdminUser,)


class PageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    renderer_classes = API_RENDERERS
    permission_classes = (permissions.IsAdminUser,)


class MovePageView(views.APIView):
    serializer_class = MovePageSerializer
    renderer_classes = API_RENDERERS
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, pk, format=None):
        if not PERMISSIONS.can_move_page(request.user, Page.objects.get(id=pk)):
            return _403_FORBIDDEN_RESPONSE
        return Response('Exposes the `Page.move_page` method')

    def put(self, request, pk, format=None):
        if not PERMISSIONS.can_move_page(request.user, Page.objects.get(id=pk)):
            return _403_FORBIDDEN_RESPONSE
        position = request.data.get('position')
        target = request.data.get('target_node_id')
        page = Page.objects.get(id=pk)
        page.move_page(target, position)
        return Response('Page moved successfully.')


class PageContentItemList(FiberListCreateAPIView):
    queryset = PageContentItem.objects.all()
    serializer_class = PageContentItemSerializer
    renderer_classes = API_RENDERERS
    permission_classes = (permissions.IsAdminUser,)


class PageContentItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PageContentItem.objects.all()
    serializer_class = PageContentItemSerializer
    renderer_classes = API_RENDERERS
    permission_classes = (permissions.IsAdminUser,)


class MovePageContentItemView(views.APIView):
    serializer_class = MovePageContentItemSerializer
    renderer_classes = API_RENDERERS
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, pk, format=None):
        if not PERMISSIONS.can_edit(request.user, Page.objects.get(page_content_items__id=pk)):
            return _403_FORBIDDEN_RESPONSE
        return Response('Exposes the `PageContentItem.move` method')

    def put(self, request, pk, format=None):
        if not PERMISSIONS.can_edit(request.user, Page.objects.get(page_content_items__id=pk)):
            return _403_FORBIDDEN_RESPONSE
        page_content_item = PageContentItem.objects.get(id=pk)
        before_page_content_item_id = request.data.get('before_page_content_item_id')
        block_name = request.data.get('block_name')
        page_content_item.move(before_page_content_item_id, block_name)
        return Response('PageContentItem moved successfully.')


class ContentItemList(FiberListCreateAPIView):
    queryset = ContentItem.objects.all()
    serializer_class = ContentItemSerializer
    renderer_classes = API_RENDERERS
    permission_classes = (permissions.IsAdminUser,)


class ContentItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContentItem.objects.all()
    serializer_class = ContentItemSerializer
    renderer_classes = API_RENDERERS
    permission_classes = (permissions.IsAdminUser,)


class FileList(IEUploadFixMixin, FiberListCreateAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    renderer_classes = API_RENDERERS
    permission_classes = (permissions.IsAdminUser,)

    pagination_class = FiberPaginationSerializer

    orderable_fields = ('filename', 'updated')

    def check_fields(self, order_by):
        if order_by not in self.orderable_fields:
            return Response("Can not order by the passed value.", status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = PERMISSIONS.filter_files(self.request.user, qs)
        search = self.request.query_params.get('search')

        if search:
            qs = qs.filter(file__icontains=search)

        order_by = self.request.query_params.get('order_by', 'updated')
        self.check_fields(order_by)

        if order_by == 'filename':
            order_by = 'file'

        sort_order = self.request.query_params.get('sortorder', 'asc')

        qs = qs.order_by('{}{}'.format('-' if sort_order != 'asc' else '', order_by))

        return qs


class FileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    renderer_classes = API_RENDERERS
    permission_classes = (permissions.IsAdminUser,)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        file_name = obj.get_filename()
        delete_response = ''

        if not request.user.has_perm('fiber.delete_image'):
            delete_response = _("You don't have permission to delete %(file_name)s.") % {
                'file_name': file_name
            }
            return Response(delete_response, status=403)

        try:
            obj.delete()
            delete_response = _("Successfully deleted %(file_name)s.") % {
                'file_name': file_name
            }
        except ProtectedError:
            delete_response = _("%(file_name)s is not deleted, because that would require deleting protected related objects.") % {
                'file_name': file_name
            }

        return Response(delete_response, status=200)


class ImageList(IEUploadFixMixin, FiberListCreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    renderer_classes = API_RENDERERS
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = FiberPaginationSerializer
    orderable_fields = ('filename', 'size', 'updated')

    def check_fields(self, order_by):
        if order_by not in self.orderable_fields:
            return Response("Can not order by the passed value.", status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = PERMISSIONS.filter_images(self.request.user, qs)
        search = self.request.query_params.get('search')
        if search:
            # TODO: image_icontains searches in the entire path, it should only search in the filename (use iregex for this?)
            qs = qs.filter(Q(image__icontains=search) | Q(title__icontains=search) | Q(width__icontains=search) | Q(height__icontains=search))

        order_by = self.request.query_params.get('order_by', 'updated')
        self.check_fields(order_by)

        if order_by == 'filename':
            order_by = 'image'
        elif order_by == 'size':
            order_by = 'width'

        sort_order = self.request.query_params.get('sortorder', 'asc')

        qs = qs.order_by('{}{}'.format('-' if sort_order != 'asc' else '', order_by))

        return qs


class ImageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    renderer_classes = API_RENDERERS
    permission_classes = (permissions.IsAdminUser,)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        file_name = obj.get_filename()
        delete_response = ''

        if not request.user.has_perm('fiber.delete_image'):
            delete_response = _("You don't have permission to delete %(file_name)s.") % {
                'file_name': file_name
            }
            return Response(delete_response, status=403)

        try:
            obj.delete()
            delete_response = _("Successfully deleted %(file_name)s.") % {
                'file_name': file_name
            }
        except ProtectedError:
            delete_response = _("%(file_name)s is not deleted, because that would require deleting protected related objects.") % {
                'file_name': file_name
            }

        return Response(delete_response, status=200)


@api_view(('GET',))
@renderer_classes(API_RENDERERS)
@permission_classes((permissions.IsAdminUser, ))
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
    renderer_classes = API_RENDERERS
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, format=None):
        """
        Provide jqTree data for the PageSelect dialog.
        """
        return Response(Page.objects.create_jqtree_data(request.user))


class ContentItemGroups(views.APIView):
    renderer_classes = API_RENDERERS
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, format=None):
        """
        Get content groups data which is suitable for jqtree.
        """
        return Response(ContentItem.objects.get_content_groups(request.user))
