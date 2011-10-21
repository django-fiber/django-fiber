/*
Copyright (c) 2003-2011, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

CKEDITOR.editorConfig = function( config )
{
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	// config.uiColor = '#AADC6E';
};

// Extra settings to get rid of the extra whitespace within tags
// More info on this subject here: http://cksource.com/forums/viewtopic.php?f=6&t=14493
CKEDITOR.on('instanceReady', function(ev)
{
	var tags = ['p', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'];

	for (var key in tags) {
		ev.editor.dataProcessor.writer.setRules(tags[key], {
			indent : false,
			breakBeforeOpen : true,
			breakAfterOpen : false,
			breakBeforeClose : false,
			breakAfterClose : true
		});
	}
});