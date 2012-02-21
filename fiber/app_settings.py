from django.conf import settings


DEFAULT_TEMPLATE = getattr(settings, 'FIBER_DEFAULT_TEMPLATE', 'base.html')
TEMPLATE_CHOICES = getattr(settings, 'FIBER_TEMPLATE_CHOICES', [])
CONTENT_TEMPLATE_CHOICES = getattr(settings, 'FIBER_CONTENT_TEMPLATE_CHOICES', [])
EXCLUDE_URLS = getattr(settings, 'FIBER_EXCLUDE_URLS', [])

FILES_DIR = getattr(settings, 'FIBER_FILES_DIR', 'uploads/files')
IMAGES_DIR = getattr(settings, 'FIBER_IMAGES_DIR', 'uploads/images')

# MPTT_ADMIN_LEVEL_INDENT defaults to 30
if not hasattr(settings, 'MPTT_ADMIN_LEVEL_INDENT'):
    settings.MPTT_ADMIN_LEVEL_INDENT = 30

EDITOR = getattr(settings, 'FIBER_EDITOR', 'fiber.editor_definitions.ckeditor.EDITOR')

METADATA_PAGE_SCHEMA = getattr(settings, 'FIBER_METADATA_PAGE_SCHEMA', {})
METADATA_CONTENT_SCHEMA = getattr(settings, 'FIBER_METADATA_CONTENT_SCHEMA', {})

if 'fiber.middleware.PageFallbackMiddleware' in settings.MIDDLEWARE_CLASSES:
    raise DeprecationWarning( \
        "fiber.middleware.PageFallbackMiddleware has been removed.\n"
        "See README.rst for new implementation details.\n"
        "It basically boils down to this:\n"
        "remove 'fiber.middleware.PageFallbackMiddleware' from settings.MIDDLEWARE_CLASSES, and\n"
        "add (r'', 'fiber.views.page') to the end of your urls.py")
