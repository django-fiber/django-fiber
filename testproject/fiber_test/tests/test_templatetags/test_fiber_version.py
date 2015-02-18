import fiber
from django.test import SimpleTestCase
from ...test_util import RenderMixin


class TestFiberVersion(RenderMixin, SimpleTestCase):
    def test_fiber_version(self):
        self.assertRendered('{% load fiber_tags %}{% fiber_version %}', str(fiber.__version__))
