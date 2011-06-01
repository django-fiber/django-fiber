(function($) {

Fiber.enhance_combobox = function(select) {
	$(select).combobox();
};

Fiber.enhance_jsontextarea = function(textarea) {
	// hide the textarea
	$(textarea).hide();

	// put everything in a wrapper for styling
	var wpr_all = $('<div class="fiber-json-widget" />').insertBefore(textarea);

	// key-value will be put in a table
	var table = $('<table/>').appendTo(wpr_all);
	var thead = $('<thead><tr><th>'+gettext('Key')+'</th><th>'+gettext('Value')+'</th><th>'+gettext('Action')+'</th></tr></thead>').appendTo(table);
	var tbody = $('<tbody/>').appendTo(table);

	// latest row of table will become add-new key-value-pair action
	var tr_add = $('<tr/>').attr('class', 'add-row').appendTo(tbody);
	var td1_add = $('<td/>').appendTo(tr_add);
	var td2_add = $('<td/>').attr('class', 'key').appendTo(tr_add);
	var td3_add = $('<td/>').appendTo(tr_add);
	$('<label/>').attr('for', textarea.name+'-adder').text(gettext('Add new')).appendTo(td1_add);
	var adder = $('<select/>').attr('id', textarea.name+'-adder').appendTo(td2_add);
	$('<a/>').text(gettext('Add')).attr('class', textarea.name+'-add-btn add-btn').appendTo(td3_add);

	var current_json = $.parseJSON(textarea.value);
	var used_keys = [];

	for (var key in current_json) {
		if (current_json[key]) {
			add_field(key, current_json[key]);
		}
	}
	
	// add toggle bar
	var toggle_div = $('<div/>').appendTo(wpr_all);
	var toggle_textarea = $('<input type="checkbox"/>').attr('id', textarea.name+'-toggle').appendTo(toggle_div);
	$('<label/>').attr('for', textarea.name+'-toggle').text(gettext('Show raw JSON')).appendTo(toggle_div);

	// on click delete key-value-pair
	$('a.'+textarea.name+'-delete-btn').live('click', function(){
		old_key = $(this).parent('td').parent('tr').attr('key-data');
		delete current_json[old_key];
		removeByValue(used_keys,old_key);
		$('<option/>').attr('value', old_key).text(old_key).appendTo($('#'+textarea.name+'-adder'));
		$(this).parent('td').parent('tr').remove();
		generate_json();
	});

	// on blur update json-textarea
	$('.'+textarea.name+'-key-value-pair select, .'+textarea.name+'-key-value-pair input, .'+textarea.name+'-key-value-pair textarea, .'+textarea.name+'-key-value-pair .ui-autocomplete-input').live('blur', function(){
		if (current_json === null) {
			current_json = {};
		}
		current_json[$(this).parent('td').parent('tr').attr('key-data')] = $(this).val();
		generate_json();
	});

	// update add-new-key-value-pair selectbox with choices not already used
	for (key in schema[textarea.name]) {
		if ($.inArray(key, used_keys) == -1) {
			$('<option/>').attr('value', key).text(key).appendTo(adder);
		}
	}
	// make it a combobox after all values are set
	adder.combobox();

	// on click add key-value-pair
	$('a.'+textarea.name+'-add-btn').live('click', function(){
		new_key = $(this).parent('td').siblings('td.key').children('input').val();
		if (new_key === '') {
			alert(gettext('Key can not be empty'));
		} else {
			if ($.inArray(new_key, used_keys) != -1) {
				alert(gettext('Key already exists!'));
			} else {
				add_field(new_key, '');
				$(this).parent('td').siblings('td.key').children('input').val('');
				$('#'+textarea.name+'-adder option[value="'+new_key+'"]').remove();
				if (current_json === null) {
					current_json = {};
				}
				current_json[new_key] = $('#'+textarea.name+'-key-'+new_key).val();
				generate_json();
			}
		}
	});

	// toggle textarea
	toggle_textarea.click(function(){
		$(textarea).toggle();
	});

	function add_field(key, value) {
		used_keys.push(key);
		var row = $('<tr/>').attr('class', textarea.name+'-key-value-pair').attr('key-data', key).insertBefore(tr_add);
		var td1 = $('<td/>').appendTo(row);
		var td2 = $('<td/>').appendTo(row);
		var td3 = $('<td/>').appendTo(row);
		$('<label/>').attr('for', textarea.name+'-key-'+key).text(gettext(key)).appendTo(td1);

		// check if this key has a special description
		if (key in schema[textarea.name]) {
			if ('widget' in schema[textarea.name][key]) {
				if (schema[textarea.name][key].widget == 'select' || schema[textarea.name][key].widget == 'combobox') {
					// add a select widget
					var select_widget = $('<select/>').attr('id', textarea.name+'-key-'+key).appendTo(td2);
					if ('values' in schema[textarea.name][key]) {
						var select_values = schema[textarea.name][key].values;
						for (var select_value in select_values) {
							if (select_values[select_value]) {
								var option = $('<option/>').attr('value', select_values[select_value]).text(select_values[select_value]).appendTo(select_widget);
								// set current value as selected
								if (select_values[select_value] == value) {
									$(option).attr('selected', 'selected');
								}
							}
						}
					}

					if (schema[textarea.name][key].widget == 'combobox') {
						$(select_widget).combobox();
					}

				} else if (schema[textarea.name][key].widget == 'textarea') {
					// add a textarea widget
					$('<textarea/>').attr('id', textarea.name+'-key-'+key).attr('value', value).appendTo(td2);

				} else {
					// unknown widget, or textfield, hence default field
					add_default_field(key, value, td2);
				}
			} else {
				// no widget specification, hence default field
				add_default_field(key, value, td2);
			}

		} else {
			// custom key, hence default field
			add_default_field(key, value, td2);
		}

		$('<a/>').text(gettext('Delete')).attr('class', textarea.name+'-delete-btn deletelink').appendTo(td3);
	}

	function add_default_field(key, value, td2) {
		$('<input type="text"/>').attr('id', textarea.name+'-key-'+key).attr('value', value).appendTo(td2);
	}

	function generate_json() {
		$(textarea).val($.toJSON(current_json));
	}

	function removeByValue(arr, val) {
		for(var i=0; i<arr.length; i++) {
			if(arr[i] == val) {
				arr.splice(i, 1);
				break;
			}
		}
	}

};

Fiber.enhance_textarea = function(textarea) {
	// TODO: add Django-like behavior:
	// - fieldsets should be split into tabs
	// - collapsible areas should work, etc.

	CKEDITOR.replace(textarea, {
		language: LANGUAGE_CODE,
		extraPlugins: 'fpagelink,ffilelink,fimagelink,fcustomlink,funlink,fimage,ftable,tabletools',
		removePlugins: 'scayt,menubutton,forms,image,link',
		toolbar:
		[
			['Format'],
			['Bold','Italic'],
			['NumberedList','BulletedList','Outdent','Indent'],
			['fPageLink','fFileLink','fImageLink','fCustomLink','fUnlink'],
			['fImage','fTable'],
			['PasteText','PasteFromWord','RemoveFormat'],
			['Maximize'],
			['Source']
		],
		format_tags: 'p;h2;h3;h4',
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
				var style = new CKEDITOR.style({
					element: 'a',
					attributes: {
						'href': selected_page_path
					}
				});
				style.type = CKEDITOR.STYLE_INLINE;
				style.apply(editor);

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
				var style = new CKEDITOR.style({
					element: 'a',
					attributes: {
						'href': selected_file_path
					}
				});
				style.type = CKEDITOR.STYLE_INLINE;
				style.apply(editor);

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
				var style = new CKEDITOR.style({
					element: 'a',
					attributes: {
						'href': selected_image_path
					}
				});
				style.type = CKEDITOR.STYLE_INLINE;
				style.apply(editor);

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
			var style = new CKEDITOR.style({
				element: 'a',
				attributes: {
					'href': custom_link
				}
			});
			style.type = CKEDITOR.STYLE_INLINE;
			style.apply(editor);
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
				var selected_image_title = 'title';

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
