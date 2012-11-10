from rest_framework import serializers

from fiber.models import Page


class PageSerializer(serializers.HyperlinkedModelSerializer):
    move_url = serializers.HyperlinkedIdentityField(view_name='page-resource-instance-move')
    page_url = serializers.Field(source='get_absolute_url')
    class Meta:
        model = Page
