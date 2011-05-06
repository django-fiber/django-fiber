from piston.handler import BaseHandler
from piston.utils import rc
from fiber.models import Image


class ImageUploadHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        Image.objects.create(
            image=request.FILES['file'],
            title='uploaded',  # TODO: empty title
        )
        return rc.CREATED
