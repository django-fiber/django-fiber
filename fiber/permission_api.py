from rest_framework.permissions import *


class IsAllOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET'):
            return True
