from fiber.models import File
from piston.handler import BaseHandler
from piston.utils import rc


class FileUploadHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        File.objects.create(
            file=request.FILES['file'],
            title='uploaded',  # TODO: empty title
        )
        return rc.CREATED
