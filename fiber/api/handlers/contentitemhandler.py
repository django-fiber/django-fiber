from fiber.models import ContentItem
from piston.handler import BaseHandler


class ContentItemHandler(BaseHandler):
    allowed_methods = ('DELETE',)
    model = ContentItem
