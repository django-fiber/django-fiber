def get_thumbnail(image, thumbnail_options):
    try:
        from easy_thumbnails.files import get_thumbnailer
        thumbnailer = get_thumbnailer(image)
        thumbnail = thumbnailer.get_thumbnail(thumbnail_options)
        return thumbnail
    except ImportError:
        return None


def get_thumbnail_url(image, thumbnail_options):
    thumbnail = get_thumbnail(image, thumbnail_options)
    if thumbnail:
        return thumbnail.url
    return None
