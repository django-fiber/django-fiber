from textile import textile


EDITOR = {
    'template_js': 'fiber/markitup_js.html',
    'template_css': 'fiber/markitup_css.html',
    'renderer': textile,
    'rename_url_expressions': (r':%s', r':%s')
}
