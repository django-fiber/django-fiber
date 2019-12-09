from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

import fiber.templatetags.fiber_tags

from fiber.models import ContentItem, Page
from ...test_util import RenderMixin


class TestShowContent(RenderMixin, TestCase):
    def setUp(self):
        self.home = Page.objects.create(title='home', url='/')
        self.contact = ContentItem.objects.create(
            name='contact', content_html='<p><a href="mailto:email@example.com">Contact me<a></p>')
        # Staff user
        self.staff = User.objects.create_user('staff', 'staff@example.com', password='staff')
        self.staff.is_staff = True
        self.staff.save()

    def test_show_content(self):
        self.assertRendered(
            '{% load fiber_tags %}{% show_content "contact" %}',
            '<div class="content"><p><a href="mailto:email@example.com">Contact me<a></p></div>')

    def test_show_content_staff_fiber_page(self):
        """Render a content item for a staff user on a fiber page"""
        self.assertRendered(
            '{% load fiber_tags %}{% show_content "contact" %}',
            '''
            <div data-fiber-data='{ "can_edit": true, "type": "content_item", "id": %(contact_pk)s, "url": "%(edit_url_contact)s", "add_url": "", "page_id": 1, "block_name": "" }' class="content">
                <p><a href="mailto:email@example.com">Contact me<a></p>
            </div>''' % {
                'contact_pk': self.contact.pk,
                'edit_url_contact': reverse('fiber_admin:fiber_contentitem_change', args=[self.contact.pk])
            }, {'fiber_page': self.home, 'user': self.staff})

    def test_show_content_staff_non_fiber_page(self):
        """Render a content item for a staff user on a non-fiber page"""
        self.assertRendered(
            '{% load fiber_tags %}{% show_content "contact" %}',
            '''
            <div data-fiber-data='{ "can_edit": true, "type": "content_item", "id": %(contact_pk)s, "url": "%(edit_url_contact)s" }' class="content">
                <p><a href="mailto:email@example.com">Contact me<a></p>
            </div>''' % {
                'contact_pk': self.contact.pk,
                'edit_url_contact': reverse('fiber_admin:fiber_contentitem_change', args=[self.contact.pk])
            }, {'user': self.staff})

    def test_show_content_that_does_not_exist(self):
        self.assertRendered('{% load fiber_tags %}{% show_content "missing" %}', '')


class TestAutoCreate(RenderMixin, TestCase):
    def setUp(self):
        self._auto_create = fiber.templatetags.fiber_tags.AUTO_CREATE_CONTENT_ITEMS
        fiber.templatetags.fiber_tags.AUTO_CREATE_CONTENT_ITEMS = True

        self.staff = User.objects.create_user('staff', 'staff@example.com', password='staff')
        self.staff.is_staff = True
        self.staff.save()

    def tearDown(self):
        fiber.templatetags.fiber_tags.AUTO_CREATE_CONTENT_ITEMS = self._auto_create

    def test_auto_create(self):
        self.assertEqual(ContentItem.objects.all().count(), 0)
        self.assertRendered('{% load fiber_tags %}{% show_content "missing" %}', '<div class="content"></div>')
        self.assertEqual(ContentItem.objects.all().count(), 1)

    def test_auto_create_staff(self):
        self.assertRendered(
            '{% load fiber_tags %}{% show_content "missing" %}',
            '''
            <div data-fiber-data='{ "can_edit": true, "type": "content_item", "id": %(item_pk)s, "url": "%(edit_url_item)s" }' class="content"></div>''' % {
                'item_pk': 1,
                'edit_url_item': reverse('fiber_admin:fiber_contentitem_change', args=[1])
            }, {'user': self.staff})
