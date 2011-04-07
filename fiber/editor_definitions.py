from textile import textile


CKEditor = {
    'template_js': 'fiber/ckeditor_js.html'
}

Markitup = {
	'template_js': 'fiber/markitup_js.html',
	'template_css': 'fiber/markitup_css.html',
	'renderer': textile,
	'rename_url_expressions': (r':%s', r':%s')
}
