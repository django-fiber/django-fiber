"""
Module that provides a base Permission class. This class may be overridden by changing the `PERMISSION_CLASS` value in the settings module.
"""


class Permissions:
    """
    This class defines the methods that a Permission class should implement.

    By default all permissions are granted to a staff user.
    """

    def filter_objects(self, user, qs):
        """
        Should only return those objects whose `user` is allowed to edit.
        `qs` can consist of type `Page` or `ContentItem`.
        """
        return qs

    def filter_images(self, user, qs):
        """
        Called by API while listing images.
        """
        return qs

    def filter_files(self, user, qs):
        """
        Called by API while listing files.
        """
        return qs

    def can_edit(self, user, obj):
        """
        Should return :const:`True` if user is allowed to edit `obj`.
        """
        return user.is_staff

    def can_move_page(self, user, page):
        """
        Should return :const:`True` if user is allowed to move page.
        """
        return user.is_staff

    def object_created(self, user, obj):
        """
        Called whenever a new instance has been created of one of Fiber's models by `user`.
        """
        pass

    def is_fiber_editor(self, user):
        """
        Determines if the user is allowd to see the Fiber admin interface.
        """
        return True

