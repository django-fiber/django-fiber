"""
    >>> from django.contrib.auth.models import User
    >>> u = User.objects.get(username='example-user')
    >>> from guardian.shortcuts import assign
    >>> from fiber.models import Page
    >>> p = Page.objects.get(title='A')
    >>> assign('change_page', u, p)
"""

from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_delete

from guardian.shortcuts import get_objects_for_user, get_perms, assign
from guardian.models import UserObjectPermission

from fiber.permissions import Permissions
from fiber.models import Image, File, Page, PageContentItem, ContentItem


PAGE_PERMISSIONS = ('change_page', 'delete_page')
CONTENTITEM_PERMISSIONS = ('change_contentitem', 'delete_contentitem')


def remove_obj_perms_connected_with_object(sender, instance, **kwargs):
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
        object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()


class CustomPermissions(Permissions):

    def __init__(self):
        """
        Since guardian does not delete permission-objects, when the objects that
        they point to are deleted, we must take care of deleting them our selves.
        See http://packages.python.org/django-guardian/userguide/caveats.html?highlight=caveat
        """
        pre_delete.connect(remove_obj_perms_connected_with_object, sender=Image)
        pre_delete.connect(remove_obj_perms_connected_with_object, sender=File)
        pre_delete.connect(remove_obj_perms_connected_with_object, sender=Page)
        pre_delete.connect(remove_obj_perms_connected_with_object, sender=PageContentItem)
        pre_delete.connect(remove_obj_perms_connected_with_object, sender=ContentItem)

    def filter_objects(self, user, qs):
        """
        Returns all objects that `user` is allowed to change, based on guardian permissions.
        Returns all objects if user is superuser.
        """
        if user.is_superuser:
            return qs
        return qs.filter(id__in=get_objects_for_user(user, 'change_%s' % qs.model.__name__.lower(), qs.model))

    def can_edit(self, user, obj):
        """
        Returns True if `user` is allowed to edit `obj` based on guardian permissions.
        """
        return 'change_%s' % obj.__class__.__name__.lower() in get_perms(user, obj)

    def can_move_page(self, user, page):
        """
        A user with change-permissions is allowed to move the page.
        A superuser always has all permissions as far as guardian is concerned.
        """
        return 'change_page' in get_perms(user, page)

    def object_created(self, user, obj):
        """
        Create 'change' permission to `obj` for `user`.
        """
        assign('change_%s' % obj.__class__.__name__.lower(), user, obj)

    def _filter_user_and_superuser(self, user, qs):
        """
        A user should see files and images owned by him and by the superuser.
        Files uploaded by other non-superusers should not be listed.

        Note - there should be only one superuser in the User model.
        """
        superuser = User.objects.get(is_superuser=True)

        qs = qs.filter(Q(id__in=get_objects_for_user(user, 'change_%s' % qs.model.__name__.lower(), qs.model)) |
            Q(id__in=get_objects_for_user(superuser, 'change_%s' % qs.model.__name__.lower(), qs.model)))
        return qs

    def filter_images(self, user, qs):
        return self._filter_user_and_superuser(user, qs)

    def filter_files(self, user, qs):
        return self._filter_user_and_superuser(user, qs)
