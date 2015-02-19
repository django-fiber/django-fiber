from django.contrib.auth.models import User
from django.test import TestCase
from fiber.models import Page
from fiber.utils.urls import get_admin_change_url
from ...test_util import RenderMixin


class TestEditableAttrs(RenderMixin, TestCase):
    def setUp(self):
        self.home = Page.objects.create(title='home', url='/')
        # Staff user
        self.staff = User.objects.create_user('staff', 'staff@example.com', password='staff')
        self.staff.is_staff = True
        self.staff.save()

    def test_editable_attrs(self):
        """Does nothing if there's not staff user in the context"""
        self.assertRendered(
            '{% load fiber_tags %}{% editable_attrs page %}',
            '', {
                'page': self.home
            })

    def test_editable_attrs_with_page_for_staff(self):
        """Returns fiber-data attribute for fiber page with staff user in context"""
        self.assertRendered(
            '{% load fiber_tags %}{% editable_attrs page %}',
            'data-fiber-data="{&quot;can_edit&quot;: true, &quot;type&quot;: &quot;page&quot;, &quot;url&quot;: &quot;%s&quot;}"' % self.home.get_change_url(), {
                'page': self.home,
                'user': self.staff
            })

    def test_editable_attrs_with_user_for_staff(self):
        """Returns fiber-data attribute for user with staff user in context"""
        self.assertRendered(
            '{% load fiber_tags %}{% editable_attrs user %}',
            'data-fiber-data="{&quot;can_edit&quot;: true, &quot;type&quot;: &quot;user&quot;, &quot;url&quot;: &quot;%s&quot;}"' % get_admin_change_url(self.staff), {
                'user_obj': self.staff,
                'user': self.staff
            })
