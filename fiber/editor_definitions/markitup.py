from textile import Textile


"""
Monkeypatch Textile - Disable glyphs substitution.
"""
def custom_glyphs(self, text):
    return text

Textile.glyphs = custom_glyphs


def textile_renderer(text):
    rendered_textile = Textile().textile(text)
    return rendered_textile

EDITOR = {
    'template_js': 'fiber/markitup_js.html',
    'template_css': 'fiber/markitup_css.html',
    'renderer': textile_renderer,
    'rename_url_expressions': (r':%s', r':%s'),
}
