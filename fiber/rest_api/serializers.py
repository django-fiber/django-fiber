from rest_framework import pagination, response, serializers

from fiber.models import Page, PageContentItem, ContentItem, File, Image

from .fields import CanEditField, UpdatedField


POSITION_CHOICES = sorted((item, item) for item in ['before', 'after', 'inside'])


class PageSerializer(serializers.ModelSerializer):
    move_url = serializers.HyperlinkedIdentityField(view_name='page-move')
    page_url = serializers.ReadOnlyField(source='get_absolute_url')
    depth = 1

    class Meta:
        model = Page
        fields = '__all__'

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
        fields = '__all__'


class MovePageContentItemSerializer(serializers.Serializer):
    before_page_content_item_id = serializers.IntegerField(required=False)
    block_name = serializers.CharField()


class ContentItemSerializer(serializers.ModelSerializer):
    depth = 1

    class Meta:
        model = ContentItem
        fields = '__all__'


class FileSerializer(serializers.HyperlinkedModelSerializer):
    file_url = serializers.ReadOnlyField(source='file.url')
    filename = serializers.ReadOnlyField(source='get_filename')
    can_edit = CanEditField()
    updated = UpdatedField()

    class Meta:
        model = File
        fields = '__all__'
        read_only_fields = ('created', )


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    image_url = serializers.ReadOnlyField(source='image.url')
    thumbnail_url = serializers.ReadOnlyField()
    filename = serializers.ReadOnlyField(source='get_filename')
    size = serializers.ReadOnlyField(source='get_size')
    can_edit = CanEditField()
    updated = UpdatedField()

    class Meta:
        model = Image
        fields = '__all__'
        read_only_fields = ('created', )


class FiberPaginationSerializer(pagination.PageNumberPagination):
    """
    Simple-data-grid expects a total_pages key for a paginated view.
    Simple-data-grid expects rows as the key for objects.
    """
    total_pages = serializers.ReadOnlyField(source='paginator.num_pages')
    results_field = 'rows'
    page_size = 5

    def get_paginated_response(self, data):
        return response.Response({
            'total_pages': self.page.paginator.num_pages,
            'rows': data
        })
