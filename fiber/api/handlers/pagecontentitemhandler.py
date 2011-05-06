from django.db.models import F, Max
from fiber.models import PageContentItem, ContentItem, Page
from piston.handler import BaseHandler
from piston.utils import rc


class PageContentItemHandler(BaseHandler):
    allowed_methods = ('POST', 'PUT', 'DELETE')
    model = PageContentItem

    def create(self, request):
        """
        Creates a new PageContentItem.
        """
        attrs = self.flatten_dict(request.POST)

        content_item = ContentItem.objects.get(pk=int(attrs['content_item_id']))

        if 'before_page_content_item_id' in attrs:
            before_page_content_item = PageContentItem.objects.get(pk=int(attrs['before_page_content_item_id']))
            page = Page.objects.get(pk=before_page_content_item.page.id)
            block_name = before_page_content_item.block_name
            sort = before_page_content_item.sort

            # make room for new content item
            PageContentItem.objects.filter(block_name=block_name).filter(sort__gte=sort).update(sort=F('sort')+1)
        else:
            page = Page.objects.get(pk=int(attrs['page_id']))
            block_name = attrs['block_name']

            all_page_content_items = PageContentItem.objects.filter(block_name=block_name).order_by('sort')
            sort_max = all_page_content_items.aggregate(Max('sort'))['sort__max']
            if sort_max != None:
                sort =  sort_max + 1
            else:
                sort = 0

        page_content_item = PageContentItem(content_item=content_item, page=page, block_name=block_name, sort=sort)
        page_content_item.save()
        return rc.CREATED

    def update(self, request, id):
        page_content_item = PageContentItem.objects.get(pk=id)

        data = request.data
        if 'action' in data:
            if data['action'] == 'move':
                next = None
                if 'before_page_content_item_id' in data:
                    next_id = int(data['before_page_content_item_id'])
                    if next_id:
                        next = PageContentItem.objects.get(pk=next_id)

                block_name = data.get('block_name')

                PageContentItem.objects.move(page_content_item, next, block_name=block_name)
                page_content_item = PageContentItem.objects.get(pk=id)

        return page_content_item

    def delete(self, request, id):
        page_content_item = PageContentItem.objects.get(pk=id)
        page_content_item.delete()

        return rc.DELETED
