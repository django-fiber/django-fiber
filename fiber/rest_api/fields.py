from rest_framework import serializers

from fiber.app_settings import PERMISSION_CLASS
from fiber.utils.import_util import load_class
from fiber.utils.date import friendly_datetime

PERMISSIONS = load_class(PERMISSION_CLASS)


class CanEditField(serializers.ReadOnlyField):
    """
    A custom field that returns True if request.user has 
    permission to edit obj.
    """

    def to_representation(self, value):
        return PERMISSIONS.can_edit(self.context['request'].user, obj)


class UpdatedField(serializers.ReadOnlyField):
    """
    Return a friendly timestamp.
    """
    def to_representation(self, value):
        return friendly_datetime(value)
