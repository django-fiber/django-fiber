==============
Advanced usage
==============


This document is used to gather more advanced usage examples.


Optional settings:
==================

These settings are optional (default values are shown):

::

	FIBER_DEFAULT_TEMPLATE = 'base.html'
	FIBER_TEMPLATE_CHOICES = []

	FIBER_EXCLUDE_URLS = []

	FIBER_IMAGES_DIR = 'uploads/images'
	FIBER_FILES_DIR = 'uploads/files'

	FIBER_METADATA_PAGE_SCHEMA = {}
	FIBER_METADATA_CONTENT_SCHEMA = {}

	COMPRESS = [the opposite of DEBUG]


Set or override fiber_page in the view:
=======================================

In this example, the news_item_detail view looks up the Page of the news_item_list by looking up its named URL. This way, you can reuse the content you have placed on the news_item_list Page for each news_item_detail Page.

::

	def news_item_detail(request, news_item_slug):
	    news_item = get_object_or_404(NewsItem, slug=news_item_slug)
	    
	    fiber_page = Page.objects.get(url__exact='"news_item_list"')
	    
	    t = loader.get_template('news_item_detail.html')
	    c = RequestContext(request, {
	        'fiber_page': fiber_page,
	        'news_item': news_item
	    })
	    return HttpResponse(t.render(c))
