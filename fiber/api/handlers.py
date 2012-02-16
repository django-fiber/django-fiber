import os
from unicodedata import normalize

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import F, Max

from piston.handler import BaseHandler
from piston.utils import rc

from fiber.utils.date import friendly_datetime

from fiber.models import Page, PageContentItem, ContentItem, Image, File



class PageHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    fields = ('data', 'children', 'show_in_menu')
    model = Page

    @classmethod
    def data(cls, page):
        return {
            'title': page.title,
            'attr': {
                'data-fiber-data': '{"type": "page", "id": %d}' % page.id,
                'href': page.get_absolute_url(),
            }
        }

    @classmethod
    def children(cls, page):
        return page.get_children()

    def read(self, request, id=None):
        if id:
            return self.read_page(id)
        else:
            return self.read_trees()

    def read_trees(self):
        return Page.objects.filter(level=0).order_by('tree_id')

    def read_page(self, page_id):
        page = Page.objects.get(id=page_id)

        # Do not include the data of the child pages.
        page.children = None
        return page

    def create(self, request):
        """
        Creates a new Page, either placed in the same level before or after a certain Page,
        or as last child below a certain parent Page.
        """
        attrs = self.flatten_dict(request.POST)

        try:
            page_title = attrs['title']
            page_relative_url = attrs['relative_url']
        except KeyError:
            return rc.BAD_REQUEST

        page = Page(title=page_title, relative_url=page_relative_url)

        if 'before_page_id' in attrs:
            before_page = Page.objects.get(pk=int(attrs['before_page_id']))
            page.parent = before_page.parent
            page.insert_at(before_page, position='left', save=False)
        elif 'below_page_id' in attrs:
            below_page = Page.objects.get(pk=int(attrs['below_page_id']))
            page.parent = below_page
            page.insert_at(below_page, position='last-child', save=False)

        page.save()
        return rc.CREATED

    def update(self, request, id):
        data = request.data

        if data.get('action') == 'move':
            self._move(
                int(id),
                int(data['target_node_id']),
                data['position']
            )
        else:
            # TODO: check if this situation occurs
            raise Exception('Unsupported action')

    def delete(self, request, id):
        page = Page.objects.get(pk=id)
        page.delete()

        return rc.DELETED

    def _move(self, page_id, target_id, position):
        page = Page.objects.get(pk=page_id)
        page.move_page(target_id, position)


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
                sort = sort_max + 1
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


class ImageHandler(BaseHandler):
    allowed_methods = ('GET', )
    fields = ('id', 'url', 'image', 'filename', 'size', 'updated')
    exclude = () # un-exclude `id`
    model = Image

    @classmethod
    def url(cls, image):
        return image.image.url

    @classmethod
    def image(cls, image):
        return image.image.url

    @classmethod
    def filename(cls, image):
        return os.path.basename(image.image.name)

    @classmethod
    def size(cls, image):
        return '%s x %d' % (image.width, image.height)

    @classmethod
    def updated(cls, image):
        return friendly_datetime(image.updated)

    def read(self, request):
        rows = int(request.GET['rows'])
        page = int(request.GET['page'])
        if 'filename' in request.GET:
            filename = request.GET['filename']
        else:
            filename = ''
        limit = page*rows
        offset = (page-1)*rows
        order_by = request.GET['sidx']
        order_reversed = (request.GET['sord'] == 'desc')  #desc or asc
        if order_by == 'updated':
            order_clause = 'updated'
        elif order_by == 'filename':
            order_clause = 'image'
        elif order_by == 'size':
            order_clause = 'width'

        if order_reversed:
            order_clause = '-%s' % order_clause

        images = Image.objects.filter(image__icontains=filename).order_by(order_clause)[offset:limit]
        return images


class FileHandler(BaseHandler):
    allowed_methods = ('GET', )
    fields = ('id', 'url', 'filename', 'updated')
    exclude = () # un-exclude `id`
    model = File

    @classmethod
    def url(cls, file):
        return file.file.url

    @classmethod
    def filename(cls, file):
        return os.path.basename(file.file.name)

    @classmethod
    def updated(cls, file):
        return friendly_datetime(file.updated)

    def read(self, request):
        rows = int(request.GET['rows'])
        page = int(request.GET['page'])
        if 'filename' in request.GET:
            filename = request.GET['filename']
        else:
            filename = ''
        limit = page*rows
        offset = (page-1)*rows
        order_by = request.GET['sidx']
        order_reversed = (request.GET['sord'] == 'desc')  #desc or asc
        if order_by == 'updated':
            order_clause = 'updated'
        elif order_by == 'filename':
            order_clause = 'file'

        if order_reversed:
            order_clause = '-%s' % order_clause

        files = File.objects.filter(file__icontains=filename).order_by(order_clause)[offset:limit]

        return files

    def create(self, request):
        File.objects.create(
            file=request.FILES['file'],
            title='uploaded',  # TODO: empty title
        )
        return rc.CREATED


class FileUploadHandler(BaseHandler):
    allowed_methods = ('POST',)

    def save_xhr(self, request):
        filename = request.GET['qqfile']
        file = SimpleUploadedFile(filename, request.raw_post_data)
        file.name = normalize('NFC', file.name)

        expected_length = int(request.environ.get('CONTENT_LENGTH', 0))
        if expected_length != file.size:
            raise Exception('File not fully uploaded')

        File.objects.create(
            file=file,
            title='uploaded',  # TODO: empty title
        )
        return rc.CREATED

    def save_form(self, request):
        file = request.FILES['qqfile']
        file.name = normalize('NFC', file.name)

        File.objects.create(
            file=file,
            title='uploaded',  # TODO: empty title
        )
        return rc.CREATED

    def create(self, request):
        if 'qqfile' in request.GET:
            return self.save_xhr(request)
        elif 'qqfile' in request.FILES:
            return self.save_form(request)
        else:
            raise Exception('Cannot upload file; no data found in request')


class ImageUploadHandler(BaseHandler):
    allowed_methods = ('POST',)

    def save_xhr(self, request):
        filename = request.GET['qqfile']
        file = SimpleUploadedFile(filename, request.raw_post_data)
        file.name = normalize('NFC', file.name)

        expected_length = int(request.environ.get('CONTENT_LENGTH', 0))
        if expected_length != file.size:
            raise Exception('File not fully uploaded')

        Image.objects.create(
            image=file,
            title='uploaded',  # TODO: empty title
        )
        return rc.CREATED

    def save_form(self, request):
        file = request.FILES['qqfile']
        file.name = normalize('NFC', file.name)

        Image.objects.create(
            image=file,
            title='uploaded',  # TODO: empty title
        )
        return rc.CREATED

    def create(self, request):
        if 'qqfile' in request.GET:
            return self.save_xhr(request)
        elif 'qqfile' in request.FILES:
            return self.save_form(request)
        else:
            raise Exception('Cannot upload file; no data found in request')


class ContentItemHandler(BaseHandler):
    allowed_methods = ('DELETE',)
    model = ContentItem
