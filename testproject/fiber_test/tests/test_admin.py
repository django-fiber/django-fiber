from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from fiber.models import Page


class TestPageAdmin(TestCase):
    def test_changelist_renders_links_and_escapes_titles(self):
        user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client.force_login(user)
        root = Page.objects.create(title='Root', url='/')
        pages = [Page.objects.create(title=title, url=f'/page-{index}/', parent=root)
                 for index, title in enumerate(['First', '<b>Middle</b>', 'Last'])]
        response = self.client.get(reverse('admin:fiber_page_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '&lt;b&gt;Middle&lt;/b&gt;')
        self.assertNotContains(response, '<b>Middle</b>')
        self.assertContains(response, f'<a href="{pages[1].pk}/move_up"')
        self.assertContains(response, f'<a href="{pages[1].pk}/move_down"')
        self.assertContains(response, f'<a href="add/?parent={pages[1].pk}"')
        self.assertContains(response, '<a href="/page-1/" title="View on site"')
        self.assertContains(response, '<span class="nobr">')
        self.assertNotContains(response, '&lt;a href=')
        self.assertNotContains(response, '&lt;span')
