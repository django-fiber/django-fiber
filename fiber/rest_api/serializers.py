from rest_framework import serializers

from fiber.models import Page, PageContentItem, ContentItem, File, Image

from .fields import CanEditField


class PageSerializer(serializers.ModelSerializer):
    move_url = serializers.HyperlinkedIdentityField(view_name='page-resource-instance-move')
    page_url = serializers.Field(source='get_absolute_url')

    class Meta:
        model = Page


class PageContentItemSerializer(serializers.ModelSerializer):
    move_url = serializers.HyperlinkedIdentityField(view_name='page-content-item-resource-instance-move')

    class Meta:
        model = PageContentItem


class ContentItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContentItem


class FileSerializer(serializers.ModelSerializer):
    file_url = serializers.Field(source='file.url')
    filename = serializers.Field(source='get_filename')
    can_edit = CanEditField()

    class Meta:
        model = File
        read_only_fields = ('created', 'updated')


class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.Field(source='image.url')
    filename = serializers.Field(source='get_filename')
    size = serializers.Field(source='get_size')
    can_edit = CanEditField()

    class Meta:
        model = Image
        read_only_fields = ('created', 'updated')
