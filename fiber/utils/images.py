from easy_thumbnails.files import get_thumbnailer


def get_thumbnail(image):
    thumbnailer = get_thumbnailer(image)
    thumbnail_options = {'size': (128, 128)}
    thumbnail = thumbnailer.get_thumbnail(thumbnail_options)
    return thumbnail


def get_thumbnail_url(image):
    return get_thumbnail(image).url
