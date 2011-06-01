jQuery.fn.slugify = function(obj) {
	jQuery(this).data('obj', jQuery(obj));
	jQuery(this).keyup(function() {
		var obj = jQuery(this).data('obj');
		var slug = jQuery(this).val().replace(/\s+/g,'-').replace(/[^a-zA-Z0-9\-]/g,'').toLowerCase();
		jQuery(this).data('obj').val(slug);
	});
	jQuery(this).blur(function() {
		var obj = jQuery(this).data('obj');
		var slug = jQuery(this).val().replace(/\s+/g,'-').replace(/[^a-zA-Z0-9\-]/g,'').toLowerCase();
		jQuery(this).data('obj').val(slug);
	});
};