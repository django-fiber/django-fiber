from .app_settings import EDITOR
from .utils.import_util import import_element


editor = import_element(EDITOR)
renderer = editor.get('renderer', None)


def get_editor_field_name(html_field_name):
    """
    Returns markup or html field name, depending on editor.
    Input is html field_name:

    get_editor_field_name('content_html')

    returns: 'content_html' or 'content_markup'
    """
    if renderer:
        return html_field_name.replace('_html', '_markup')
    else:
        return html_field_name
