from django.db import models

from rest_framework import serializers

from fiber.models import Page, PageContentItem, ContentItem, Image


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


class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.Field(source='image.url')
    filename = serializers.Field(source='get_filename')
    size = serializers.Field(source='get_size')
    class Meta:
        model = Image
        read_only_fields = ('created', 'updated')

#class ImageResource(FileResource):
#    model = Image
#
#    def can_edit(self, instance):
#        return PERMISSIONS.can_edit(self.view.user, instance)

