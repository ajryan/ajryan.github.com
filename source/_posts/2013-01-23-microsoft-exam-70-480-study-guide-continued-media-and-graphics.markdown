---
layout: post
title: "Microsoft Exam 70-480 study guide continued: Media and Graphics"
date: 2013-01-23 10:43
comments: true
categories: [study, web]
---

Continuing the study guide for Microsoft Exam 70-480, we are addressing the media and graphics goals within the **Write code that interacts with UI controls** objective.<!--more-->

## Implement and Manipulate Document Structures and Objects (24%)

### Write code that interacts with UI controls ###

#### Implement media controls

HTML5 has two new tags, `video` and `audio`, which allow direct embedding of these sources. Prior to HTML5, this was accomplished via the `embed` and `object` tags, and relied on plugins for playing the source. Modern browsers provide native implementations for playing audio and video, in support of the new tags.

##### Tag attributes

The `audio` and `video` tags supports the following custom attributes:

* `src`: URL for the source file
* `autoplay`: boolean - should the file play immediately?
* `loop`: boolean - should the file loop upon completion?
* `controls`: boolean - should the browser show its own controls?
* `preload`: value can be `none`, `metadata`, or `auto`. Indicates whether none of the file, only its metadata, or a browser-determined amount of the file should be pre-loaded before beginning playback.

The `video` tag supports the additional attribute:

* `poster`: URL for an image to display while the video is loading

Note that in HTML5 boolean attributes can be included without a value (`<audio src='file.mp3' controls />`), or self-value (, as )`<audio src='file.mp3' controls="controls"/>`).

Earlier HTML5 drafts had an `autobuffer` atrribute that is superseded by `preload`. Both attribute can be used while browsers transition.

These are block content tags, and so they support all of the attributes common to block content.

##### Source formats

Different browsers support different file formats, and there is no single format supported by all major browsers.

* For audio, WAV garners the most support, with only Chrome excluded. Firefox, Chrome, and Opera support Ogg; Safari, Chrome, and IE support MP3; Firefox, Safari, Opera, and IE support WAV.

* For video, webm has been agreed upon as the standard format for video, with some caveats. Safari does not currently support webm, and Internet Explorer will play webm video *if* the codec is installed separately. Within the type attribute, the codecs can be specified, video and then audio, e.g. `<source src="movie.webm" type='video/webm; codecs="vp8, vorbis"'/>`. Note the double quotes embedded within single quotes. The other major video types are mp4 and ogv
.
Because there is not a single source format supported by all major browsers, `source` elements can be nested inside the `audio` and `video` elements to provide multiple sources. The order of the sources is important: certain versions of Firefox had issues if the MP3 source was included first, so it's recommended to provide an OGG source followed by an MP3 source to cover all browsers. For video, mp4 should be included first to avoid an iOS Safari issue.

MIME type should be specified on the source tags - this allows the browser to pre-determine which file to download.

##### Examples

Given the above information, here is an HTML5 `audio` control with all possible attributes set:

```
	<audio controls autoplay loop preload="auto" autobuffer>
		<source src="file.ogg" type="audio/ogg">
		<source src="file.mp3" type="audio/mp3">
		<p>We could supply a Flash fallback or <a href="">link to the file for download</a> here.</p>
	</audio>
```

And video:

```
	<video controls autoplay loop preload="auto" autobuffer>
		<source src="movie.webm" type='video/webm; codecs="vp8, vorbis"' />
		<source src="movie.ogv" type='video/ogg; codecs="theora, vorbis"' />
		<p>We could supply a Flash fallback or <a href="">link to the file for download</a> here.</p>
	</audio>
```

##### Browser compatibility

Create an `audio` or `video` element and check for the existence of the `canPlayType` function on it to determine if the HTML5 audio tag is implemented in the current browser. The `canPlayType` function can then be used to check what file types are supported: empty string, "maybe", or "probably" will be returned. When the tag is not supported, or the browser does not support your available sources, you can fall back to Flash.

Currently only IE10 and Chrome support the `<track> ` element within a media control. The purpose of tracks is to add parallel timed features such as navigation points, subtitles, or alternate audio streams.

##### Methods and Properties

If the `controls` attribute is not set, custom controls can be implemented by accessing the following methods and properties. You may wish to implement your own controls to achieve a more consistent appearance across browsers.

Important properties:

`error, src, readyState, seeking, currentTime, duration, paused, playbackRate, played, seekable, ended, autoplay, loop, volume, muted`

Important methods:

`canPlayType, load, play, pause`

##### Events

The media controls provide the following commonly-used events:

* `canplay`: Fires when the control determines whether it can play the video source.
* `playing`: Fires when playback is ready to start after having been paused or media not yet downloaded.
* `ended`: Fires when playback stops at the end of the file.
* `timeupdate`: Fires when the playback position changes during playback. Firefox fires once per frame, Webkit fires every 250ms.
* `play`: Fires when no longer paused, either after the play function is called or autoplay causes playback to begin.
* `pause`: Fires when paused after the pause function is called.
* `volumechange`: Fires after the volume or muted attribute value changes.

Note that the playing and play events seem very similar: play will fire as soon as the play command is issued, and then the playing event will fire once playback actually begins.

