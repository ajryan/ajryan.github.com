---
layout: post
title: "HTML and jQuery: Displaying and Positioning Custom Tooltips"
date: 2013-04-25 11:15
comments: true
categories: [development, html, jquery, javascript]
---

At a client I was recently tasked with implementing a site that presents tooltips with a custom appearance. I thought I'd share some lessons learned about consistently displaying the tooltips and working around positioning problems.<!--more-->

## Removing existing tooltips

In the site I am working with, the custom tooltips must be displayed for an ASP.NET control that has its own tooltip implementation. This means that when the page is initially rendered, the `title` attribute is already set on the items where I need custom tooltips. This means I need to remove the title attribute but preserve its text for displaying later in my custom tooltip. There is an other wrinkle, in that the site is displayed in Internet Explorer's quirks mode, which means the `alt` attribute will also display a browser tooltip on hover. I needed to remove the `alt` attribute as well, to avoid "double tooltips" with my custom tooltip and the browser tooltip being displayed simultaneously.

Here's a snippet illustrating the technique:

{% codeblock lang:javascript %}
$map.children('area').each(function() {
  var $area = $(this);
  $area.attr('data-customtooltip', $area.attr('title'));
  $area.removeAttr('alt title');
})
{% endcodeblock %}

The control uses an image map to provide tooltip and interactive functions. I get a jQuery object for the `map`, then iterate is children. The `title` attribute is copied to a `data-customtooltip` attribute, and the `alt` and `title` attributes are removed to prevent display of the native browser tooltip.

## Displaying and positioning the custom tooltip

The next piece of the puzzle is displaying a custom tooltip when the mouse is over an `area`. I include the following HTML in the master layout page:

{% codeblock lang:html %}
<div
  id="tooltip"
  style="
    position: fixed;
    z-index: 999;
    display: none;">
</div>
{% endcodeblock %}

This creates a `div` that is initially invisible and detached from the overall page layout. Of course, the `div` is also styled to fit with the site's overall theme.

Back in the JavaScript, I hooked the `mouseenter` event to set the tooltip text and then display the hidden `div`. Initially, I simply positioned the `div` below and to the left of the mouse pointer. Unfortunately, this naive positioning technique falls down when the mouse is near the lower-right corner of a page or frame: the tooltip is cut off at the page/frame edge. Native browser tooltips "float" above the page surface and can even extend beyond the edges of the browser window, but this is not possible with an HTML element. To work around this issue, I detect the "quadrant" of the page that the mouse cursor occupies, and position the tooltip away from the page corner. For example, if the mouse cursor is nearest the lower-right corner, I position the tooltip above and to the left of the cursor.

{% codeblock lang:javascript %}
$tooltipDiv = $('#tooltip');
$map
 	.on('mouseenter', 'area', function(e) {
 		var $this = $(this);
 		
 		// set the tooltip text from our custom attribute
 		var customTitle = $this.attr('data-customtooltip');
 		$tooltipDiv.html(customTitle);

 		// determine if the mouse is in the left / top "halves" of the document
 		var mouseLeft = e.pageX < (document.body.clientWidth / 2);
 		var mouseTop = e.pageY < (document.body.clientHeight / 2);

 		// position the tooltip away from the mouse quadrant
 		var css = {};
 		if (mouseLeft)
 			css.left = e.pageX + 10 + 'px';
 		else
 			css.left = e.pageX - (7 + $tooltipDiv.width()) + 'px';
 		if (mouseTop)
 			css.top = e.pageY + 10 + 'px';
 		else
 			css.top = e.pageY - (7 + $tooltipDiv.height()) + 'px';

 		$tooltipDiv.css(css);
 		$tooltipDiv.show();
	})
	.mouseleave(
		function() { $tooltipDiv.hide(); }
	);
{% endcodeblock %}

Note that I am always using the `left` and `top` CSS attributes to position the `div`. I ran into strange issues when I attempted to set the left/top to auto and position using right/bottom. I don't think Internet Explorer supports positioning in this manner.

Also note that I don't attach the `mouseenter` handler to each `area` directly. There can be dozens of areas on the page that require a tooltip - hooking up that many event handlers would not perform as well. It's better to attach a single handler for when the event bubbles to the `map`, then let jQuery filter for the child elements that we want to deal with.


