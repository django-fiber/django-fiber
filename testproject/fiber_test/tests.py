from django.test import TestCase

from fiber.models import Page, ContentItem, PageContentItem


class FiberTests(TestCase):
    def test_fiber(self):
        # setup
        frontpage = Page.objects.create(title='frontpage', url='/')
        lorem_ipsum = ContentItem.objects.create(content_html='lorem ipsum')
        PageContentItem.objects.create(page=frontpage, content_item=lorem_ipsum, block_name='main')

        # - get page
        response = self.client.get('/')
        self.assertContains(response, 'lorem ipsum')