#### Implement HTML5 canvas and SVG graphics

Both the Canvas and SVG APIs are available to developers for creating graphics. Both are vector graphics technologies but are better suited for different tasks. The primary difference is that SVG can be expressed in markup and styled with CSS, while Canvas drawing is performed through scripting. Another difference is that SVG is a "retained mode" model in which the graphic definition remains in memory and can be modified and re-rendered, while Canvas is an "immediate" or "fire and forget" model that renders directly to the screen when its API is called.

The choice of which technology to use comes down to several factors:

* Developer familiarity: graphics APIs - Canvas versus markup - SVG
* Performance: size of screen has a large effect on Canvas, number of objects has a large effect on SVG
* Fidelity: SVG is scalable and stays crisp at any magnification
* High performance filtering: Canvas is better suited to pixel-based render, e.g. filters, ray tracers, pixel replacement/green screen
* Real-time data: Canvas is much better suited for images that require rendering real-time changes in many small objects, e.g. weather animations


##### Canvas

The `canvas` element enables rendering of resolution-independent graphics. A context is used for drawing, the most commonly implemented being Canvas 2D. Most browsers have implemented hardware-accelerated canvas rendering.

Canvas allows you to draw rectangles, lines, fills, arcs, shadows, Bezier curves, quadratic curves, images, and video.

Check for canvas support by creating a canvas element, verifying that it possesses the get `getContext` function, and that `getContext('2d')` is truthy. Canvas is supported on IE 7 / Firefox 3 / Safari 3 / Chrome 3 / Opera 10 / Android 1; basically, wide support on current browsers. Warning: IE 8 and below do not support the full API - the Explorercanvas library an be used in this case.

With a `canvas` element on the page, you can call its `getContext('2d')` method to get a Canvas 2D context and begin drawing.

The following are some interesting canvas APIs, assuming `ctx` is a Canvas 2D context:

* `ctx.fillStyle = "style"`: sets the current fill style, may be a color, pattern, or gradient
* `ctx.strokeStyle = "style"`: similar to fillStyle, but for outlines.
* `ctx.drawImage(img, x, y)`: draw an HTML Image element into the context. Using an img on the page, it can be drawn during window.onLoad. For an Image created in JavaScript, the image.onLoad event should be used.
* `ctx.fillRect(x, y, width, height)`: draw the fill of a rectangle in the current fillStyle
* `ctx.strokeRect(x, y, width, height)`: draw the stroke of a rectangle in the current strokeStyle
* `ctx.clearRect(x, y, width, height)`: clears the target rectangle
* `ctx.beginPath()`: begins a new path for the next stroke
* `ctx.moveTo(x,y)`: moves the pen position without drawing
* `ctx.lineTo(x,y)`: defines a path with the pen from the current position
* `ctx.strokeStyle = "style"`: sets the stroke style
* `ctx.stroke()`: draws the current path with the current stroke style
* `ctx.font`, `ctx.textAlign`, and `ctx.textBaseline`: set the current text drawing properties
* `ctx.fillText("text", x, y)`: write text at the given position (x at left edge, y relative to textBasline).
* `var grad = ctx.createLinearGradient(x0, y0, x1, y1)`: create a linear gradient with the given angle
* `grad.addColorStop(position, "color")`: add a color stop to the gradient, at a position between 0.0 and 1.0.

Canvas coordinates originate in the upper left, with the X axis horizontal.

You can listen to the `click` event, which provides cursor position, to interact with the canvas.

##### SVG

SVG graphics can be displayed by including an `<svg>` tag with SVG markup inside. SVG graphic elements can be styled with their own attributes, or with CSS. SVG elements can be modified via the DOM API, but CSS styling takes precedence for rendering. CSS pseudo-classes (like :hover) can be used to trigger style changes. SVG has its own CSS namespace with attributes like fill, stroke, stroke-width, stop-color, etc.

The `defs` tag within the SVG tag allows the definition of gradients and filters, which can be combined for interesting fill effects, blurs, and shadows.

**Example**

The following example illustrates the primary primitives and styles possible

```
	<style type="text/css">
		svg.draw {
			width: 300px;
			height: 300px;
			border: #666 1px solid;
		}
		.black-stroke {
			stroke: black;
			stroke-width: 2;
		}
		.red-fill {
			fill: red;
		}
		.blue-fill {
			fill: blue;
		}
	</style>
	
	<svg class="draw" xmlns="http://www.w3.org/2000/svg">
		<defs>
			<radialGradient id="gradient" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
				<stop offset="0%" style="stop-color:rgb(200,200,200); stop-opacity:0"/>
				<stop offset="100%" style="stop-color:rgb(0,0,255); stop-opacity:1"/>
			</radialGradient>
		</defs>
		<circle class="red-fill black-stroke" cx="50" cy="50" r="25" />
		<rect class="blue-fill black-stroke" x="5" y="5" width="30" height="40"/>
		<line class="black-stroke" x1="0" y1="0" x2="200" y2="200" />
		<ellipse cx="150" cy="150" rx="30" ry="50" fill="url(#gradient)" />
		<polygon  points="20,10 300,20, 170,50" fill="green" />
		<polyline points="0,0 0,20 20,20 20,40 40,40 40,60" fill="yellow" />
	</svg>
```