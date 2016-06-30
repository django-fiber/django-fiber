from rest_framework import serializers

from fiber.models import Page, PageContentItem, ContentItem, File, Image

from .fields import CanEditField, UpdatedField


POSITION_CHOICES = sorted((item, item) for item in ['before', 'after', 'inside'])


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
