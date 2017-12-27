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

AUTO_CREATE_CONTENT_ITEMS = getattr(settings, 'FIBER_AUTO_CREATE_CONTENT_ITEMS', False)

METADATA_PAGE_SCHEMA = getattr(settings, 'FIBER_METADATA_PAGE_SCHEMA', {})
METADATA_CONTENT_SCHEMA = getattr(settings, 'FIBER_METADATA_CONTENT_SCHEMA', {})

API_RENDER_HTML = getattr(settings, 'API_RENDER_HTML', False)

IMAGE_PREVIEW = getattr(settings, 'FIBER_IMAGE_PREVIEW', True)
LIST_THUMBNAIL_OPTIONS = getattr(settings, 'FIBER_LIST_THUMBNAIL_OPTIONS', {'size': (111, 111)})
DETAIL_THUMBNAIL_OPTIONS = getattr(settings, 'FIBER_DETAIL_THUMBNAIL_OPTIONS', {'size': (228, 228)})

"""
Point this class to your own Permission Class as declared in :mod:`fiber.permissions`.
"""
PERMISSION_CLASS = getattr(settings, 'PERMISSION_CLASS', 'fiber.permissions.Permissions')
