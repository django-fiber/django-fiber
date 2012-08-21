"""
Module that provides a base Permission class. This class may be overridden by changinng the `API_PERMISSION_CLASS` value in the settings module.
"""


class Permissions(object):
    """
    This class defines the methods that a Permission class may implement.

    By default all permissions are granted to a superuser.
    """

    def filter_objects(self, user, qs):
        """
        Should only return those objects which `user` is allowed to edit.
        """
        return qs

    def can_edit_page(self, user, page):
        """
        True if user is allowed to edit the Page instance.
        """
        return True

    def can_move_page(self, user, page):
        return True

