from django.conf import settings


LOGIN_STRING = getattr(settings, 'FIBER_LOGIN_STRING', '@fiber')

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

PAGE_MANAGER = getattr(settings, 'FIBER_PAGE_MANAGER', 'fiber.managers.PageManager')
CONTENT_ITEM_MANAGER = getattr(settings, 'FIBER_CONTENT_ITEM_MANAGER', 'fiber.managers.ContentItemManager')

METADATA_PAGE_SCHEMA = getattr(settings, 'FIBER_METADATA_PAGE_SCHEMA', {})
METADATA_CONTENT_SCHEMA = getattr(settings, 'FIBER_METADATA_CONTENT_SCHEMA', {})

API_RENDER_HTML = getattr(settings, 'API_RENDER_HTML', False)

"""
Point this class to your own Permission Class as declared in :mod:`fiber.permissions`.
"""
PERMISSION_CLASS = getattr(settings, 'PERMISSION_CLASS', 'fiber.permissions.Permissions')

if 'fiber.middleware.PageFallbackMiddleware' in settings.MIDDLEWARE_CLASSES:
    raise DeprecationWarning(
        "fiber.middleware.PageFallbackMiddleware has been removed.\n"
        "See README.rst for new implementation details.\n"
        "It basically boils down to this:\n"
        "remove 'fiber.middleware.PageFallbackMiddleware' from settings.MIDDLEWARE_CLASSES, and\n"
        "add (r'', 'fiber.views.page') to the end of your urls.py")
