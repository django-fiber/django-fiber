(function($) {

Fiber.enhance_textarea = function(textarea, auto_height) {

	if (window.CKEDITOR_CONFIG_STYLES_SET) {
		if (!CKEDITOR.stylesSet.get('config_styles_set')) {
			CKEDITOR.stylesSet.add('config_styles_set', window.CKEDITOR_CONFIG_STYLES_SET);
		}
	}

	window.CKEDITOR_CONFIG_TOOLBAR = window.CKEDITOR_CONFIG_TOOLBAR || [
		['Format'],
		window.CKEDITOR_CONFIG_STYLES_SET ? ['Styles'] : '-',
		['Bold','Italic'],
		['NumberedList','BulletedList','Outdent','Indent'],
		['fPageLink','fFileLink','fImageLink','fCustomLink','fUnlink'],
		['fImage','Table'],
		['PasteText','PasteFromWord','RemoveFormat'],
		['Maximize'],
		['Source']
	];

	if (auto_height) {
		CKEDITOR.config.height = window.innerHeight - (($('.ui-dialog').height() - $(textarea).height()) + 140);
	}

	CKEDITOR.replace(textarea, {
		skin: 'moono',
		language: LANGUAGE_CODE,
		extraPlugins: window.CKEDITOR_CONFIG_EXTRA_PLUGINS || 'fpagelink,ffilelink,fimagelink,fcustomlink,funlink,fimage,table,tabletools',
		removePlugins: window.CKEDITOR_CONFIG_REMOVE_PLUGINS || 'scayt,language,menubutton,forms,image,link',
		allowedContent: window.CKEDITOR_CONFIG_ALLOWED_CONTENT || false,
		extraAllowedContent: window.CKEDITOR_CONFIG_EXTRA_ALLOWED_CONTENT || 'a[*]{*}(*);img[*]{*}(*);iframe[*];object[*];param[*];embed[*]',
		toolbar: window.CKEDITOR_CONFIG_TOOLBAR,
		format_tags: window.CKEDITOR_CONFIG_FORMAT_TAGS || 'p;h2;h3;h4',
		stylesSet: window.CKEDITOR_CONFIG_STYLES_SET || null,
		toolbarCanCollapse: window.CKEDITOR_TOOLBAR_CAN_COLLAPSE || false,
		resize_maxWidth: window.CKEDITOR_CONFIG_MAX_WIDTH || 610,
		baseFloatZIndex: window.CKEDITOR_BASE_FLOAT_Z_INDEX || 1100
	});
};

Fiber.remove_textarea = function(textarea) {
	if (textarea.id in CKEDITOR.instances) {
		CKEDITOR.instances[textarea.id].destroy(false);
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
				// delete any existing links on the selected text
				editor.document.$.execCommand('unlink', false, null);

				// create a new link
				editor.focus();
				var selection = editor.getSelection(); // need to do this to 'initialize'
				var style = new CKEDITOR.style({
					element: 'a',
					attributes: {
						'href': page_select_dialog.selected_url
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
				command: 'fpagelink'
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
				var row = file_select_dialog.get_selected_row();
				var selected_file_path = row.file_url;

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
				command: 'ffilelink'
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
				var row = image_select_dialog.get_selected_row();
				var selected_image_path = row.image_url;

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
				command: 'fimagelink'
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
				command: 'fcustomlink'
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
				command: 'funlink'
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
				var selected_image_td = $(this.uiDialog.find('tr.selected td'));
				var selected_image_path = $(selected_image_td[0]).text();
				var selected_image_title = $(selected_image_td[0]).find('img').attr('title');

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
				command: 'fimage'
			});
		}
	});
}

extend_CKEditor();

})(fiber_jQuery);
