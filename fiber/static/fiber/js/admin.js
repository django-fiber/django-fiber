var fiber_jQuery = $.noConflict(true);

// fiber namespace
var Fiber = {};

Fiber.enhance_textarea = function(textarea) {};
Fiber.remove_textarea = function(textarea) {};

(function($) { // start of jQuery noConflict mode

// some plugins use jQuery() instead of $()
jQuery = $;

var busyIndicator = {
	show: function() {
		$('#df-wpr-busy').show();
	},
	hide: function() {
		$('#df-wpr-busy').hide();
	}
};

Fiber.enhance_combobox = function(select) {
	$(select).combobox();
};

Fiber.enhance_content_template_select = function(select) {
	var template_name = $(select);
	var fieldset_of_template_name = $('select#id_template_name').parents('fieldset')[0];
	var hidden_template_name = $('<input type="hidden" name="template_name" id="id_template_name_hidden">');

	hidden_template_name.val(template_name.val());
	$(fieldset_of_template_name).append(hidden_template_name);
	$(fieldset_of_template_name).hide();
	$('.ui-dialog-buttonset').append(template_name);

	template_name.change(function() {
		$('#id_template_name_hidden').val($(this).val());
	});
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

// abstract class for a basic admin dialog
var AdminDialog = Class.extend({

	// default options
	defaults: {
		url: null,
		width: 744,
		height: 'auto',
		start_width: 744,
		start_height: 480
	},

	// constructor
	init: function(options) {
		this.options = $.extend({}, this.defaults, options); // TODO: get dialog dimensions and behavior from options
		this.create_dialog();
		this.init_dialog();
		this.open();
	},

	// create a basic dialog, use only as example
	create_dialog: function() {
		this.uiDialog = $(document.createElement('div')).dialog({
			autoOpen: false,
			modal: true,
			resizable: false,
			width: this.options.start_width,
			height: this.options.start_height,
			position: ['center', 40]
		});

		this.uiDialog.dialog('option', 'title', gettext('Action')); // TODO: dynamically fill in action

		this.uiDialog.dialog('option', 'buttons', {
			'Action': {
				text: 'Action', // TODO: dynamically fill in action
				click: $.proxy(function() {
					this.action_click();
				}, this)
			},
			'Cancel': {
				text: gettext('Cancel'),
				click: $.proxy(function() {
					this.cancel_click();
				}, this)
			}
		});

		this.uiDialog.dialog('option', 'close', $.proxy(this.close, this));
	},

	// initialize the dialog
	init_dialog: function() {},

	redraw: function() {
		this.uiDialog.dialog('option', 'width', this.options.width);
		this.uiDialog.dialog('option', 'height', this.options.height);
		this.uiDialog.dialog('option', 'position', ['center', 40]);
	},

	cancel_click: function() {
		this.close();
	},

	// customize open dialog behavior
	open: function() {
		this.uiDialog.dialog('open');
		this.redraw();
	},

	// customize close dialog behavior
	close: function() {
		this.uiDialog.dialog('option', 'close', null); // prevent recursive calls to this function
		this.uiDialog.dialog('close');
	},

	// customize destroy dialog behavior
	destroy: function() {
		this.uiDialog.dialog('destroy');
	}
});

// abstract class for a basic admin form dialog
var AdminFormDialog = AdminDialog.extend({

	// create admin form dialog
	create_dialog: function() {
		this._super();
		this.uiDialog.dialog('option', 'close', $.proxy(this.destroy, this));
	},

	// initialize the admin form
	init_dialog: function() {
		this.admin_form = new AdminForm({
			url: this.options.url
		});
		this.admin_form.admin_form_load_success = $.proxy(function() {
			this.append_form();
			this.redraw();
		}, this);
		this.admin_form.load();
	},

	// append form to the dialog
	append_form: function() {
		this.uiDialog.append(this.admin_form.form);
	},

	// customize destroy dialog behavior
	destroy: function() {
		this.admin_form.destroy();
		this._super();
	}
});


// abstract class for a basic admin REST dialog
var AdminRESTDialog = AdminDialog.extend({

	// initialize the REST call
	init_dialog: function() {
		busyIndicator.show();

		$.ajax({
			url: this.options.url,
			context: this,
			success: function(data) {
				if (this.init_dialog_success) {
					this.init_dialog_success(data);
				}
			}
		});
	}
});


// abstract class for a basic df admin form
var AdminForm = Class.extend({

	defaults: {},

	// constructor
	init: function(options) {
		this.options = $.extend({}, options, this.defaults);
	},

	// load form from HTML, set styling and interaction
	load: function() {
		busyIndicator.show();

		$.ajax({
			url: this.options.url,
			context: this,
			success: function(data) {
				this.get_form_from_HTML(data);
				this.set_form_action();
				this.set_styling();
				if (this.admin_form_load_success) {
					this.admin_form_load_success();
				}
				this.set_interaction();

				busyIndicator.hide();
			}
		});
	},

	// get the form element from the HTML that is returned by the XHR
	get_form_from_HTML: function(html) {
		var forms = $(document.createElement('div')).html(this.strip_HTML(html)).find('#content-main form[id$=_form]');
		if (forms.length == 1) {
			this.form = $(forms[0]);

			this.form.append('<input type="hidden" name="_continue" />'); // this prevents the redirect to the changelist
		}
	},

	// helper function for cleaning HTML
	strip_HTML: function(html) {
		return html
		.replace(/\n/g, '\uffff')
		.replace(/<script(.*?)<\/script>/gm, '')
		.replace(/<link(.*?)>/gm, '')
		.replace(/<style(.*?)<\/style>/gm, '')
		.replace(/\sstyle=['"](.*?)['"]/gm, '')
		.replace(/\uffff/g, '\n');
	},

	// customize form action
	set_form_action: function(url) {
		if (url) {
			this.form.attr('action', url);
		} else if (this.options.url) {
			this.form.attr('action', this.options.url);
		}
	},

	// placeholder function for modifying styling of the form
	set_styling: function() {},

	// placeholder function for modifying behavior of the form
	set_interaction: function() {},

	destroy: function() {
		this.form.remove();
	}
});


var LoginFormDialog = AdminFormDialog.extend({

	defaults: {
		url: BACKEND_BASE_URL,
		width: 250,
		height: 'auto',
		start_width: 250
	},

	// initialize the login form
	init_dialog: function() {
		this.admin_form = new LoginForm({
			url: this.options.url
		});
		this.admin_form.admin_form_load_success = $.proxy(function() {
			this.append_form();
			this.redraw();
		}, this);
		this.admin_form.load();

		this.uiDialog.dialog('option', 'title', gettext('Fiber Login')); // TODO: dynamically fill in action
		// TODO: is this the correct place for this?
		var action_button = this.uiDialog.parent().find(':button:contains("Action")');
		action_button.find('.ui-button-text').text(gettext('Login')).attr('id', 'login_button');

	},

	action_click: function() {
		this.admin_form.form.ajaxSubmit({
			cache: false,
			url: FIBER_LOGIN_URL,
			type: 'POST',
			context: this,
			datatype: 'json',
			success: function(data) {
				if (data.status == 'success') {
					this.after_action_success();
				} else {
					var errornote = this.admin_form.form.find('p.errornote');
					// check if errornote already exists
					if (errornote.length === 0) {
						errornote = $('<p class="errornote"></p>');
						this.admin_form.form.prepend(errornote);
					}
					errornote.text(data.message);
				}
			}
		});
	},

	after_action_success: function() {
		// when successful, reload the page
		reloadPage();
	},

	cancel_click: function() {
		this.destroy();
	}
});


var LoginForm = AdminForm.extend({

	set_styling: function() {
		// remove submit button(s) and `delete` link
		this.form.find('div.submit-row').remove();

		// strip ':' from the end of labels
		this.form.find('label').each(function() {
			$(this).text($(this).text().replace(':', ''));
		});
	},

	// get the form element from the HTML that is returned by the XHR
	get_form_from_HTML: function(html) {
		var forms = $(document.createElement('div')).html(this.strip_HTML(html)).find('#content-main form[id$=-form]');

		if (forms.length == 1) {
			this.form = $(forms[0]);
		}
	},

	set_interaction: function() {
		this.form.find('#id_username').focus();
		this.form.find('#id_password').keypress(function (e) {
			if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) {
				$('#login_button').click();
				return false;
			} else {
				return true;
			}
		});
	},

	destroy: function() {
		this.form.remove();
	}
});


var ChangeFormDialog = AdminFormDialog.extend({

	// initialize the change form
	init_dialog: function() {
		this.admin_form = new ChangeForm({
			url: this.options.url
		});
		this.admin_form.admin_form_load_success = $.proxy(function() {
			this.append_form();
			this.redraw();
		}, this);
		this.admin_form.load();

		// TODO: is this the correct place for this?
		var action_button = this.uiDialog.parent().find(':button:contains("Action")');
		action_button.find('.ui-button-text').text(gettext('Save'));
	},

	action_click: function() {
		busyIndicator.show();

		this.admin_form.form.ajaxSubmit({
			cache: false,
			context: this,
			success: function(responseText, statusText, xhr, $form) {
				var response_change_form = new ChangeForm({
					url: this.admin_form.options.url
				});

				response_change_form.get_form_from_HTML(responseText);

				if (response_change_form.form.find('p.errornote').length) {
					this.admin_form.destroy();
					this.admin_form = response_change_form;

					this.admin_form.set_form_action();
					this.admin_form.set_styling();
					this.append_form();
					this.admin_form.set_interaction();
					busyIndicator.hide();
				} else {
					this.after_action_success(responseText, statusText, xhr, $form);
				}
			}
		});
	},

	after_action_success: function(responseText, statusText, xhr, $form) {
		this.admin_form.destroy();
		this.close();
		reloadPage();
	},

	cancel_click: function() {
		this.destroy();
	}
});

function enhance_textareas(container, auto_height) {
	container.find('textarea.fiber-editor').each(function() {
		Fiber.enhance_textarea(this, auto_height);
	});
}

function enhance_comboboxes(container) {
	container.find('select.fiber-combobox').each(function() {
		Fiber.enhance_combobox(this);
	});
}

function enhance_jsontextareas(container) {
	container.find('textarea.fiber-jsonwidget').each(function() {
		Fiber.enhance_jsontextarea(this);
	});
}

function enhance_content_template_select(container) {
	container.find('select#id_template_name').each(function() {
		Fiber.enhance_content_template_select(this);
	});
}

var ChangeForm = AdminForm.extend({

	set_styling: function() {
		// remove submit button(s) and `delete` link
		this.form.find('div.submit-row').remove();

		// strip ':' from the end of labels
		this.form.find('label').each(function() {
			$(this).text($(this).text().replace(':', ''));
		});
	},

	set_interaction: function() {
		// TODO: add Django-like behavior:
		// - fieldsets should be split into tabs
		// - collapsible areas should work, etc.
		enhance_textareas(this.form, true);
		enhance_comboboxes(this.form);
		enhance_jsontextareas(this.form);
		enhance_content_template_select(this.form);
	},

	destroy: function() {
		this.form.find('textarea.fiber-editor').each(function() {
			Fiber.remove_textarea(this);
		});

		this.form.remove();
	}
});


var BaseFileSelectDialog = AdminRESTDialog.extend({

	open: function() {
		this._super();
		// Create the upload button after displaying the dialog
		this.create_upload_button();
	},

	get_upload_path: function() {
		// override this
	},

	refresh_grid: function() {
		// override this
	},

	create_upload_button: function() {
		var button_pane = this.uiDialog.parent().find('.ui-dialog-buttonpane');

		var upload_button_pane = $('<div/>').prependTo(button_pane)
			.attr({
				'id': 'upload-buttonpane'
			});

		var upload_button = $('<button type="button">' + gettext('Upload a new file') + '</button>')
			.appendTo(upload_button_pane)
			.attr({
				'class': 'upload',
				'id': 'upload-file-button'
			})
			.button({
				icons: {
					primary: 'ui-icon-circle-plus'
				}
			})
			.css({
				'margin-top': 0,
				'margin-bottom': 0,
				'margin-right': 0
			});

		// Valums file uploader
		var uploader = new qq.FileUploaderBasic({
			element: upload_button_pane[0],
			button: upload_button_pane[0], // connecting directly to the jQUery UI upload_button doesn't work
			action: this.get_upload_path(),
			params: {
				'sessionid': $.cookie('sessionid')
			},
			onComplete: $.proxy(function(id, fileName, responseJSON) {
				this.refresh_grid();
			}, this),
			debug: false
		});

		// reset button behavior
		upload_button_pane.css({
			'position': 'absolute',
			'margin-top': 8,
			'margin-bottom': 8
		});
	}
});


Fiber.ImageSelectDialog = BaseFileSelectDialog.extend({

	defaults: {
		url: '/api/v1/images.jqgrid-json',
		width: 520,
		height: 'auto',
		start_width: 480,
		start_height: 'auto'
	},

	// override default dialog window
	init_dialog: function() {
		// don't call _super, just call init_dialog_success at the end
		this.uiDialog.dialog('option', 'zIndex', 1200); // set z-index here, because it can't set by _super

		// enhance action button
		var action_button = this.uiDialog.parent().find(':button:contains("Action")');
		action_button.attr('id', 'action-button');

		action_button.find('.ui-button-text').text(gettext('Select'));

		action_button.attr('disabled', 'disabled');
		action_button.addClass('ui-button-disabled ui-state-disabled');

		this.uiDialog.dialog('option', 'title', gettext('Select an image'));

		this.init_dialog_success();
	},

	init_dialog_success: function(data) {

		var action_button = this.uiDialog.parent().find('#action-button');
		var filename = '';

		this.image_select_grid = $(document.createElement('table')).attr('id', 'ui-image-select-grid'); // the id attribute is necessary for jqGrid
		this.image_select_grid_pager = $(document.createElement('div')).attr('id', 'ui-image-select-grid-pager');
		this.image_select_filter = $(document.createElement('div')).attr('id', 'ui-image-select-filter');
		this.image_select_filter.append($(document.createElement('label')).attr({ id: 'ui-image-select-filter-label'}).text(gettext('Filter by filename')));
		this.image_select_filter.append($(document.createElement('input')).attr({ id: 'ui-image-select-filter-input', name: 'filter', value: '', type: 'text' }));
		this.uiDialog.append(this.image_select_filter);
		this.uiDialog.append(this.image_select_grid);
		this.uiDialog.append(this.image_select_grid_pager);

		$('#ui-image-select-filter-input').keyup(function() {
			var new_filename = $('#ui-image-select-filter-input').val();
			if (filename != new_filename) {
				filename = new_filename;
				$("#ui-image-select-grid").jqGrid('setGridParam',{ postData:{ filename: $('#ui-image-select-filter-input').val() }, search: true }).trigger("reloadGrid");
			}
		});

		var thumbnail_formatter = function(cellvalue, options, rowObject) {
			return '<img src="' + cellvalue + '" title="' + rowObject[2] + '" />';
		};

		this.image_select_grid.jqGrid({
			url: this.options.url,
			datatype: 'json',
			colNames: ['url', gettext('Image'), gettext('Filename'), gettext('Size'), gettext('Updated')],
			colModel: [
				{ name: 'url', index: 'url', hidden: true },
				{ name: 'image', index: 'image', width: 120, resizable: false, sortable: false, formatter: thumbnail_formatter },
				{ name: 'filename', index: 'filename', width: 160, resizable: false },
				{ name: 'size', index: 'size', width: 80, resizable: false },
				{ name: 'updated', index: 'updated', width: 160, resizable: false }
			],
			rowNum: 50,
			pager: '#ui-image-select-grid-pager',
			shrinkToFit: false,
			width: 520,
			height: 300,
			sortname: 'updated',
			sortorder: 'desc',
			onSelectRow: function(id) {
				action_button.attr('disabled', '');
				action_button.removeClass('ui-button-disabled ui-state-disabled');
			},
			gridComplete: function() {
				var num_pages = $("#ui-image-select-grid").getGridParam('lastpage');
				if (num_pages > 1) {
					$('#ui-image-select-grid-pager').show();
				} else {
					$("#ui-image-select-grid-pager").hide();
				}
			}
		});
	},

	get_upload_path: function() {
		return '/api/v1/images/';
	},

	refresh_grid: function() {
		this.image_select_grid.trigger('reloadGrid');
	},

	close: function() {
		this.image_select_grid.GridDestroy();
		this._super();
	},

	destroy: function() {
		this.image_select_grid.GridDestroy();
		this._super();
	}
});


Fiber.FileSelectDialog = BaseFileSelectDialog.extend({

	defaults: {
		url: '/api/v1/files.jqgrid-json',
		width: 520,
		height: 'auto',
		start_width: 480,
		start_height: 'auto'
	},

	// override default dialog window
	init_dialog: function() {
		// don't call _super, just call init_dialog_success at the end
		this.uiDialog.dialog('option', 'zIndex', 1200); // set z-index here, because it can't set by _super

		// enhance action button
		var action_button = this.uiDialog.parent().find(':button:contains("Action")');
		action_button.attr('id', 'action-button');

		action_button.find('.ui-button-text').text(gettext('Select'));

		action_button.attr('disabled', 'disabled');
		action_button.addClass('ui-button-disabled ui-state-disabled');

		this.uiDialog.dialog('option', 'title', gettext('Select a file'));

		this.init_dialog_success();
	},

	init_dialog_success: function(data) {
		var action_button = this.uiDialog.parent().find('#action-button');
		var filename = '';

		this.file_select_grid = $(document.createElement('table')).attr('id', 'ui-file-select-grid'); // the id attribute is necessary for jqGrid
		this.file_select_grid_pager = $(document.createElement('div')).attr('id', 'ui-file-select-grid-pager');
		this.file_select_filter = $(document.createElement('div')).attr('id', 'ui-file-select-filter');
		this.file_select_filter.append($(document.createElement('label')).attr({ id: 'ui-file-select-filter-label'}).text(gettext('Filter by filename')));
		this.file_select_filter.append($(document.createElement('input')).attr({ id: 'ui-file-select-filter-input', name: 'filter', value: '', type: 'text' }));
		this.uiDialog.append(this.file_select_filter);
		this.uiDialog.append(this.file_select_grid);
		this.uiDialog.append(this.file_select_grid_pager);

		$('#ui-file-select-filter-input').keyup(function() {
			var new_filename = $('#ui-file-select-filter-input').val();
			if (filename != new_filename) {
				filename = new_filename;
				$("#ui-file-select-grid").jqGrid('setGridParam',{ postData:{ filename: $('#ui-file-select-filter-input').val() }, search: true }).trigger('reloadGrid');
			}
		});
		this.file_select_grid.jqGrid({
			url: this.options.url,
			datatype: 'json',
			data: { 'filename': 'praxis'},
			colNames: ['url', gettext('Filename'), gettext('Updated')],
			colModel: [
				{ name: 'url', index: 'url', hidden: true },
				{ name: 'filename', index: 'filename', width: 360, resizable: false },
				{ name: 'updated', index: 'updated', width: 160, resizable: false }
			],
			rowNum: 50,
			pager: '#ui-file-select-grid-pager',
			shrinkToFit: false,
			width: 520,
			height: 300,
			sortname: 'updated',
			sortorder: 'desc',
			onSelectRow: function(id) {
				action_button.attr('disabled', '');
				action_button.removeClass('ui-button-disabled ui-state-disabled');
			},
			gridComplete: function() {
				var num_pages = $("#ui-file-select-grid").getGridParam('lastpage');
				if (num_pages > 1) {
					$('#ui-file-select-grid-pager').show();
				} else {
					$("#ui-file-select-grid-pager").hide();
				}
			}
		});
	},

	get_upload_path: function() {
		return '/api/v1/files/';
	},

	refresh_grid: function() {
		this.file_select_grid.trigger('reloadGrid');
	},

	action_click: function() {
		// do something
	},

	cancel_click: function() {
		this.destroy();
	},

	close: function() {
		this.file_select_grid.GridDestroy();
		this._super();
	},

	destroy: function() {
		this.file_select_grid.GridDestroy();
		this._super();
	}
});


Fiber.PageSelectDialog = AdminRESTDialog.extend({

	defaults: {
		url: '/api/v1/pages.json',
		width: 480,
		height: 320,
		start_width: 480,
		start_height: 320
	},

	// override default dialog window
	init_dialog: function() {
		// don't call _super, just call init_dialog_success at the end
		this.uiDialog.dialog('option', 'zIndex', 1200); // set z-index here, because it can't set by _super

		// enhance action button
		var action_button = this.uiDialog.parent().find(':button:contains("Action")');
		action_button.attr('id', 'action-button');

		action_button.find('.ui-button-text').text(gettext('Select'));

		action_button.attr('disabled', 'disabled');
		action_button.addClass('ui-button-disabled ui-state-disabled');

		this.uiDialog.dialog('option', 'title', gettext('Select a page'));

		this.init_dialog_success();
	},

	init_dialog_success: function(data) {
		this.selected_url = null;

		var action_button = this.uiDialog.parent().find('#action-button');

		var page_tree_div = $(document.createElement('div'));
		this.uiDialog.append(page_tree_div);

		function handleClick(e) {
			if (! e.node.url) {
				return false;
			}
			else {
				this.selected_url = e.node.url;

				action_button.attr('disabled', '');
				action_button.removeClass('ui-button-disabled ui-state-disabled');

				return true;
			}
		}

		function createLi(node, $li) {
			if (node.change_url) {
				$li.find('.title').before('<span class="icon"></span>');
				$li.find('div').addClass('page');
			}
		}

		function handle_load_data(data) {
			page_tree_div.tree({
				data: data,
				selectable: true,
				autoOpen: 1,
				onCreateLi: $.proxy(createLi, this)
			});
			page_tree_div.bind('tree.click',$.proxy(handleClick, this));
		}

		$.ajax({
			url: '/admin/fiber/pages.json',
			success: $.proxy(handle_load_data, this),
			cache: false,
			dataType: 'json'
		});
	},

	action_click: function() {
		// do something
	},

	cancel_click: function() {
		this.destroy();
	}
});


var ChangePageFormDialog = ChangeFormDialog.extend({

	defaults: {
		width: 325,
		height: 'auto',
		start_width: 325
	},

	init_dialog: function() {
		var extra_field;
		this._super();

		this.admin_form.options.before_page_id = this.options.before_page_id;
		this.admin_form.options.below_page_id = this.options.below_page_id;
		this.admin_form.set_interaction = function() {
			if (this.options.before_page_id) {
				extra_field = $('<input type="hidden" name="before_page_id" />');
				extra_field.val(this.options.before_page_id);
				this.form.append(extra_field);
			}

			if (this.options.below_page_id) {
				extra_field = $('<input type="hidden" name="below_page_id" />');
				extra_field.val(this.options.below_page_id);
				this.form.append(extra_field);
			}

			var $url_field = $('#id_url');
			var $title_field = $('#id_title');

			// remove autocompletion from title field
			$title_field.attr('autocomplete', 'off');

			// automatically slugify the title field when the url field is initially empty
			if (!$url_field.val()) {
				$title_field.slugify($url_field);
			}

			// automatically (re)start slugifying the title field when the url field is emptied
			$url_field.change(function() {
				if (!$url_field.val()) {
					$title_field.slugify($url_field);
				}
			});
		};
	}
});


var AddButton = Class.extend({ // TODO: subclass to AddPageButton / AddContentItemButton / AddOtherButton

	// default options
	defaults: {},

	init: function(fiber_item, options) {
		this.fiber_item = fiber_item;
		this.mouse_is_over = null;

		this.admin_layer = $('#df-layer');

		this.set_options(options);
		this.set_appearance();
		this.attach_events();
	},

	set_options: function(options) {
		var params = this.fiber_item.element_data;
		this.options = $.extend({}, this.defaults, params, options);
	},

	set_appearance: function() {
		this.add_button = $('<a href="#" class="ui-button ui-widget ui-state-default add"></a>'); // TODO: rename to this.$element?
		this.admin_layer.append(this.add_button);
	},

	set_position: function() {
		this.add_button.position(this.fiber_item.button_position());
	},

	on_click: function() {
		// TODO: split this into subclasses
		if (this.fiber_item.element_data.type == 'page') {
			params = {
				url: this.options.add_url,
				before_page_id: this.options.before_page_id,
				below_page_id: this.options.parent_id // TODO: rename below_page_id to parent_id?
			};

			new ChangePageFormDialog(params); // TODO: create AddPageFormDialog?
		} else if (this.fiber_item.element_data.type == 'content_item') {
			params = {
				url: this.options.add_url,
				block_name: this.options.block_name,
				page_id: this.options.page_id,
				before_page_content_item_id: this.options.before_page_content_item_id
			};

			new AddContentItemFormDialog(params);
		}

		adminPage.hide_admin_elements();
		return false;
	},

	attach_events: function() {
		this.add_button.hover(
			$.proxy(this.on_mouseenter, this),
			$.proxy(this.on_mouseleave, this)
		);

		this.add_button.click(
			$.proxy(this.on_click, this)
		);
	},

	on_mouseenter: function(e) {
		e.stopPropagation();
		this.fiber_item.$element.trigger('mouseenter');
		this.add_button.addClass('ui-state-hover');
	},

	on_mouseleave: function(e) {
		e.stopPropagation();
		this.fiber_item.$element.trigger('mouseleave');
		this.add_button.removeClass('ui-state-hover');
	},

	show: function() {
		if ($.browser.msie && parseInt($.browser.version, 10) == 7) {
			this.add_button.addClass('ui-button'); // only necessary for IE7
		}
		this.add_button.show();
		this.set_position();
	},

	hide: function() {
		if ($.browser.msie && parseInt($.browser.version, 10) == 7) {
			this.add_button.removeClass('ui-button'); // only necessary for IE7
		}
		this.add_button.hide();
	}
});


var DroppableArea = Class.extend({

	// default options
	defaults: {},

	init: function(fiber_item, options) {
		this.fiber_item = fiber_item;

		this.admin_layer = $('#df-layer');

		this.set_options(options);
		this.set_appearance();
		this.make_droppable();
	},

	set_options: function(options) {
		var params = $.parseJSON(this.fiber_item.$element.dataset('fiber-data'));
		this.options = $.extend({}, this.defaults, params, options);
	},

	set_appearance: function() {
		this.droppable_area = $('<div class="ui-droppable"></div>');

		this.admin_layer.append(this.droppable_area);
	},

	make_droppable: function() {
		this.droppable_area.droppable({
			scope: 'content_item',
			drop: $.proxy(function(event, ui) {
				var fiber_item_data = $.parseJSON($(ui.draggable).dataset('fiber-data'));
				if (fiber_item_data.type == 'content_item') {
					if (fiber_item_data.block_name) {
						// move content item
						this.move_content_item(fiber_item_data);
					}
					else {
						// drag content from menu
						this.add_content_item(fiber_item_data.id);
					}
				}
			}, this),
			tolerance: 'pointer',
			hoverClass: 'ui-state-hover',
			activeClass: 'ui-state-active'
		});
	},

	add_content_item: function(content_item_id) { // TODO: move to utils? (DRY)
		// perform an AJAX call to add the added object to the current page,
		// optionally placed before the beforePageContentItem
		var data = {
			content_item_id: content_item_id,
			page_id: this.options.page_id,
			block_name: this.options.block_name
		};

		if (this.options.before_page_content_item_id) {
			data.before_page_content_item_id = this.options.before_page_content_item_id;
		}

		busyIndicator.show();

		$.ajax({
			url: '/api/v1/page_content_items/',
			type: 'POST',
			data: data,
			success: function(data) {
				// when successful, reload the page
				reloadPage();
			}
		});
	},

	move_content_item: function(fiber_item_data) {
		busyIndicator.show();

		$.ajax({
			url: '/api/v1/page_content_item/' + fiber_item_data.page_content_item_id + '/',
			type: 'PUT',
			data: {
				before_page_content_item_id: this.fiber_item.element_data.page_content_item_id,
				action: 'move',
				block_name: this.fiber_item.element_data.block_name
			},
			success: function() {
				reloadPage();
			}
		});
	},

	set_position: function() {
		this.droppable_area.width(this.fiber_item.$element.outerWidth());
		this.droppable_area.position(this.fiber_item.droppable_position());
	},

	show: function() {
		this.droppable_area.show();
		this.set_position();
	},

	hide: function() {
		this.droppable_area.hide();
	}
});


var ChangeContentItemFormDialog = ChangeFormDialog.extend({

	init_dialog: function() {
		this._super();

		this.admin_form.options.page_id = this.options.page_id;
		this.admin_form.options.block_name = this.options.block_name;
		this.admin_form.options.before_page_content_item_id = this.options.before_page_content_item_id;
	}
});


var AddContentItemFormDialog = ChangeContentItemFormDialog.extend({

	init_dialog: function() {
		this._super();

		this.after_action_success = $.proxy(function(responseText, statusText, xhr, $form) {
			// find id of added content item
			var added_content_item_id = xhr.responseXML.URL.replace(/\/$/,'').split('/').pop();

			if (added_content_item_id) {
				this.add_content_item(added_content_item_id);
			}
		}, this);
	},

	add_content_item: function(content_item_id) { // TODO: move to utils? (DRY)
		// perform an AJAX call to add the added object to the current page,
		// placed before the beforeElement
		var data = {
			content_item_id: content_item_id,
			page_id: this.options.page_id,
			block_name: this.options.block_name
		};

		if (this.options.before_page_content_item_id) {
			data.before_page_content_item_id = this.options.before_page_content_item_id;
		}

		busyIndicator.show();

		$.ajax({
			url: '/api/v1/page_content_items/',
			type: 'POST',
			data: data,
			success: function(data) {
				// when successful, reload the page
				reloadPage();
			}
		});
	}
});


var adminPage = {
	all_fiber_items: [],

	create_fiber_item: function($fiber_element) {
		// create new FiberItem
		var fiber_item = new FiberItem($fiber_element);
		this.all_fiber_items.push(fiber_item);

		// find closest parent, and see if it is already a FiberItem
		var closest_parent = $fiber_element.parent().closest('[data-fiber-data]:not(body)');
		if (closest_parent.length) {
			var parent = null;
			$.each(this.all_fiber_items, function(i, all_fiber_item) {
				if (all_fiber_item.$element[0] == closest_parent[0]) {
					parent = all_fiber_item;
					return false;
				}
			});
			if (!parent) {
				parent = this.create_fiber_item(closest_parent);
			}
			parent.add_child(fiber_item);
			fiber_item.parent = parent;
		}
		return fiber_item;
	},

	get_fiber_item_containers: function() {
		var fiber_item_containers = [];
		$.each(this.all_fiber_items, function(i, fiber_item) {
			if (!fiber_item.parent) {
				fiber_item_containers.push(fiber_item);
			}
		});

		return fiber_item_containers;
	},

	init_admin_elements: function() {
		var fiber_elements = this.get_fiber_elements();

		// create nested structure of Fiber items
		$.each(this.get_fiber_elements(), $.proxy(function(i, fiber_element) {
			this.create_fiber_item($(fiber_element));
		}, this));

		$.each(this.all_fiber_items, function(i, fiber_item) {
			fiber_item.post_init();
		});
	},

	hide_admin_elements: function() {
		$.each(this.get_fiber_item_containers(), function(i, fiber_item_container) {
			fiber_item_container.hide_admin_elements();
		});
	},

	show_droppables: function() {
		$.each(this.get_fiber_item_containers(), function(i, fiber_item_container) {
			fiber_item_container.show_droppables();
		});
	},

	hide_droppables: function() {
		$.each(this.get_fiber_item_containers(), function(i, fiber_item_container) {
			fiber_item_container.hide_droppables();
		});
	},

	// get fiber elements in page (excluding admin divs).
	get_fiber_elements: function() {
		var page_divs = $(document.body).children(':visible').not('#df-wpr-layer, #df-wpr-sidebar');
		return page_divs.find('[data-fiber-data]');
	},

	init_page_tree: function() {
		function handleClick(e) {
			if (e.node.url) {
				window.location = e.node.url;
				return true;
			}
			else {
				return false;
			}
		}

		function handleMoveNode(moved_node, target_node, position) {
			busyIndicator.show();

			$.ajax({
				url: '/api/v1/page/' + moved_node.id + '/',
				type: 'PUT',
				dataType: 'json',
				data: {
					action: 'move',
					target_node_id: target_node.id,
					position: position
				},
				success: function(data) {
					reloadPage();
				}
			});
		}

		function createLi(node, $li) {
			if (node.change_url) {
				var $div = $li.find('div');
				$li.find('.title').before('<span class="icon"></span>');
				$div.addClass('page');

				if (!node.show_in_menu) {
					$div.addClass('hidden-in-menu');
				}

				if (!node.is_public) {
					$div.addClass('not-public');
				}

				if (node.is_redirect) {
					$div.addClass('redirect');
				}
			}
		}

		function canMove(moved_node, target_node, position) {
			if (!moved_node.url) {
				// cannot move menu
				return false;
			}

			if (!target_node) {
				return true;
			}
			else if (!target_node.url) {
				// can move inside menu, not before or after
				return (position == 'inside');
			}
			else {
				// can move page node
				return true;
			}
		}

		this.admin_page_tree.tree({
			data: window.fiber_page_data,
			autoOpen: 0,
			saveState: 'fiber_pages',
			dragAndDrop: true,
			onMoveNode: handleMoveNode,
			selectable: true,
			onCreateLi: $.proxy(createLi, this),
			onCanMove: $.proxy(canMove, this)
		});
		this.admin_page_tree.bind('tree.click', handleClick);
		this.admin_page_tree.bind('tree.contextmenu', $.proxy(this.handle_page_menu_context_menu, this));

		// disable textual selection of tree elements
		$('.sidebar-tree').disableSelection();
	},

	init_content_tree: function() {
		this.admin_content_tree.tree({
			data: window.fiber_content_items_data,
			saveState: 'fiber_content_items'
		});
		this.admin_content_tree.bind('tree.contextmenu', $.proxy(this.handle_content_item_menu_context_menu, this));

		this.make_content_items_draggable();
	},

	make_content_items_draggable: function() {
		var tree = this.admin_content_tree.tree('getTree');
		tree.iterate(function(node) {
			if (node.change_url) {
				var $node = $(node.element);

				// make dragtgable
				$node.draggable({
					scope: 'content_item',
					revert: 'invalid',
					helper: 'clone'
				});
				$node.bind('dragstart', function() {
					adminPage.show_droppables();
				});
				$node.bind('dragstop', function() {
					adminPage.hide_droppables();
				});

				// add fiber-data
				$node.attr(
					'data-fiber-data',
					$.toJSON({
						type: 'content_item',
						id: node.id
					})
				);
			}

			return true;
		});
	},

	handle_page_menu_context_menu: function(e) {
		// remove other visible context menus
		$(document.body).find('.ui-context-menu').remove();

		var node = e.node;
		if (! node.url) {
			return;
		}

		var contextmenu = $('<ul class="ui-context-menu"></ul>');

		contextmenu.append(
			$('<li><a href="#">'+gettext('Edit')+'</a></li>').click($.proxy(function() {
				var change_page_form_dialog = new ChangePageFormDialog({
					url: node.change_url,
					page_id: node.id
				});
			}, this))
		);

		contextmenu.append(
			$('<li><a href="#">'+gettext('Add sub page')+'</a></li>').click($.proxy(function() {
				var add_page_form_dialog = new ChangePageFormDialog({
					url: node.add_url,
					below_page_id: node.id
				});
			}, this))
		);

		contextmenu.append(
			$('<li><a href="#">'+gettext('Delete')+'</a></li>').click($.proxy(function() {

				// show a confirmation dialog, that also warns about sub pages that will be removed
				var confirmation_dialog = $('<div class="dialog"></div>').dialog({
					modal: true,
					resizable: false,
					width: 400,
					position: ['center', 40],
					buttons: {
						'Delete': {
							text: gettext('Delete'),
							click: function() {
								$this = $(this);
								$this.dialog('close');

								busyIndicator.show();

								$.ajax({
									url: '/api/v1/page/' + node.id + '/',
									type: 'DELETE',
									data: {},
									success: function(data) {
										// when successful, reload the current page
										reloadPage({
											error: function() {
												// If page reload fails, because current page is deleted, then
												// go to the parent of the deleted page.
												reloadPage({
													id: node.parent.id
												});
											}
										});
									}
								});
							}
						},
						'Cancel': {
							text: gettext('Cancel'),
							click: function() {
								$this = $(this);
								$this.dialog('close');
							}
						}
					}
				});

				var confirmation_text = interpolate(gettext('<p>Are you sure you want to delete the page "<strong>%s</strong>"?</p>'), [$.trim(node.name)]);
				var num_sub_pages = node.children.length;
				if (num_sub_pages) {
					if (num_sub_pages == 1) {
						confirmation_text += interpolate(gettext('<p>There is <strong>%s page</strong> below this page that will also be deleted.</p>'), [num_sub_pages]);
					} else {
						confirmation_text += interpolate(gettext('<p>There are <strong>%s pages</strong> below this page that will also be deleted.</p>'), [num_sub_pages]);
					}
				}

				confirmation_dialog.dialog('option', 'title', gettext('Are you sure?'));
				confirmation_dialog.html(confirmation_text);
			}, this))
		);

		contextmenu.menu().removeClass('ui-corner-all');
		$(document.body).append(contextmenu);
		contextmenu.offset({ left: e.click_event.pageX, top: e.click_event.pageY });
	},

	handle_content_item_menu_context_menu: function(e) {
		$(document.body).find('.ui-context-menu').remove();

		var node = e.node;
		if (! node.change_url) {
			return;
		}

		var contextmenu = $('<ul class="ui-context-menu"></ul>');

		contextmenu.append(
			$('<li><a href="#">'+gettext('Edit')+'</a></li>').click(function() {
				new ChangeContentItemFormDialog({
					url: node.change_url
				});
			})
		);

		contextmenu.append(
			$('<li><a href="#">'+gettext('Delete')+'</a></li>').click(function() {
				var confirmationDialog = $('<div></div>').dialog({
					modal: true,
					resizable: false,
					width: 400,
					position: ['center', 40],
					buttons: {
						'Delete': {
							text: gettext('Delete'),
							click: function() {
								$(this).dialog('close');

								busyIndicator.show();

								$.ajax({
									url: '/api/v1/content_item/' + node.id + '/',
									type: 'DELETE',
									data: {},
									success: function(data) {
										reloadPage();
									}
								});
							}
						},
						'Cancel': {
							text: gettext('Cancel'),
							click: function() {
								$(this).dialog('close');
							}
						}
					}
				});
				confirmationDialog.dialog('option', 'title', gettext('Are you sure?'));
				confirmationDialog.html(gettext('<p>Are you sure you want to delete this item?</p>'));
			})
		);
		if (node.used_on_pages.length >= 1) {
			var context_submenu_used_on_pages = $('<ul class="ui-context-menu"></ul>');

			$(node.used_on_pages).each(function(index) {
				context_submenu_used_on_pages.append(
					$('<li><a href="#">'+node.used_on_pages[index].title+'</a></li>').click(function() {
						location.href = node.used_on_pages[index].url;
					})
				);
			});

			contextmenu.append(
					$('<li><a href="#">'+gettext('Used on pages')+'</a></li>').prepend(context_submenu_used_on_pages)
			);
		}
		contextmenu.flyoutmenu().removeClass('ui-corner-all');

		$(document.body).append(contextmenu);
		contextmenu.offset({ left: e.click_event.pageX, top: e.click_event.pageY });
	},

	toggleAdminSidebar: function() {
		var animation_duration = 200;

		var wpr_admin_sidebar = this.wpr_admin_sidebar;
		var toggle_button = this.toggle_button;

		// define animation values
		var animate_sidebar_left_to = wpr_admin_sidebar.hidden ? 0 : (10 - 240);
		var animate_body_left_to = wpr_admin_sidebar.hidden ? 240 : 10;

		function toggle_sidebar() {
			wpr_admin_sidebar.hidden = wpr_admin_sidebar.hidden ? false : true;
			$.cookie('df-sidebar-hidden', wpr_admin_sidebar.hidden, { path: '/' });
			if (wpr_admin_sidebar.hidden) {
				this.hide_sidebar();
			} else {
				this.show_sidebar();
			}
		}

		wpr_admin_sidebar.animate(
			{
				left: animate_sidebar_left_to
			},
			animation_duration,
			$.proxy(toggle_sidebar, this)
		);

		$('#wpr-body').animate(
			{
				left: animate_body_left_to,
				marginRight: animate_body_left_to
			},
			animation_duration
		);

		this.hide_admin_elements();
	},

	init_toggle_admin_sidebar: function() {
		var hidden = $.cookie('df-sidebar-hidden') == 'true' ? true : false;
		if (hidden) {
			this.hide_sidebar();
		}
		else {
			this.show_sidebar();
		}

		this.toggle_button.click(
			$.proxy(this.toggleAdminSidebar, this)
		);
	},

	show_sidebar: function() {
		this.wpr_admin_sidebar.hidden = false;

		$('body').addClass('df-sidebar');
		this.toggle_button.removeClass('df-hidden');
		this.wpr_admin_sidebar.removeClass('df-hidden');
	},

	hide_sidebar: function() {
		this.wpr_admin_sidebar.hidden = true;

		$('body').removeClass('df-sidebar');
		this.toggle_button.addClass('df-hidden');
		this.wpr_admin_sidebar.addClass('df-hidden');
	},

	init_admin_sidebar: function() {
		this.wpr_admin_layer = $('#df-wpr-layer');
		this.wpr_admin_sidebar = $('#df-wpr-sidebar');
		this.admin_sidebar = $('#df-sidebar');
		this.admin_page_tree = $('#df-sidebar-page-tree');
		this.admin_content_tree = $('#df-sidebar-content-tree');
		this.toggle_button = $('#df-btn-toggle-sidebar');

		this.init_page_tree();
		this.init_content_tree();
		this.init_toggle_admin_sidebar();
	},

	init_backend: function() {
		enhance_textareas($(document.body), false);
		enhance_comboboxes($(document.body));
		enhance_jsontextareas($(document.body));

		var backend_toolbar = $('<div id="fiber-backend-toolbar"></div>');
		var frontend_button = $('<p class="frontend"></p>').appendTo(backend_toolbar);
		var link = $(document.createElement('a')).text(gettext('Frontend')).attr('href', '/').attr('title', gettext('Frontend')).appendTo(frontend_button);
		$('<span class="icon"></span>').prependTo(link);
		backend_toolbar.prependTo($('body'));
	},

	init: function(body_fiber_data) {
		this.body_fiber_data = body_fiber_data;

		if (body_fiber_data.frontend) {
			$('body').addClass('df-admin');
			this.init_admin_sidebar();
			this.init_admin_elements();
		}
		else if (body_fiber_data.backend) {
			this.init_backend();
		}

		// TODO: move context menu hiding to another place
		// hide context menus when scrolling or resizing the window
		$(window).bind('scroll resize', function() {
			$(document.body).find('.ui-context-menu').remove();
		});

		// hide context menus when scrolling the sidebar
		$('#df-sidebar').bind('scroll', function() {
			$(document.body).find('.ui-context-menu').remove();
		});

		// hide context menus when (right)clicking somewhere else
		$('html, body').bind('click contextmenu', function() {
			$(document.body).find('.ui-context-menu').remove();
		});
	}
};

/* Reload page.
  If this is a fiber page, then obtain the current url from the server api.
  Otherwise, use the current url.

  params (optional): dictionary
	id (optional): page id to reload, default is the current page
	error (optional): callback function if the page cannot be reloaded

  Examples:
	// reload the current page
	reloadPage();

	// reload this page id
	reloadPage({
		id: page_id
	});

	// reload current page, if it fails load a fallback page
	reloadPage({
		error: function() {
			reloadPage(fallback_page_id);
		}
	});
*/
function reloadPage(params) {
	var page_id;

	if (params && params.id) {
		page_id = params.id;
	}

	if (!page_id) {
		// Get the id of the current page.
		page_id = $.parseJSON($('body').dataset('fiber-data')).page_id;
	}

	if (!page_id) {
		// Page id is not available, so this is not a fiber page.
		// Reload current url.
		window.location.replace(window.location);
	} else {
		busyIndicator.show();

		$.ajax({
			url: '/api/v1/page/' + page_id + '/',
			type: 'GET',
			success: function(data) {
				window.location.replace(data.data.attr.href);
			},
			error: function() {
				if (params && params.error) {
					params.error();
				}
			}
		});
	}
}


// TODO: subclass for specific uses (add / change) and types (page / content / other)
var FiberItem = Class.extend({
	// TODO: add defaults?

	init: function($element) {
		this.$element = $element;
		this.element_data = $.parseJSON(this.$element.dataset('fiber-data'));

		this.parent = null;
		this.children = [];
	},

	// this is run after the nested structure of fiber items is generated
	post_init: function() {
		this.button = null;
		this.droppable = null;

		// set minimum height of (possibly empty) containers
		// TODO: also do this for menus?
		if (this.element_data.type == 'content_item' && !this.parent) {
			this.$element.css('min-height', '20px');
		}

		this.attach_events();
		this.make_draggable();
	},

	add_child: function(child) {
		this.children.push(child);
	},

	show_admin_element: function() {
		if (!this.button) {
			this.create_button();
		}
		this.button.show();
	},

	show_admin_elements: function() {
		// show nested admin elements
		$.each(this.children, function(i, child) {
			child.show_admin_elements();
		});

		this.show_admin_element();
	},

	hide_admin_element: function() {
		if (this.button) {
			this.button.hide();
		}
	},

	hide_admin_elements: function() {
		// hide nested admin elements
		$.each(this.children, function(i, child) {
			child.hide_admin_elements();
		});

		this.hide_admin_element();
	},

	show_droppable: function() {
		// TODO: move to separate content_item class
		if (this.element_data.type == 'content_item') {
			if (!this.droppable) {
				this.create_droppable();
			}
			this.droppable.show();
		}
	},

	show_droppables: function() {
		// show nested droppables
		$.each(this.children, function(i, child) {
			child.show_droppables();
		});

		this.show_droppable();
	},

	hide_droppable: function() {
		if (this.droppable) {
			this.droppable.hide();
		}
	},

	hide_droppables: function() {
		// hide nested droppables
		$.each(this.children, function(i, child) {
			child.hide_droppables();
		});

		this.hide_droppable();
	},

	make_draggable: function() {
		if (this.element_data.type == 'content_item' && this.parent) {
			this.$element.draggable({
				scope: 'content_item',
				revert: 'invalid',
				zIndex: 1001,
				start: function() {
					adminPage.show_droppables();
				},
				stop: function() {
					adminPage.hide_droppables();
				}
			});
		}
	},

	orientation: function() {
		if (this.parent) {
			return this.parent.orientation();
		} else {
			if (!this._orientation) {
				if (this.$element.is('ul')) {
					var second = $('<li><a href="#">2</a></li>').prependTo(this.$element);
					var first = $('<li><a href="#">1</a></li>').prependTo(this.$element);
					if (first.offset().left < second.offset().left) {
						this._orientation = 'horizontal';
					} else {
						this._orientation = 'vertical';
					}
					first.remove();
					second.remove();
				}
			}
			return this._orientation;
		}
	},

	create_button: function() {
		// TODO: split this into subclasses
		if (this.element_data.type == 'page') {
			params = {
				before_page_id: this.element_data.id
			};

			this.button = new AddButton(
				this, params
			);
		} else if (this.element_data.type == 'content_item') {
			if (
				this.element_data.block_name &&
				this.element_data.page_id
			) {
				params = {
					before_page_content_item_id: this.element_data.page_content_item_id
				};

				this.button = new AddButton(
					this, params
				);
			}
		}
	},

	button_position: function() {
		position_params = {
			my: 'center center',
			at: 'left top',
			of: this.$element
		};

		if (this.element_data.type == 'page') {

			if (this.orientation() == 'horizontal') {
				if (this.element_data.url) {
					// menu items should have a '+' before them
					position_params = {
						my: 'center center',
						at: 'left center',
						of: this.$element.parent('li')
					};
				} else {
					// menu item containers should have a '+' at the end
					position_params = {
						my: 'center center',
						at: 'right center',
						of: this.$element.children('li').length ? this.$element.children('li:last') : this.$element
					};
				}
			} else if (this.orientation() == 'vertical') {
				if (this.element_data.url) {
					// menu items should have a '+' before them
					position_params = {
						my: 'center center',
						at: 'center top',
						of: this.$element.parent('li')
					};
				} else {
					// menu item containers should have a '+' at the end
					position_params = {
						my: 'center center',
						at: 'center bottom',
						of: this.$element.children('li').length ? this.$element.children('li:last') : this.$element
					};
				}
			}

		} else if (this.element_data.type == 'content_item') {
			// content item containers should have a '+' at the end
			if (!this.element_data.url) {
				if (this.children.length) {
					position_params.at = 'left bottom';
				}
			}
		}

		return position_params;
	},

	create_droppable: function() {
		this.droppable = new DroppableArea(
			this
		);
	},

	droppable_position: function() {
		position_params = {
			my: 'left top',
			at: 'left top',
			of: this.$element,
			offset: '0 -8'
		};

		if (!this.element_data.url) {
			// containers should have a droppable at the end
			if (this.children.length) {
				position_params.at = 'left bottom';
			} else {
				position_params.at = 'left top';
			}
		}

		return position_params;
	},

	attach_events: function() {
		this.$element.hover(
			$.proxy(this.on_mouseenter, this),
			$.proxy(this.on_mouseleave, this)
		);

		this.$element.dblclick(
			$.proxy(this.on_dblclick, this)
		);

		this.$element.disableSelection();
		this.$element.bind('contextmenu',
			$.proxy(this.on_contextmenu, this)
		);
	},

	on_mouseenter: function(e) {
		// bubble mouseenter to containers
		e.stopPropagation();
		if (!this.parent) {
			this.show_admin_elements();
		} else {
			this.parent.$element.trigger('mouseenter');
		}
	},

	on_mouseleave: function(e) {
		// bubble mouseleave to containers
		e.stopPropagation();
		if (!this.parent) {
			this.hide_admin_elements();
		} else {
			this.parent.$element.trigger('mouseleave');
		}
	},

	on_dblclick: function() {
		this.edit_content_item();
		return false;
	},

	on_contextmenu: function(e) {
		e.preventDefault();
		e.stopPropagation();

		// remove other visible context menus
		$(document.body).find('.ui-context-menu').remove();

		var contextmenu = $('<ul class="ui-context-menu"></ul>');

		if (this.element_data.type == 'page') {
			contextmenu.append(
				$('<li><a href="#">'+gettext('Edit')+'</a></li>').click(
					$.proxy(this.edit_page, this)
				)
			);
		} else if (this.element_data.type == 'content_item') {
			contextmenu.append(
				$('<li><a href="#">'+gettext('Edit')+'</a></li>').click(
					$.proxy(this.edit_content_item, this)
				)
			);

			contextmenu.append(
				$('<li><a href="#">'+gettext('Remove from page')+'</a></li>').click(
					$.proxy(this.remove_from_page, this)
				)
			);
			if (this.element_data.used_on_pages.length > 1) {
				var context_submenu_used_on_pages = $('<ul class="ui-context-menu"></ul>');
				$(this.element_data.used_on_pages).each(function(index, value) {
					context_submenu_used_on_pages.append(
						$('<li><a href="#">'+value.title+'</a></li>').click(function() {
							location.href = value.url;
						})
					);
				});

				contextmenu.append(
					$('<li><a href="#">'+gettext('Used on pages')+'</a></li>').prepend(context_submenu_used_on_pages)
				);
			}
		}

		contextmenu.flyoutmenu().removeClass('ui-corner-all');
		$(document.body).append(contextmenu);

		contextmenu.offset({ left: e.pageX, top: e.pageY });
	},

	// TODO: move to page specific class (remove / delete)
	remove_from_page: function() {
		busyIndicator.show();
		adminPage.hide_admin_elements();

		$.ajax({
			url: '/api/v1/page_content_item/' + this.element_data.page_content_item_id + '/',
			type: 'DELETE',
			data: {},
			success: function(data) {
				reloadPage();
			}
		});
	},

	// TODO: move to page specific class (edit)
	edit_page: function() {
		adminPage.hide_admin_elements();

		var changePageFormDialog = new ChangePageFormDialog({
			url: this.element_data.url,
			page_id: this.element_data.id
		});
	},

	// TODO: move to content item specific class (edit)
	edit_content_item: function() {
		if (this.element_data.url) {
			adminPage.hide_admin_elements();

			new ChangeContentItemFormDialog({
				url: this.element_data.url
			});
		}
	}
});


$(window).ready(function() {
	var body_fiber_data = $.parseJSON($('body').dataset('fiber-data'));
	adminPage.init(body_fiber_data);

	if (body_fiber_data.show_login) {
		$('body').addClass('df-admin');
		loginform = new LoginFormDialog();
	}
});

})(fiber_jQuery); // end of jQuery noConflict mode
