from rest_framework import serializers

from fiber.models import Page, PageContentItem, ContentItem, File, Image

from .fields import CanEditField, UpdatedField


POSITION_CHOICES = sorted((item, item) for item in ['before', 'after', 'inside'])


class MovePageSerializer(serializers.Serializer):
    position = serializers.ChoiceField(choices=POSITION_CHOICES)
    target_node_id = serializers.IntegerField()


class PageContentItemSerializer(serializers.ModelSerializer):
    move_url = serializers.HyperlinkedIdentityField(view_name='pagecontentitem-move')

    class Meta:
        model = PageContentItem
        depth = 1


class ContentItemShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentItem
        depth = 1
        fields = [
            'created',
            'name',
            'content_html',
        ]


class PageContentItemShortSerializer(serializers.ModelSerializer):
    content_item = ContentItemShortSerializer()

    class Meta:
        model = PageContentItem
        fields = [
            'content_item',
        ]



class MovePageContentItemSerializer(serializers.Serializer):
    before_page_content_item_id = serializers.IntegerField(required=False)
    block_name = serializers.CharField()


class ContentItemSerializer(serializers.ModelSerializer):
    #depth = 1

    class Meta:
        model = ContentItem
        depth = 1
        fields = [
            'name',
            'content_markup',
            'content_html',
            'protected',
            'metadata',
            'template_name',
        ]


class PageSerializer(serializers.ModelSerializer):
    #contentitems = ContentItemSerializer(read_only=True, many=True)
    page_content_items = PageContentItemShortSerializer(many=True)

    class Meta:
        model = Page
        depth = 1
        fields = [
            'site_id',
            'url',
            'title',
            'doc_title',
            'get_absolute_url',
            'redirect_page',
            'template_name',
            'show_in_menu',
            'page_content_items',
            'metadata',
            'image',
            'created',
            'updated',
            'level'
        ]


class FileSerializer(serializers.HyperlinkedModelSerializer):
    file_url = serializers.ReadOnlyField(source='file.url')
    filename = serializers.ReadOnlyField(source='get_filename')
    #can_edit = CanEditField(read_only=True)
    #updated = UpdatedField()

    class Meta:
        model = File
        read_only_fields = ('created', )


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    image_url = serializers.ReadOnlyField(source='image.url')
    thumbnail_url = serializers.ReadOnlyField()
    filename = serializers.ReadOnlyField(source='get_filename')
    size = serializers.ReadOnlyField(source='get_size')
    #can_edit = CanEditField(default=1, read_only=True)
    #updated = UpdatedField(required=False)

    class Meta:
        model = Image
        read_only_fields = ('created', 'image_url', 'filename', 'size', 'can_edit', 'thumbnail_url',  )

# FIXME: This used to inherit from rest_framework.pagination.BasePaginationSerializer, however
# the way django-rest-framework handles pagination has changed. Figure out how to fix this.
# class FiberPaginationSerializer(pagination.BasePaginationSerializer):
class FiberPaginationSerializer(serializers.Serializer):
    """
    Simple-data-grid expects a total_pages key for a paginated view.
    Simple-data-grid expects rows as the key for objects.
    """
    total_pages = serializers.Field(source='paginator.num_pages')
    results_field = 'rows'


class IdCounterSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
