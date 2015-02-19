from django.test import TestCase
from fiber.models import Page
from fiber.utils.urls import get_admin_change_url
from ...test_util import RenderMixin


class TestEditableAttrs(RenderMixin, TestCase):
    def setUp(self):
        self.home = Page.objects.create(title='home', url='/')

    def test_editable_attrs(self):
        self.assertRendered(
            '{% load fiber_tags %}{% editable_attrs page %}',
            'data-fiber-data="{&quot;url&quot;: &quot;%s&quot;}"' % get_admin_change_url(self.home), {
                'page': self.home
            })
