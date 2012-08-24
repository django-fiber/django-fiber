"""
Module that provides a base Permission class. This class may be overridden by changinng the `PERMISSION_CLASS` value in the settings module.
"""


class Permissions(object):
    """
    This class defines the methods that a Permission class may implement.

    By default all permissions are granted to a staffuser.
    """

    def filter_objects(self, user, qs):
        """
        Should only return those objects which `user` is allowed to edit.
        `qs` can consist of type `Page` or `ContentItem`.
        """
        return qs

    def filter_images(self, user, qs):
        """
        Called by api while listing images.
        """
        return qs

    def filter_files(self, user, qs):
        """
        Called by api while listing files.
        """
        return qs

    def can_edit(self, user, obj):
        """
        Should return :const:`True` if user is allowed to edit `obj`.
        """
        return True

    def can_move_page(self, user, page):
        """
        Should return :const:`True` if user is allowed to move page.
        """
        return True

    def object_created(self, user, obj):
        """
        Called whenever a new instance has been created of one of Fiber's models by `user`.
        """
        pass

