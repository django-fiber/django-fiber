"""
Module that provides a base Permission class. This class may be overridden by changinng the `API_PERMISSION_CLASS` value in the settings module.
"""


class Permissions(object):
    """
    This class defines the methods that a Permission class must implement.

    By default all permissions are granted to a superuser.
    """

    def filter_pages(self, user, qs):
        """
        Should only return those pages which `user` is allowed to edit.
        """
        return qs

    def can_edit_page(self, user, page):
        return True

    def can_delete_page(self, user, page):
        return True

    def can_add_sub_page(self, user, page):
        return True

    def can_move_page(self, user, page):
        return True

    def filter_content_items(self, user, qs):
        return qs

    def can_edit_content_item(self, user, content_item):
        return True

    def can_delete_content_item(self, user, content_item):
        return True

    def can_add_page_content_item(self, user, page, content_item):
        return True

    def can_delete_page_content_item(self, user, page_content_item):
        return True

    def can_move_page_content_item(self, user, page_content_item):
        return True

