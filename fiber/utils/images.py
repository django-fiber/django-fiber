class ThumbnailException(Exception):
    pass


def get_thumbnail(image, thumbnail_options):
    try:
        from easy_thumbnails.files import get_thumbnailer
        from easy_thumbnails.exceptions import InvalidImageFormatError
        try:
            thumbnailer = get_thumbnailer(image)
            thumbnail = thumbnailer.get_thumbnail(thumbnail_options)
            return thumbnail
        except InvalidImageFormatError as e:
            raise ThumbnailException(str(e))
        except OSError as e:
            raise ThumbnailException(str(e))
    except ImportError:
        return


def get_thumbnail_url(image, thumbnail_options):
    try:
        thumbnail = get_thumbnail(image, thumbnail_options)
        if thumbnail:
            return thumbnail.url
    except ThumbnailException:
        return
    return
