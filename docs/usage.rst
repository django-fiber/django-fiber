=====
Usage
=====


Usage instructions
==================


Page tree
---------

Fiber was designed to coexist with your existing Django apps. In addition to the URLs that you define in your urls.py files you can create a tree of URLs that Fiber uses to create menus. Each node of the tree is a Page, which:

- has a title
- lives at a specific URL
- references a template
- serve as a placeholder for Content items
- can optionally redirect to another URL
- has some more tricks up its sleeve we'll talk about later

So before you can use Fiber template tags in your templates, you first have to create the Page tree. A simple Page tree might look like this:

- mainmenu

  - Home
  - About us

    - Mission
    - Our people

  - News


The root node is a special Page, whose sole purpose is to group Pages into a menu. The title of the root node is used to reference the menu when writing out the menu in your templates. The other properties of the root node (like URL) are ignored by Fiber.

Note: You can create multiple root nodes to create multiple, independent menus.


Pages
-----

The URL of a Page can be specified in 3 different ways:

- as an absolute URL, like this: /this/is/an/absolute-url/
- as a relative URL, like this: relative-url
- as a named URL, like this: "news_item_list"

Absolute URLs
.............

Using absolute URLs, you can specify the full URL path to the Page.
Absolute URLs should start (and preferably also end) with a slash.
You can also specify links to external sites by providing the full URL (starting with http:// or https://).

Relative URLs
.............

Relative URLs are like folders on your computer. The full absolute URL of the Page is determined by walking up the tree, while concatenating relative URLs until the root node is reached, or until an absolute URL is encountered.
Relative URLs should not contain slashes.

Named URLs
..........

Named URLs are looked up in the urls.py files of all registered apps.
Currently only named URLs that don't have parameters are supported.


Templates
---------

When you have created your Page tree, you can start using the Fiber template tags in your templates.
At the beginning of your template(s), load the Fiber template tags::

	{% load fiber_tags %}

Using the Fiber template tags, you can:

- write out content items, that either

  - have a specified name
  - are linked to a specific location on the current page
  - are linked to a specific location on another page

- write out valid XHTML menu structures

  - of pages below a named root page (this is the menu name),
  - limited to a minimum and maximum level (depth),
  - that mark the currently active page,
  - optionally expanding all descendants of the currently active page,
  - with all possible css hooks you could ever need


Content items
-------------

You can write out content items with the 'show_content' and 'show_page_content' template tags::

	{% show_content "content_item_name" %}
	{% show_page_content "block_name" %}
	{% show_page_content other_page "block_name" %} other_page being a Page object

Examples
........

This shows content item named 'address'::

	{% show_content "address" %}

This shows content items that are linked to the location named 'content' on the current page::

	{% show_page_content "content" %}

This shows content items that are linked to the location named 'content' on another page 'other_page'::

	{% show_page_content other_page "content" %}


Menus
-----

You can write out menus with the 'show_menu' template tag::

	{% show_menu "menu_name" min_level max_level ["all_descendants / all"] %}

The menu name refers to a top-level node in the page tree.

Examples
........

The examples below assume the pages are structured like this:

- mainmenu

  - Home
  - About us

    - Mission
    - Our people

  - News
  - Products

    - Product A

      - Testimonials
      - Downloads

        - Technical data sheet
        - User manual

    - Product B

      - Downloads

    - Product C

      - Downloads

  - Contact

    - Newsletter
    - Directions

- generalmenu

  - Disclaimer
  - Privacy statement

Main menu
.........

Show first and second level pages, below the root page named 'mainmenu'::

	{% show_menu "mainmenu" 1 2 %}

When the user is currently visiting the 'Home' page, this will show (current pages are bold):

- **Home**
- About us
- News
- Products
- Contact

When the user is currently visiting the 'Products' page, this will show:

- Home
- About us
- News
- **Products**

  - Product A
  - Product B
  - Product C

- Contact

As you can see, the sub pages of the currently active 'Products' page are automatically expanded.

When the user is currently visiting the 'Product A' page, this will show:

- Home
- About us
- News
- **Products**

  - **Product A**
  - Product B
  - Product C

- Contact

The sub pages of the 'Product A' page are not shown, because they are outside of the specified minimum and maximum levels.

Sub menu
........

Show pages from level 3 to 5, below the root page named 'mainmenu', and also show all descendants of the currently active page::

	{% show_menu "mainmenu" 3 5 "all_descendants" %}

When the user is currently visiting the 'Home' page, this will show an empty menu, since it cannot be determined what level 3 pages are currently active.

However, when the user is currently visiting the 'Product A' page, this will show:

- **Product A**

  - Testimonials
  - Downloads

    - Technical data sheet
    - User manual

- Product B
- Product C

Notice that all pages below the currently active 'Product A' page are expanded because of the 'all_descendants' parameter.

Sitemap
.......

Show all pages, with all pages expanded::

	{% show_menu "mainmenu" 1 999 "all" %}
	{% show_menu "generalmenu" 1 999 "all" %}
