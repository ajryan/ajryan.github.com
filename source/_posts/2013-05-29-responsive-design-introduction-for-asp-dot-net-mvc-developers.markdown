---
layout: post
title: "Responsive Web Design - Introduction for ASP.NET MVC Developers"
date: 2013-05-29 12:53
comments: true
categories: [development, html, CSS, javascript, IIS, ASP.NET, Visual Studio]
---

The term "Responsive Web Design" was coined in 2010 by Ethan Marcotte in his [canonical article](http://alistapart.com/article/responsive-web-design) defining the technique. Recently, I spent some time researching the history and modern state of the art of Response Web Design (RWD). This article presents a survey of my findings, and provides examples of specific techniques. We'll focus on Visual Studio / ASP.NET MVC tools and techniques for getting the job done.<!--more-->

## Defining Responsive ##

In the context of Responsive Web Design, the term "responsive" is the opposite of "prescriptive." You've probably heard arguments against prescriptive approaches to language and grammar. Language and meaning are organic, evolving things that are constantly being re-created by their users. Prescriptivism in language does not account for its evolution, and can ignore the context and needs of its users. We have experienced "Prescriptive Web Design" from the dawn of the web, in the form of "best viewed in Netscape 4.0.3 on a 800 x 600 monitor at 16-bit color depth." The modern variation is a placeholder page replacing desired content with "sorry, this page not formatted for mobile devices" How short-sighted, to actually hide content from valuable eyeballs? Responsive Web Design is decidedly *not* prescriptive.

Responsive Web Design is a set of techniques that allow our pages to adapt to the capabilities of the client. Client, in this case, being both the electronic and human consumer of our content. The goal is to ensure that our content can be comfortably and accessibly consumed by as many devices and people, of varying capabilities, as possible. 

These techniques respond to

* Browser capabilities (HTML5, native audio/video, CSS3, plugins)

* Device capabilities (geolocation, resolution, input methods)

* User capabilities (vision, hearing)

* Viewport (media type, resolution, density, orientation)

Prescriptive designs enforce requirements on the client: they require certain screen sizes, input devices, or plugin support to fully render content. Responsive designs inquire about the capabilities of the client and put forth the best possible experience given those capabilities. They are as functional as possible in limited scenarios and enhance the experience as capabilities increase.

## Why? ##

Why use responsive techniques? The sweet spot for RWD is a balance of development effort and reach: responsive design techniques will get your content in front of the most eyeballs, in a usable form, the the least effort. This form may not be optimal for every client scenario, but the aim is to find an appropriate compromise where required, and to take advantage of advanced capabilities where possible.

Consider the polar approaches:

* The cheapest option is to design only for desktop and cross your fingers for mobile users. Desktop clients less restrictive and therefore simpler to target.

* The most expensive option is to implement separate designs for phone, tablet and desktop (potentially even developing native mobile clients.) You will deliver the most optimal experience for each device, at greatly increased cost of development *and maintenance.*

Beyond the cost-reach compromise, RWD provides several other benefits:

* **Consistency**: Delivery of a consistent experience across devices. Styling, navigation, and user experience will be familiar and aid users who arrive at your site using different clients at different times. There is a single set of markup and CSS to maintain, reducing the chance of styles "evolving apart" over time.

* **Value First**: RWD forces you to first examine the value of the content being delivered, then decide how to present it. The tendancy when designing for a single platform can be to dive into *Lorem Ipsum* wireframes before content is fully realized. A content-first approach results in a design that exists purely to support the maximum transmission of the value of content; wireframe-first approaches can result in designs with vestigial features that distract from content value.

Responsive design is about delivering the greatest possible user joy regardless of the access method. It is not a dogma or a recipe, it's more of a mindset that is focused on experience first.

## Why Not? ##

Responsive techniques are not useful or cost-effective for all applications. When the client capabilities are fully controlled, it is not necessary to design for multiple clients. Enterprise applications being deployed across known devices are the most common scenario here. Solutions that require specific interaction modes may not benefit from RWD, for example, interactions that are simply not possible on a touch device.

## History ##

Here is a brief timeline of some influential articles that have led to the current state of thinking on Responsive Web Design:

* [John Allsopp - A Dao of Web Design](http://alistapart.com/article/dao): Letting go of control in favor of accepting and adapting to client differences.

* [Ethan Marcotte - Responsive Web Design](http://alistapart.com/article/responsive-web-design): Original articulation of the principles.

* [Jason Grigsby - CSS Media Query for Mobile is Fool's Gold](http://blog.cloudfour.com/css-media-query-for-mobile-is-fools-gold/): First major rebuttal, warning that bandwidth suffers - additional HTML, CSS, and (potentially) JavaScript to render on a smaller screen with *more* code. Important for pivoting the discussion toward general adaptability away from a mobile "silver bullet."

* [Luke Wroblewski - Mobile First](http://alistapart.com/article/organizing-mobile): Refinement of responsive design approach working from most-constrained to least.

## Core Techniques ##

The original **Responsive Web Design** article defined the approach as being composed of three techniques: a Fluid Grid, Media Queries, and Flexible Images. Thinking in these areas has evolved a bit since the original article -- here are some thoughts on each of the original techniques:

* **Fluid Grid (Adaptive Grid)** The original article names it "fluid," but this has come to mean proportional, which is not strictly required. An adaptive grid (and an adaptive layout in general) provides a framework for adjusting presentation to window sizes, resolutions, and screen densities. The earliest fluid layouts were focused on achieving proportional columns using CSS (a technique that was trivial using the common table-based layouts at the time). Further developments of adaptive layout are more focused on typography, especially given the emergence of high-density displays that make pixel- and point-sizing less reliable. A fully-fledged adaptive grid framework (potentially combined with a pre-defined base style set) can be a nice productivity boost.

* **Media Queries** The media query is a CSS3 feature that allows you to target CSS rules at specific ranges of window or screen size. The most common application of media queries in RWD is for adjusting the layout by repositioning or hiding certain elements as the available space is reduced.

* **Flexible Images (Adaptive Media)** The original article focuses on flexibly sizing and positioning images for smaller screen dimensions and lower bandwidth. Further thinking in this area has included selectively loading smaller image files in lower-bandwidth scenarios. With the addition of HTML5 Video and Audio capabilities, these media types should be considered as well.

It is absolutely not essential to use all of these techniques in every web design effort. These primary techniques form the foundation of RWD thinking, and many additional techniques have been developed along the way. There is a toolbox available, and you can choose the appropriate tools for each job.

## Grid Systems ##

### Grid System Rationale ###

Many responsive sites rely on a grid system for layout. Abstracting the foundation of the layout provides a clean, consistent framework for positioning site components. A grid can be defined as a horizontal sectioning of the canvas in to columns and gutters. Content lives in columns, and gutters provide whitespace between them. Grids help us think about design, and they help users engage with your content. You can compare a CSS grid to the "snap to grid" function provided in form designer and presentation software: it provides convenient, consistent alignment and spacing for the elements on a page.

Several frameworks and generators exist that provide grid systems. They fall into four basic categories:

• **Fixed**: the container width is set to a fixed width, and the column count, column width, and gutter width are set to fixed fractions of the container. Column spanning is possible, but the container will never resize with the window.

• **Responsive**: a set of media queries provides a progressive step-down of container width, column count, column width, and gutter width.

• **Fluid**: the column count is fixed; container width, column width, and gutter width are percentages of the canvas.

• **Fluid + Responsive**: media queries set the container width and column count; within each breakpoint, column and gutter widths are proportional.

### Grid System Framework Comparison ###

There are dozens of CSS grid frameworks available, at varying degrees of complexity, maturity, and compatibility. This list selects some notable popular frameworks that focus on different use cases, roughly ordered from simplest to more fully-featured. New ones are constantly being released that build on principles developed in those that came before.

<table class="content-table">
	<tr>
		<th>Framework</th><th>Classification</th><th>Max size</th><th>Columns</th><th>Notes</th>
	</tr>
	<tr>
		<td><a href="http://960.gs">960gs</a></td><td>Static</td><td>960px</td><td>12 / 16</td><td>Grid only<br/>IE7+<br/>CSS</td>
	</tr>
	<tr>
		<td><a href="http://www.getskeleton.com/">Skeleton</a></td>
		<td>Responsive</td>
		<td>960px (desktop/tablet-landscape)<br/>768px (tablet-portrait)<br/>420px (mobile-landscape)<br/>300px (mobile-portrait)</td>
		<td>16</td>
		<td>Lightweight CSS framework<br/>IE7+<br/>CSS</td>
	</tr>
	<tr>
		<td><a href="http://responsive.gs/">responsive.gs</a></td>
		<td>Fluid + Responsive</td>
		<td>Any<br/>Columns stack below 768px</td>
		<td>12/16/2024</td>
		<td>Grid only<br/>IE7+<br/>CSS</td>
	</tr>
	<tr>
		<td><a href="http://neat.bourbon.io/">Bourbon Neat</a></td><td>Fluid + Responsive</td><td>Any</td><td>12<br/>(or custom)</td><td>Grid addon to Bourbon<br/>IE9+<br/>Sass</td>
	</tr>
	<tr>
		<td><a href="http://twitter.github.io/bootstrap/">Bootstrap</a></td>
		<td>Static OR<br/>Fluid OR<br/>Fluid + Responsive</td>
		<td>Static: 940px<br/>Others: Any (nestable)</td>
		<td>16</td>
		<td>Full client-side framework<br/>IE6+<br/>LESS</td>
	</tr>
</table>

Some additional notes on the grid frameworks:

* **960gs** The granddaddy. A good starting point to understand the concepts to launch you toward rolling your own. Viable for sites that are likely to have only desktop traffic. Consider 1140 grid given rise of wider screens.

* **Skeleton** Relatively minimal and easily customizable. Provides a layout skeleton (output) and CSS skeleton (source) with reset/sane defaults /media-query breakpoints for you to customize. Has not been maintained in a while (lots of open Github issues) - the dmur fork is more active.

* **Bourbon Neat** Relies exclusively on Sass mixins - no classes applied to markup. Extremely customizable.

* **Responsive.gs** Enforces border-box box-sizing model on all elements.

* **Bootstrap** Probably the best-known (or at least most buzzed-about) client-side framework available. A complete suite of layout, styling, and input/interactivity tools. Tends to leave a recognizable stamp on the appearance of the site.

Note that responsive features rely on media queries - grids with responsive features will serve either the desktop or mobile view to <= IE8 depending on whether they are "mobile first" or "desktop first." JavaScript polyfills may be leveraged to extend back-compatibility to earlier browsers than those targeted by the framework.

It can be difficult to adapt an existing project to use a CSS framework - the framework may rely on certain style reset features, typographic assumptions, box-model settings, or other styling techniques that are not compatible with the existing codebase. Even for new work, adoption of a framework can assert a certain identifiable look and feel (for example, the Bootstrap buttons and navbar). It is worth spending time customizing the base style to ensure unique branding. This will often require you to learn at least the basics of a CSS preprocessor tool like LESS or Sass.

### Grid System Demo ###

A page demonstrating the [responsive.gs](http://responsive.gs) grid system can be found here: [DEMO](http://codecampresponsive.apphb.com/Home/ResponsiveGs). View the page on a mobile device and/or experiment with resizing the browser window.

Responsive.gs provides a very lightweight framework purely focused on grid layout; it does not enforce any look-and-feel on the site. The framework applies the `box-sizing: border-box` CSS rule to all elements, enabling a simpler sizing model. This rule makes it easier to calculate sizing in layouts: it changes the box size calculation to include padding and border in the overall height and width of a box. Due to this low-level rule, adoption of responsive.gs into an existing layout could result in some painful size adjustments. However, you'll find that starting fresh with this rule applied can make layout size calculations much more intuitive.

The framework is proportionally fluid at widths above 768px, while all columns stack vertically at 100% width on smaller screens. It's very simple to lay out columns with responsive.gs: apply the `row` class to define a full-width row, then use the `col` and `span_*` classes to set proportional column widths within the row.

{% codeblock responsive.gs lang:html %}
<section class="row">
  <article class="col span_6 bg4"><h3>col span_6</h3><img class="left-quarter" src="http://fillmurray.com/200/300"><p>Column 1.</p></article>
  <article class="col span_6 bg3"><h3>col span_6</h3><p>Column 2.</p></article>
  <article class="col span_4 bg2"><h3>col span_4</h3><p>Column 3.</p></article>
</section>
{% endcodeblock %}

Compatibility notes: Because the `box-sizing` rule is not supported on IE7 or lower, a polyfill (for inclusion using conditional comments) is provided. The framework is "mobile first", in that all columns are laid out to 100% width in the base style, then set to proportional widths within a media query. This means that users of IE8 and below will receive the mobile experience.

## Media Queries ##

Media queries are mostly about width, width, width. We generally assume that our layouts are equal to the width of the browser window and that they can be infinitely long. Thank goodness we aren't working with fixed-height pages! Everyone expects to scroll vertically when viewing a page, and the mouse wheel convention is to scroll the page vertically. There are some clever / artistic layouts that scroll horizontally, but these can be difficult for users to "grok" initially, and should only be used for specialized content and audiences. (A media query can reference height, and there are some interesting cases where that can be useful described [here](http://trentwalton.com/2012/01/11/vertical-media-queries-wide-sites/).)

Given that the primary constraint on our designs is the width of the page, it's very useful to be able to write width-aware CSS rules. When there is room, allow elements to be positioned next to one another horizontally. When there isn't, reposition elements into a vertical flow, remove non-essential elements, and/or provide methods for the user to toggle the visibility of lower-priority elements.

### Selecting Breakpoints ###

The horizontal width where a media query changes the layout is referred to as a "breakpoint." There are many references that attempt to provide the screen dimensions of popular devices, which one could adopt for layout breakpoints. This approach is *not* workable, because the device landscape is constantly changing - it would result in an explosion of difficult-to-maintain rules, and bloat the size of the CSS transmitted to the browser.

Here is an overview of a workflow that can help identify the most appropriate breakpoints for an application:

* CONTENT is king. It's not possible to select and design around a set of device-based breakpoints. CSS will be heavy and under-performing, and compromises will be made to "fit in the box." It's better to evaluate your content and think in general terms about presenting it in "big," "middle," and "small" contexts.

* Start at a size near your initial wireframe target, and start resizing until things start looking "wrong"

* Set a breakpoint with some breathing room before things go haywire, then apply rules to fix the layout in the "wrong side"

* Repeat this exercise moving inward and outward until unreasonably small and large

* Three sizes, small /medium / large, represent a maintainable sweet-spot

Additional considerations for media query breakpoints:

* Line length is important. On wider layouts, it may be useful to set max-width to a comfortable reading length and allow margins to increase as the viewport grows wider. In browsers that support it, CSS3 multi-column can allow content to flow to multiple columns and avoid whitespace in wider scenarios.

* Scaling widths out in ems proportionally to a base-font em ensure your design renders consistently across operating systems with missing fonts, user-selected fonts, zooms, and display densities.

* Knowledge of common device widths is useful (along with testing the site on biggest-marketshare devices), but creating a layout appropriate to the content is most important of all.

* iOS reports *portrait* `device-width` and `device-height` regardless of orientation (use `orientation` in query to differentiate)

### Size, Move, Hide, Replace, or Transform? ###

There are many options available for style specializations inside a media query. This list defines the most common techniques:

* **Size**: Shrink box and / or font

* **Move**: Reposition an element (most commonly moving horizontally laid out columns to vertically stacked)

* **Hide**: Remove entirely

* **Replace**: Provide the same function in a smaller package (common example – list of navigation links collapsed to navigation menu menu)

* **Transform**: Maintain the same markup, but change its initial presentation (e.g. collapsing a context box into an accordion)

Selection of the most appropriate technique depends on several factors:

* Semantics of the element / component

* May descend from size > move > hide at cascading breakpoints

* Remember that the most-important content should come first in markup for accessibility and SEO (see grid system push / pull classes)

### The Mobile Viewport ###

In order to effectively leverage media queries for mobile devices, it is necessary to include the `viewport` meta tag in the `head` of the page, like so:

    <meta name="viewport" content="width=device-width" />

This instructs the mobile browser to treat device pixels as CSS pixels, that is, for the physical and virtual dimensions of the screen to be the same. (This is a bit of an oversimplification, since multiple high-density display pixels are sometimes treated as a single virtual device pixel. See [A Tale of Two Viewports](http://www.quirksmode.org/mobile/viewports.html) for an excellent explanation.) When the `viewport` tag is not present, most mobile browsers will effectively "zoom" a larger virtual viewport into the smaller physical device viewport, by treating a device pixel as multiple CSS pixels. When mobile devices first became capable of browsing the web, this behavior was necessary to provide enough space to lay out pages designed exclusively for the desktop. Users employ the "double-tap zoom" gesture to focus on portions of the page. 

The `viewport` meta tag allows us to instruct the browser how to treat the Layout Viewport relative to the Visual Viewport. Let's examine the differences between the Layout Viewport and the Visual Viewport.

**Layout Viewport**

* CSS pixels available to layout

* Resize of a Desktop browser window resizes the Layout Viewport and causes a reflow

  * The Mobile Layout Viewport is set at the initial load and does not change

  * Mobile devices play some extra tricks with text wrapping - divs will lay out correctly, but the wrap point may be adjusted based on double-tap zoom size; text may re-wrap on zoom as well.

**Visual Viewport**

* The Visual Viewport is the CSS pixel dimension of the visible area of the page

* Resize of a Desktop browser window resizes the Visual Viewport

* Mobile zoom resizes the Visual Viewport

Additional notes on the `viewport` meta-tag:

* Controls the layout viewport

* Determines the number of device pixels per CSS pixel at zoom = 1

* 99% of the time, use the <meta name=“viewport” content=“width=device-width”> tag 

* For most modern devices, the default iOS and Android layout viewport width is 980 CSS pixels, with initial scale set to match the visual viewport

* The content attribute is comma-separated

  * Width = [px|device-width]. Device width is “screen width in CSS pixels at 100% zoom”

  * Height – little-used

  * Initial-scale = device pixel multiplier

  * Maximum-scale = device pixel multiplier

  * User-scalable = [true|false]. Whether to allow the user to scale. Think very carefully before limiting this.

  * CSS 2.1 recommends that CSS pixels correlate to one 96dpi pixel at arms’ length; initial-scale=1 requests this

* IE10 on Windows 8 ignores the viewport meta tag in snapped view. You need the following CSS declaration:

{% codeblock lang:css %}
@-ms-viewport {
    width: device-width;
}
{% endcodeblock %}

### Tangent: ASP.NET MVC Technique - Server-side mobile refinement ###

This topic is not directly related to media queries, but can be used in conjunction with them to achieve comfortable layout *and* bandwidth reduction while maintaining a single page of markup. It is important to remember that content hidden with `display: none` is still downloaded. The idea behind the following technique is to remove a component from the layout flow using a media query, and apply server-side processing to entirely eliminate its content from the payload.

Here is an overview of the steps involved:

* Add the [NuGet package](http://nuget.org/packages/51Degrees.mobi) from [51Degrees.mobi](http://51degrees.mobi) for better device detection. Inclusion of this package causes the `Request.Browser.IsMobileDevice` property to be set for each request, detecting a much broader range of devices than the out-of-box behavior.

* An alternative is the [DetectMobileBrowsers.com](http://DetectMobileBrowsers.com) regex for simple useragent-based detection.

* In your server-side markup (.aspx or .cshtml), wrap the component you wish to hide from mobile devices as follows:

{% codeblock lang:html %}
@if (!Request.Browser.IsMobileDevice) {
	<section class="sidebar">
	    <p>Check out my twitter feed:</p>
	    <ul>
	        <li>Post 1</li>
	        <li>Post 2</li>
	        <li>Post 3</li>
	    </ul>
	</section>
}
{% endcodeblock %}

* Implement a media query to flow the remainder of the layout into the previously-occupied space.

* When Output Caching is in use, ensure the mobile and non-mobile variations of the page are cached separately. Include the attribute `[OutputCache(Duration = 60, VaryByCustom = "Mobile")]` on each controller action that relies on this technique. Provide the custom cache key by overriding `GetVaryByCustomString` in `Global.asax.cs`:

{% codeblock lang:csharp %}
public override string GetVaryByCustomString(System.Web.HttpContext context, string custom)
{
    if (custom != "Mobile")
        return null;

    return context.Request.Browser.IsMobileDevice.ToString();
}
{% endcodeblock %}

* Depending on the nature of the content, you may wish to provide a way for the user to asynchronously request it after the initial page load.

You can see this technique in action here: [DEMO](http://codecampresponsive.apphb.com/Home/OutputCacheMobileHiding). View the source of the page from a mobile device (or with a mobile user agent string) to verify that the sidebar is not transmitted. On desktop devices, the sidebar is included and hidden/shown as the page width changes.

## Adaptive Media ##

In Marcotte's original article, the only medium considered for adaptability was the image. Modern sites deliver images, video, and audio to devices of varying capabilities. The following sections describe responsive techniques for dealing with all three.

A page demonstrating many of the following techniques is available here: [DEMO](http://codecampresponsive.apphb.com/Home/ResponsiveMedia).

### Responsive Images ###

We must consider layout and bandwidth when planning a responsive approach for images. Here are some notes on responsive image techniques:

* **Scaling**: Basic image scaling can be accomplished with `width: 100%` and `max-width` CSS properties. IE7 may require a polyfill depending on other CSS properties in use. 

* **Cropping**: At media query breakpoints, set negative margins with overflow: hidden to avoid shrinking the image and 

* **Swap/Omit**: On the server side, alternative image href may be set in markup, or images may be omitted when a mobile browser is detected. An HTTP handler may be employed to dynamically scale images according to user agent. Client-side techniques for selecting images according to page size exist, but there is no silver bullet - most of these techniques will result in multiple image downloads or suffer from very un-semantic (and potentially non-accessible) markup.

* **SVG**: Scalable Vector Graphics images have the benefit of full-fidelity scaling with a single file. Internet Explorer introduced SVG support in IE9, so a fallback is required for earlier IE versions. As with most "swap" techniques, it's important to monitor network traffic and avoid transmission of both files, when possible, or to employ a server-side approach.

Be sure to choose the correct image format. PNG works best for logos and vectors, JPEG for photos and other realistic images. GIF should rarely be used, though can be effective for <= IE6 as a work around for PNG transparency. Losslessly optimize your PNG images - this can reduce size by a surprising amount (see [PngGauntlet](http://http://pnggauntlet.com/) for example).

### Responsive Video ###

HTML5 introduced full video support, which modern browsers all handle. HTML5 video is generally more performant and less buggy than relying on plugin-based approaches. It is necessary, though, to provide a fallback for older browsers - the goal with video is a balance of performance and compatibility.

* Supply VP8- and H.264-encoded files and you will cover nearly all user agents

* Omitting the type from the final source will cause most browsers to check the metadata to determine if it can be played. Bandwidth / accessibility tradeoff.

* One *could* use the little-known `media` attribute to serve smaller files to smaller devices, although at the time of this writing it appears this attribute may be dropped.

* IIS NOTE: need to add mime types for video, or IIS will return a 404.3. See `Web.config` section `system.webserver\staticContent\mimeMap`.

* Within the video tag, below the sources, include a flash fallback and video download link (for users without flash).

* Use JavaScript and/or HTTP module and user agent detection to serve appropriate codec and filesize

* Good resources:

  * Mark Pilgrim’s excellent, very in-depth (though getting out-of-date) guide: http://diveintohtml5.info/video.html
  
  * Concise, easy to read guide from JWPlayer: http://www.longtailvideo.com/support/jw-player/jw-player-for-flash-v5/22644/using-the-html5-video-tag/

  * [FlowPlayer](http://flowplayer.org/) is a pre-packaged, responsive, broadly compatible option.

  * Nice tool for generating markup: [Video for Everybody](http://camendesign.co.uk/code/video_for_everybody)

Don't discount the option of hosting the video externally (Vimeo, Youtube) and IFRAMEing in a player – they’ve solved the cross-browser issues and will take bandwidth & connection pressure off your server.

**Flexible video sizing:**

* For the `<video>` tag, you can rely on `width: 100%` and `max-width` with `height: auto` to flexibly resize video while maintaining aspect ratio.

* Flash and IFRAMEs have issues – can’t automatically set height to preserve the aspect ratio. Thierry Koblentz “Creating Intrinsic Ratios for Video” to the rescue - [post](http://www.alistapart.com/articles/creating-intrinsic-ratios-for-video/).

  * Set a wrapper DIV with relative position, zero height, and bottom-padding representing the aspect radio (e.g. 56.25% == 16:9)

  * Set an inner div absolutely positioned with 100% width and height

  * This technique has issues in IE7 and below – use a conditional style sheet

### Responsive Audio ###

Techniques for audio largely follow those for video, except that layout adjustment is not really a concern. Rely on the HTML5 `audio` tag with fallbacks, and provide download links for users without plugin support. On the server side, consider serving files encoded to lower bit rates when mobile devices are detected.

## Other Considerations ##

Now that we have covered the the three primary categories of responsive web design techniques, let's briefly visit some related considerations.

### Forms ###

Forms must provide a usable mobile layout and be touch-friendly. The following are important points to consider for responsive forms:

* Note the “field zoom” feature of many mobile browsers. When an input field is focused, the browser will zoom the viewport to the width of the field.

  * This makes top-aligned labels better, otherwise the label or field may be cut off.

  * Set `input, textarea { font-size: 1em }` to avoid extra zoom on iDevices – lower font sizes will introduce additional zoom

* Touch-friendly

  * Sizing (finger targets): extra padding on inputs, and larger label targets for radio and checkbox controls.

  * Click versus Touch events: there is a delay between the initial touch event and final click event, during which the browser is waiting for a potential gesture. If you know that a given control has no gesture interaction, you can trigger interactions from the touch event, resulting in faster response. This can be difficult to implement reliably - see [FT Fastclick]( http://labs.ft.com/articles/ft-fastclick/) for a solid implementation.

* Input Types

  * HTML5 introduces new values for the `input` element's `type` attribute. Mobile browsers key off this attribute to provide the most appropriate keyboard layout for the type (e.g. email type results in keyboard with @ symbol).

  * Some desktop browsers implement some native validation and specialized input controls for certain input types. This may not be desired - the `form` element's `novalidate` attribute can prevent native validation, and CSS can be used to prevent browser-substituted controls. 

### Typography ###

The trend is toward more minimal interfaces that place typography in the forefront. The increased prevalence of high-density displays makes the display of beautiful type accessible to a greater number of users. Consider the following points related to typography:

* The user (or at least platform developer) has already specified his / her preferred default font size. Rather than overriding this, we should respect it as a base and scale from there.

* New “retina”-class devices and high density displays can make pixel sizing unreliable. The future of the “pixel” is uncertain - `em` should be the default sizing unit, unless you have a really good reason to use pixels.

* On higher-density displays, you may wish to increase font weight to achieve a uniform result across displays. Antialiasing on lower-density displays results in greater perceived weight given the same font on a higher-density display.

* On standard-density displays, serif fonts below 12px are not sharp enough. But you should be over 12px anyway.

* Good Metrics
 
  * Font size: bigger than you think. Hold a book or magazine at a comfortable distance and compare.
 
  * Contrast: ratio font color to background brightness. Steer clear of full black (looks like a “hole”) and full white.
  
  * Line Height: for text, 140% of font size is a good general rule, but depends on face (ascender/descender ratio to x-height and “blackness”). In CSS, use proportional line-height notation (e.g. `font: Arial 1em/1.44`) with no units.

  * Line Length (measure): From 45 to 75 characters is good balance of ease in tracking to next line versus not having to do it too often. When browsers support it, you can use CSS3 column count when the view gets very wide. You can leave width “on the table” and set a `max-width`. Ensure text blocks have good height in proportion to width.

  * Spacing: Headings can often use more vertical padding to breathe

* Gotchas

  * Note that when using fluid (proportional) layout techniques, you give up some control over line length

  * Web Font browser quirks and format support (use [Font Squirrel](http://www.fontsquirrel.com/))

  * When serving locally, apply correct mimetype to web fonts

## Conclusion ##

Responsive Web Design has been around for several years, and has been gathering steam since its introduction. There is no "one size fits all" approach for cross-device sites - careful evaluation and application of the available techniques is required. Good luck on your projects!