---
layout: post
title: "Microsoft Exam 70-480: Programming in HTML5 with JavaScript and CSS3"
date: 2013-01-18 09:11
comments: true
categories: [study, web]
---

I am planning to earn the Microsoft Certified Solutions Developer (MCSD): Web Applications certification. The first exam on this track is 70-480: Programming in HTML5 with JavaScript and CSS3. My study notes follow.<!--more-->

## Implement and Manipulate Document Structures and Objects (24%)

### Create the document structure ###

#### Structure the UI using semantic markup, including for search engines and screen readers ####

* HTML5 introduces several new tags, and does not support some others that were deprecated in HTML 4.0.1.

* The new tags are: 

`article, aside, audio,
bdi,
canvas, command,
datalist, details,
embed,
figure, figcaption, footer, header, hgroup,
keygen, mark, meter, nav, output, progress,
rp, rt, ruby,
section, source, summary,
time, track,
video,
wbr`

* In total there are 30 new tags.

* The following 12 tags are no longer supported in HTML5. Most of these were deprecated in HTML 4.0.1, with the exception of acronym, big, frame, frameset, noframes, and tt.

`acroynm, applet, basefont, big, center, dir, font, frame, frameset, noframes, strike, tt`

* The objectives make special mention of the new semantic tags for structure.

	* `section` (block): Grouping of content. Typically will include a heading. W3C: "A generic section of a document. A thematic grouping of content, typically with a heading." Sections usually will appear inside articles, but can be used independently.

	* `article` (block): Individual/independent block of content, such as a blog post or news article. Articles should be able to stand alone, whereas sections may be part of a larger whole. Usually contain sections. May be sub-articles (e.g. comments on blog entry). Should be independently re-distributable, e.g. in syndication.

	* `nav` (block): Navigational feature, usually site-level. Section of a page that links to other pages or parts within the page - a section with navigation links. W3C: "Not all groups of links need to be in a nav - intended for sections that consist of *major* navigation blocks. Common for footers to have list of links to policies etc, nav is not appropriate here."

	* `header`: Will contain heading content, often will contain nav. Usually site/page-level header. Will include introductory and/or navigational aids. Usually will contain sections H? / HGROUP. Can wrap TOC, search form, logos, etc.

	* footer (block): Will contain foot-note content, like attributions, copyright, etc. Typically site/page-level footer.
	* aside (block): Content tangentially related to primary content.

* Some of the new semantic structuring tags have the property of being "sectioning content,"" or being a "sectioning root." This means that the HTML outlining engine will give these nodes special treatment. Sectioning content defines the scope of headings and footers - within an `article, aside, nav, section` tag, headers are nested within the outline of their parents, regardless of header level. So, `<body><h2>Top</h2><section><h1>Inner</h1></section></body>` results in the H1 being outlined within the H2.

* Other new semantic tags not directly related to structure:

	* `figure` (block) / `figcaption` (text): The figure tag provides stand-alone, illustrative content, like a plot, image, or video; its first child figcaption tag provides a related caption.

	* `hgroup` (block): A group of headings. Should contain <h[1-6]> tags only. Provides a hint to the HTML outlining engine that only the first header in the group should be included in the outline, and that the following headings within the group are not additional outline-able sections but are instead subheadings of the first.

	* `mark` (text): Highlighted text, or text referred to elsewhere.

	* `time` (text): A date and/or time representation.

* The key to remember about the new "semantic" tags is that they allow one to express the meaning of a block in the tag itself, rather than via a CSS class or ID. This brings some standardization to naming (should I call it my class "article" or "feature"?), and promotes block roles to more prominence than other CSS attributes. They also aid in accessibility; for example, users of screen readers can indicate the order in which NAV sections should be read.

* It is important to frame the overall context for structuring a document as well. HTML documents always begin with a DOCTYPE declaration, and should include a HEAD and BODY, as well as charset declaration within the head.

	* The HTML5 doctype is simply `<!doctype html>`, without a URL or version number.
	* Inside the HEAD (and within the first 512 bytes of the document), a META tag indicating the charset should be included, e.g. `<meta charset=utf-8>`. Note META tags are not required to be closed, and the charset value does not need to be quoted. Specifying the charset is essential for avoiding potential security issues in which a URL could be crafted to inject arbitrary script into the page body.

* The new HTML5 tags are supported in IE 9, Firefox 16, Chrome 23, Safari 5.1, iOS Safari 4.0, Android Browser 2.2, and Blackberry 7.0. To ensure support in older browsers, an HTML5 shim can be employed, or the JavaScript `document.createElement` API can be used to create elements that do not exist.

#### Create a layout container in HTML ####

* Creating a layout container involves defining the elements that provide the overall structure to a page - positioning of the header/nav, footer, potential sidebar, and primary content.

* The primary CSS attribute that affects the layout of block display elements is `position`. It can have the following values:

	* `absolute`: An element positioned absolutely is offset (trbl) from its first parent with non-static position. Absolutely-positioned elements do *not* participate in normal layout flow.
	* `relative`: An element with relative position can be offset from its original/inherited position (trbl). Content moves, but originally reserved space is still preserved in flow.
	* `static`: Static position is the default, items are flowed normally and (trbl) has no effect.
	* `fixed`: Fixed position is (trbl) relative to the browser window and will not move when scrolled.

* When elements overlap, `z-index` must be considered. Higher z-index results in an element being positioned on top. Equal z-index results in the last item in the document being positioned on top.

* Modern layouts are most commonly achieved by `float`ing various elements around each other. Floating allows sibling content to flow around an element, if there is room  next to it. If not, the floated element will wrap to the next line. Floated elements should be inserted *before* float:none elements.

## To Be Continued...

I think that's a good introductory post and plenty of basic material to chew on. In my next post we'll pick up with the next objective: "Write code that interacts with UI controls."