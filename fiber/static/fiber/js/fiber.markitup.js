(function($) {

Fiber.enhance_textarea = function(textarea) {
	var $textarea = $(textarea);
	$textarea.markItUp(markitup_settings);

	// Helper class to retrieve/replace user text selection in IE
	var UserSelectionIE = function() {
		this.textRange = (document.selection && document.selection.createRange) ? document.selection.createRange() : false;
	};
	UserSelectionIE.prototype.markItUp = function(options) {
		if (this.textRange && options) {
			this.options = options;

			if ((typeof(this.options['openWith']) === 'string') &&
			    (typeof(this.options['closeWith']) === 'string') &&
			    (typeof(this.options['placeHolder']) === 'string')) {
				if (this.textRange.text.length) {
					this.textRange.text = this.options['openWith'] + this.textRange.text + this.options['closeWith'];
				} else {
					this.textRange.text = this.options['openWith'] + this.options['placeHolder'] + this.options['closeWith'];
				}
			} else if (typeof(this.options['replaceWith']) === 'string') {
				this.textRange.text = this.options['replaceWith'];
			}
			this.textRange.select();
		}
	};

	var header = $textarea.parent('.markItUpContainer').find('.markItUpHeader');

	// Link To A Page In This Site
	header.find('li.select_page a').click(function() {
		// Save selection in textarea. This is necessary for IE.
		var userSelectionIE = new UserSelectionIE();

		var page_select_dialog = new Fiber.PageSelectDialog();
		page_select_dialog.action_click = function() {
			if (userSelectionIE.textRange) {
				// Replace textarea selection for IE
				userSelectionIE.markItUp({
					openWith: '"',
					closeWith: '":'+ page_select_dialog.selected_url,
					placeHolder: 'page'
				});
			} else {
				$.markItUp({
					target: $textarea,
					openWith: '"',
					closeWith: '":'+ page_select_dialog.selected_url,
					placeHolder: 'page'
				});
			}

			this.destroy();
		};
	});

	// Link To A File In This Site
	header.find('li.select_file a').click(function() {
		// Save selection in textarea. This is necessary for IE.
		var userSelectionIE = new UserSelectionIE();

		var file_select_dialog = new Fiber.FileSelectDialog();
		file_select_dialog.action_click = function() {
			var selected_file_path = $(this.uiDialog.find('tr.ui-state-highlight td')[0]).text();

			if (userSelectionIE.textRange) {
				// Replace textarea selection for IE
				userSelectionIE.markItUp({
					openWith: '"',
					closeWith: '":'+ selected_file_path,
					placeHolder: 'file'
				});
			} else {
				$.markItUp({
					target: $textarea,
					openWith: '"',
					closeWith: '":'+ selected_file_path,
					placeHolder: 'file'
				});
			}

			this.destroy();
		};
	});

	// Link To An Image In This Site
	header.find('li.select_link_to_image a').click(function() {
		// Save selection in textarea. This is necessary for IE.
		var userSelectionIE = new UserSelectionIE();

		var image_select_dialog = new Fiber.ImageSelectDialog();
		image_select_dialog.action_click = function() {
			var selected_image_path = $(this.uiDialog.find('tr.ui-state-highlight td')[0]).text();

			if (userSelectionIE.textRange) {
				// Replace textarea selection for IE
				userSelectionIE.markItUp({
					openWith: '"',
					closeWith: '":'+ selected_image_path,
					placeHolder: 'image'
				});
			} else {
				$.markItUp({
					target: $textarea,
					openWith: '"',
					closeWith: '":'+ selected_image_path,
					placeHolder: 'image'
				});
			}

			this.destroy();
		};
	});

	// Image
	header.find('li.select_image a').click(function() {
		// Save selection in textarea. This is necessary for IE.
		var userSelectionIE = new UserSelectionIE();

		var image_select_dialog = new Fiber.ImageSelectDialog();
		image_select_dialog.action_click = function() {
			var selected_image_path = $(this.uiDialog.find('tr.ui-state-highlight td')[0]).text();
			var selected_image_textile = '!' + selected_image_path + '!';

			if (userSelectionIE.textRange) {
				// Replace textarea selection for IE
				userSelectionIE.markItUp({
					replaceWith: selected_image_textile
				});
			} else {
				$.markItUp({
					target: $textarea,
					replaceWith: selected_image_textile
				});
			}

			this.destroy();
		};
	});

};

})(fiber_jQuery);
