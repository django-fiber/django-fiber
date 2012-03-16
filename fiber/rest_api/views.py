"""
The root view for the rest api.
"""

from django.core.urlresolvers import reverse
from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated

class ApiRoot(View):

    permissions = (IsAuthenticated, )
    
    def get(self, request):
        return [{'name': 'pages', 'url': reverse('page-resource-root')},
                {'name': 'page content items', 'url': reverse('page-content-item-resource-root')},
                {'name': 'content items', 'url': reverse('content-item-resource-root')},
                {'name': 'images', 'url': reverse('image-resource-root')},
                {'name': 'files', 'url': reverse('file-resource-root')},
                ]

