(function($) {

Fiber.enhance_textarea = function(textarea) {

	if (window.CKEDITOR_CONFIG_STYLES_SET) {
		if (!CKEDITOR.stylesSet.get('config_styles_set')) {
			CKEDITOR.stylesSet.add('config_styles_set', window.CKEDITOR_CONFIG_STYLES_SET);
		}
	}

	window.CKEDITOR_CONFIG_TOOLBAR = window.CKEDITOR_CONFIG_TOOLBAR || [
		['Format'],
		window.CKEDITOR_CONFIG_STYLES_SET ? ['Styles'] : null,
		['Bold','Italic'],
		['NumberedList','BulletedList','Outdent','Indent'],
		['fPageLink','fFileLink','fImageLink','fCustomLink','fUnlink'],
		['fImage','fTable'],
		['PasteText','PasteFromWord','RemoveFormat'],
		['Maximize'],
		['Source']
	];

	CKEDITOR.replace(textarea, {
		language: LANGUAGE_CODE,
		extraPlugins: 'fpagelink,ffilelink,fimagelink,fcustomlink,funlink,fimage,ftable,tabletools',
		removePlugins: 'scayt,menubutton,forms,image,link',
		toolbar: window.CKEDITOR_CONFIG_TOOLBAR,
		format_tags: window.CKEDITOR_CONFIG_FORMAT_TAGS || 'p;h2;h3;h4',
		stylesSet: window.CKEDITOR_CONFIG_STYLES_SET || null,
		toolbarCanCollapse: false,
		resize_maxWidth: 610,
		baseFloatZIndex: 1100
	});
};

Fiber.remove_textarea = function(textarea) {
	if (textarea.id in CKEDITOR.instances) {
		CKEDITOR.remove(CKEDITOR.instances[textarea.id]);
	}
};

function extend_CKEditor() {

	// fPageLink
	var fpagelinkCmd = {
		canUndo: false,
		exec: function(editor) {

			// show page select dialog
			var page_select_dialog = new Fiber.PageSelectDialog();

			page_select_dialog.action_click = function() {
				var selected_page_path = this.uiDialog.find('a.ui-state-active').attr('href');

				// delete any existing links on the selected text
				editor.document.$.execCommand('unlink', false, null);

				// create a new link
				editor.focus();
				var selection = editor.getSelection(); // need to do this to 'initialize'
				var style = new CKEDITOR.style({
					element: 'a',
					attributes: {
						'href': selected_page_path
					}
				});
				style.type = CKEDITOR.STYLE_INLINE;
				style.apply(editor.document);

				this.destroy();
			};
		}
	};

	// register plugin 'fpagelink'
	CKEDITOR.plugins.add('fpagelink', {
		init: function(editor) {
			editor.addCommand('fpagelink', fpagelinkCmd);
			editor.ui.addButton('fPageLink', {
				label: gettext('Link to a Page in This Site'),
				command: 'fpagelink',
				icon: STATIC_URL + 'fiber/images/ckeditor/icon-pagelink.png'
			});
		}
	});

	// fFileLink
	var ffilelinkCmd = {
		canUndo: false,
		exec: function(editor) {

			// show file select dialog
			var file_select_dialog = new Fiber.FileSelectDialog();

			file_select_dialog.action_click = function() {
				var selected_file_path = $(this.uiDialog.find('tr.ui-state-highlight td')[0]).text();

				// delete any existing links on the selected text
				editor.document.$.execCommand('unlink', false, null);

				// create a new link
				editor.focus();
				var selection = editor.getSelection();
				var style = new CKEDITOR.style({
					element: 'a',
					attributes: {
						'href': selected_file_path
					}
				});
				style.type = CKEDITOR.STYLE_INLINE;
				style.apply(editor.document);

				this.destroy();
			};
		}
	};

	// register plugin 'ffilelink'
	CKEDITOR.plugins.add('ffilelink', {
		init: function(editor) {
			editor.addCommand('ffilelink', ffilelinkCmd);
			editor.ui.addButton('fFileLink', {
				label: gettext('Link to a File in This Site'),
				command: 'ffilelink',
				icon: STATIC_URL + 'fiber/images/ckeditor/icon-filelink.png'
			});
		}
	});

	// fImageLink
	var fimagelinkCmd = {
		canUndo: false,
		exec: function(editor) {

			// show image select dialog
			var image_select_dialog = new Fiber.ImageSelectDialog();

			image_select_dialog.action_click = function() {
				var selected_image_path = $(this.uiDialog.find('tr.ui-state-highlight td')[0]).text();

				// delete any existing links on the selected text
				editor.document.$.execCommand('unlink', false, null);

				// create a new link
				editor.focus();
				var selection = editor.getSelection();
				var style = new CKEDITOR.style({
					element: 'a',
					attributes: {
						'href': selected_image_path
					}
				});
				style.type = CKEDITOR.STYLE_INLINE;
				style.apply(editor.document);

				this.destroy();
			};
		}
	};

	// register plugin 'fimagelink'
	CKEDITOR.plugins.add('fimagelink', {
		init: function(editor) {
			editor.addCommand('fimagelink', fimagelinkCmd);
			editor.ui.addButton('fImageLink', {
				label: gettext('Link to an Image in This Site'),
				command: 'fimagelink',
				icon: STATIC_URL + 'fiber/images/ckeditor/icon-imagelink.png'
			});
		}
	});

	// fCustomLink
	var fcustomlinkCmd = {
		canUndo: false,
		exec: function(editor) {

			// prompt for custom link - TODO: create custom jQuery UI dialog for this
			var custom_link = window.prompt(gettext('Please Enter a Link'), 'http://');

			// delete any existing links on the selected text
			editor.document.$.execCommand('unlink', false, null);

			// create a new link
			editor.focus();
			var selection = editor.getSelection();
			var style = new CKEDITOR.style({
				element: 'a',
				attributes: {
					'href': custom_link
				}
			});
			style.type = CKEDITOR.STYLE_INLINE;
			style.apply(editor.document);
		}
	};

	// register plugin 'fcustomlink'
	CKEDITOR.plugins.add('fcustomlink', {
		init: function(editor) {
			editor.addCommand('fcustomlink', fcustomlinkCmd);
			editor.ui.addButton('fCustomLink', {
				label: gettext('Custom Link'),
				command: 'fcustomlink',
				icon: STATIC_URL + 'fiber/images/ckeditor/icon-customlink.png'
			});
		}
	});

	// fUnlink
	var funlinkCmd = {
		canUndo: false,
		exec: function(editor) {
			// delete any existing links on the selected text
			editor.document.$.execCommand('unlink', false, null);
		}
	};

	// register plugin 'funlink'
	CKEDITOR.plugins.add('funlink', {
		init: function(editor) {
			editor.addCommand('funlink', funlinkCmd);
			editor.ui.addButton('fUnlink', {
				label: gettext('Unlink'),
				command: 'funlink',
				icon: STATIC_URL + 'fiber/images/ckeditor/icon-unlink.png'
			});
		}
	});

	// fImage
	var fimageCmd = {
		canUndo: false,
		exec: function(editor) {

			// show image select dialog
			var image_select_dialog = new Fiber.ImageSelectDialog();

			image_select_dialog.action_click = function() {
				var selected_image_path = $(this.uiDialog.find('tr.ui-state-highlight td')[0]).text();
				var selected_image_title = '';

				// create image element, and insert it
				var imageElement = CKEDITOR.dom.element.createFromHtml('<img src="' + selected_image_path + '" title="' + CKEDITOR.tools.htmlEncode(selected_image_title) + '" />');
				editor.insertElement(imageElement);

				this.destroy();
			};
		}
	};

	// register plugin 'fimage'
	CKEDITOR.plugins.add('fimage', {
		init: function(editor) {
			editor.addCommand('fimage', fimageCmd);
			editor.ui.addButton('fImage', {
				label: gettext('Image'),
				command: 'fimage',
				icon: STATIC_URL + 'fiber/images/ckeditor/icon-image.png'
			});
		}
	});

	// fTable
	var ftableCmd = {
		canUndo: false,
		exec: function(editor) {

			// insert a new table
			editor.insertHtml('<table border="0" cellspacing="0" cellpadding="0">' +
				'<thead>' +
					'<tr>' +
						'<th>column 1</th><th>column 2</th>' +
					'</tr>' +
				'</thead>' +
				'<tbody>' +
					'<tr>' +
						'<td></td><td></td>' +
					'</tr>' +
					'<tr>' +
						'<td></td><td></td>' +
					'</tr>' +
					'<tr>' +
						'<td></td><td></td>' +
					'</tr>' +
				'</tbody>' +
			'</table>');
		}
	};

	// register plugin 'ftable'
	CKEDITOR.plugins.add('ftable', {
		init: function(editor) {
			editor.addCommand('ftable', ftableCmd);
			editor.ui.addButton('fTable', {
				label: gettext('Table'),
				command: 'ftable',
				icon: STATIC_URL + 'fiber/images/ckeditor/icon-table.png'
			});
		}
	});
}

extend_CKEditor();

})(fiber_jQuery);
