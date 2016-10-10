from rest_framework import serializers, pagination

from fiber.models import Page, PageContentItem, ContentItem, File, Image


from fiber.app_settings import PERMISSION_CLASS
from fiber.utils.import_util import load_class
from fiber.utils.date import friendly_datetime

PERMISSIONS = load_class(PERMISSION_CLASS)

POSITION_CHOICES = sorted((item, item) for item in ['before', 'after', 'inside'])


class CanEditMixin(object):
    """
    Adds a 'can_edit' field that returns True if request.user has permission to edit obj.
    """

    can_edit = serializers.SerializerMethodField()

    def get_can_edit(self, obj):
        return PERMISSIONS.can_edit(self.context['request'].user, obj)


class UpdatedMixin(object):

    """
    Adds a 'updated' field that returns a friendly timestamp.
    """
    updated = serializers.SerializerMethodField()

    def get_updated(self, obj):
        return friendly_datetime(obj.updated)


class PageSerializer(serializers.ModelSerializer):
    move_url = serializers.HyperlinkedIdentityField(view_name='page-move')
    page_url = serializers.ReadOnlyField(source='get_absolute_url')
    depth = 1

    class Meta:
        model = Page

    def get_field(self, model_field):
        if model_field.name == 'url':
            return serializers.URLField()


class MovePageSerializer(serializers.Serializer):
    position = serializers.ChoiceField(choices=POSITION_CHOICES)
    target_node_id = serializers.IntegerField()


class PageContentItemSerializer(serializers.ModelSerializer):
    move_url = serializers.HyperlinkedIdentityField(view_name='pagecontentitem-move')
    depth = 1

    class Meta:
        model = PageContentItem


class MovePageContentItemSerializer(serializers.Serializer):
    before_page_content_item_id = serializers.IntegerField(required=False)
    block_name = serializers.CharField()


class ContentItemSerializer(serializers.ModelSerializer):
    depth = 1

    class Meta:
        model = ContentItem


class FileSerializer(CanEditMixin, UpdatedMixin, serializers.HyperlinkedModelSerializer):
    file_url = serializers.Field(source='file.url')
    filename = serializers.Field(source='get_filename')

    class Meta:
        model = File
        read_only_fields = ('created', )


class ImageSerializer(CanEditMixin, UpdatedMixin, serializers.HyperlinkedModelSerializer):
    image_url = serializers.ReadOnlyField(source='image.url')
    thumbnail_url = serializers.ReadOnlyField()
    filename = serializers.ReadOnlyField(source='get_filename')
    size = serializers.ReadOnlyField(source='get_size')

    class Meta:
        model = Image
        read_only_fields = ('created', )


class FiberPaginationSerializer(pagination.BasePaginationSerializer):
    """
    Simple-data-grid expects a total_pages key for a paginated view.
    Simple-data-grid expects rows as the key for objects.
    """
    total_pages = serializers.ReadOnlyField(source='paginator.num_pages')
    results_field = 'rows'
