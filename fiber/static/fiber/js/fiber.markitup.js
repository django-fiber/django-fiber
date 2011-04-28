(function($) {

Fiber.enhance_textarea = function(textarea) {
	var $textarea = $(textarea);
	$textarea.markItUp(markitup_settings);

	var header = $textarea.parent('.markItUpContainer').find('.markItUpHeader');
	header.find('li.select_page a').click(function() {
		// Save selection in textarea. This is necessary for ie.
		var caret = $textarea.caret();

		var page_select_dialog = new Fiber.PageSelectDialog();
		page_select_dialog.action_click = function() {
			// Restore textarea selection.
			$textarea.caret(caret);

			var selected_page_path = this.uiDialog.find('a.ui-state-active').attr('href');
			$.markItUp({
				target: $textarea,
				openWith: '"',
				closeWith: '":'+ selected_page_path,
				placeHolder: 'link'
			});

			this.destroy();
		};
	});

	header.find('li.select_link_to_image a').click(function() {
		// Save selection in textarea. This is necessary for ie.
		var caret = $textarea.caret();

		var image_select_dialog = new Fiber.ImageSelectDialog();
		image_select_dialog.action_click = function() {
			// Restore textarea selection.
			$textarea.caret(caret);

			var selectedImagePath = $(this.uiDialog.find('tr.ui-state-highlight td')[0]).text();
			$.markItUp({
				target: $textarea,
				openWith: '"',
				closeWith: '":'+ selectedImagePath,
				placeHolder: 'image'
			});

			this.destroy();
		};
	});

	header.find('li.select_image a').click(function() {
		// Save selection in textarea. This is necessary for ie.
		var caret = $textarea.caret();

		var image_select_dialog = new Fiber.ImageSelectDialog();
		image_select_dialog.action_click = function() {
			// Restore textarea selection.
			$textarea.caret(caret);

			var selected_image_path = $(this.uiDialog.find('tr.ui-state-highlight td')[0]).text();
			$.markItUp({
				target: $textarea,
				replaceWith: '!' + selected_image_path + '!',
				placeHolder: 'image'
			});

			this.destroy();
		};
	});

	header.find('li.select_file a').click(function() {
		// Save selection in textarea. This is necessary for ie.
		var caret = $textarea.caret();

		var file_select_dialog = new Fiber.FileSelectDialog();
		file_select_dialog.action_click = function() {
			// Restore textarea selection.
			$textarea.caret(caret);

			var selected_file_path = $(this.uiDialog.find('tr.ui-state-highlight td')[0]).text();
			$.markItUp({
				target: $textarea,
				openWith: '"',
				closeWith: '":'+ selected_file_path,
				placeHolder: 'file'
			});

			this.destroy();
		};
	});
}

})(fiber_jQuery);
