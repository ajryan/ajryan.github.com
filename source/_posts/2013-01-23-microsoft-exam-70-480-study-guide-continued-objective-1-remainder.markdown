---
layout: post
title: "Microsoft Exam 70-480 study guide continued: Objective 1 remainder"
date: 2013-01-23 10:43
comments: true
categories: [study, web]
---

Continuing the study guide for Microsoft Exam 70-480. My test date is coming up fast so I need to pick up the pace. I spent a long time on the new HTML5 features, because I have not delved into them in much detail on a project. Most of the remainder of this objective is familiar territory and will have cursory notes.<!--more-->

## Implement and Manipulate Document Structures and Objects (24%)

### Apply styling to HTML elements programmatically

Much of this material was covered in my [earlier study guide post](http://ajryan.github.com/blog/2013/01/22/microsoft-exam-70-480-study-guide-continued/).

More specifically, after getting a node, you can `setAttribute('style', 'value')` or access the `.style` property directly and set specific CSS attributes on it. For example, `document.getElementById("container").style.color = "red"`. When applying hyphenated properties, drop hyphens as use lowerCamelCase (e.g. backgroundColor). Vendor-prefixed styles are accessed via `ms`, `Moz`, `O`, and `webkit` OR `Webkit` followed by the UpperCamelCase property.

With jQuery, it's a matter of using the `css` method to set a CSS property.

#### Change the location of an element

The same prior post gives information about moving an element within the DOM (insertBefore and *Child methods) or with jQuery (after/before/append/prepend).

Position can also be changed by modifying the CSS `position` and `top/right/bottom/left` properties (node.style.*). 

#### Apply a transform

CSS3 transformations allow translation (lateral movement), rotation, scaling, and skew, in both 2D (broad support) and 3D (much less support). Due to the immaturity of browser support, vendor-specific CSS attributes are required. The relevant 2D transform function values are:

`matrix, translate[|X|Y], scale[|X|Y], rotate, skew[|X|Y]`

Transforms are defined in CSS with the `transform`, `transform-origin', `transform-style`, `perspective`, `perspective-origin`, and `backface-visibility` attributes.

Internet Explorer 10 supports 3D transforms: 

`matrix3d, translate3d, translateZ, scale3d, scaleZ, rotate[3d|X|Y`

Other important considerations:

* Betas of IE10 required the `-ms-` prefix, but the current release does not.

* Multiple functions can be chained together in a single transform attribute and are cumulative.

* The box model and flow of a transformed element are calculated and applied *before* the transformation is applied - the element occupies its original position in the flow.

* Transforms can be combined with transitions for interesting animations. The `transition` attribute should be applied to the element's original style. When a new style is applied, either programmatically or via JavaScript, the transition occurs. You can specify `all` or a particular CSS property to transition. The syntax is `transition: property duration timing-function delay, ...`. Browser prefixes should be used.

* Remember this overall objective is about applying styling programmatically: in this case, the vendor-specific properties must be accessed, e.g. `div.style.WebkitTransformOrigin = "2px 5px"`.

#### Show and hide elements

Elements can be shown and hidden via the `display: none` and `visibility: hidden` CSS properties. The primary difference is that `display` removes the element from the document flow while `visibility` makes the element invisible but keeps its space in the flow.

Via native API, use `.style.display` or `.style.visibility`. Via jQuery, the `.hide()` API can be used, which allows the setting of a duration and/or a more complex easing function. Under the covers, jQuery affects the `display` CSS attribute. When animating, the size of the object is gradually reduced to zero before display is set to none.

### Implement HTML5 APIs.

#### Storage APIs

Cookies are traditionally used to associate values with a user and retrieve them at a later time, potentially across sessions. When the limitations of cookies are encountered, the storage API is useful. 

* Cookies are limited by most browsers to 4KB and 300 max count within a domain.
* They must be included in all HTTP requests and responses to the domain; they are stored locally in plain text
* They are domain-wide and do not support multiple application sessions within a browser session.

HTML5 Web Storage offers many improvements over cookies:

* Purely client side - the data does not need to round-trip, so there is no download time or bandwidth usage.
* No 4KB limitation - IE provides around 10 MB of local and 10 MB of session storage.
* Multi-session - if you use session storage, you can have two separate state storage areas within a single browser session.

Working with the Storage API:

* Check for browser support by checking `'localStorage' in window && window['localStorage'] !=== null` (similar for sessionStorage). In the following samples, sessionStorage can be substituted for localStorage. 

* The lifetime of localStorage is persistent across browser sessions; sessionStorage persists only as long as a page/tab is open.

* The scope of localStorage is within the same linear domain hierarchy (e.g. domain.com, bob.domain.com, and alice.bob.domain.com can access one-another's localStorage, but john.domain.com cannot access bob.domain.com localStorage). The scope of sessionStorage is within the current page/tab.

* There are three ways to store a key/value pair:

```
	localStorage.myKey = 'myValue';
	localStorage.setItem('myKey', 'myValue');
	localStorage['myKey'] = 'myValue';
```

* To get the value of a key:

```
	var value = localStorage.myKey;
	value = localStorage['myKey'];
	value = localStorage.getItem('myKey');
```

* To remove an item from storage:

```
	localStorage.removeItem('myKey');
```

* To clear all items from storage:

```
	localStorage.clear();
```

* Note that only string data may be stored as a value. Any non-string will be stored as a string using standard JavaScript conversion. If you want to preserve an object, `JSON.stringify` should be used to store and `JSON.parse` should be used to retrieve.

* Supported in IE 8, Firefox 3.5, Chrome 4, Safari 4, Opera 10.5, iOS Safari 3.2, Android 2.1.

#### AppCache API

The AppCache API allows the creation of offline web applications. Its primary functions are:

* Client-side cache of pages, images, scripts, style sheets, etc.
* Accessing cached content via standard URIs

In order to cache something you need to create a manifest. Following is a sample manifest:

```
	CACHE MANIFEST
	# 2013-24-01:v3

	CACHE:
	# Defines resources to be cached after they are downloaded for the first time
	script/app.js
	css/styles.css
	images/pic1.png

	FALLBACK:
	# Resources to use when online resources not available, in the form onlineURL cacheURL
	# File-for-file
	images/big_pic2.png images/pic2.png
	# File-for-path
	images/ images/offline.png
	# File-for-wildcard
	*.jpg offline.jpg

	NETWORK:
	# resources that will never be cached - user must be online
	images/pic3.png
```

Manifest files must be served with the MIME type `text/cache-manifest`, have CACHE MANIFEST as the very first line, and be UTF-8 encoded.

The manifest is referenced in the `html` tag. 

```
<html manifest="appcache.manifest">
...
</html>
```

Other AppCache notes:

* Any page that references a manifest is implicitly cached and does not need to be included in the manifest file itself.

* There are three ways to trigger a client-side cache update:

	* The cache automatically updated when the manifest file changes, so a version comment can be used to trigger an update.

	* The cache is updated programmatically with `applicationCache.update()` - this still requires that the manifest have changed from the last-downloaded version.

	* The user can manually clear the browser's cache of your site.

* Pages served over HTTPS can work offline.

* The `window.applicationCache` object provides access to the cache. It has the following useful properties and events:

	* `status` field: Indicates the current cache status, returned as one of the following appCache members: `UNCACHED, IDLE, CHECKING, DOWNLOADING, UPDATEREADY, OBSOLETE`\
	* `update` function: Trigger an async check of the manifest. Will throw an exception of the page is not cached.
	* `swapCache` function: Swap currently ready cache update into the current storage. After swapping in the cache, the page must be reloaded to reflect the changes.
	* `updateReady` event: fires when a cache update has been downloaded. In the handler, you can swap the cache and prompt the user to reload if they choose.
	* `error` event: fires when the manifest cannot download, changes during its download, returns 404, manifest is OK but page itself fails to download.
	* `progress` event: fires as each resource listed in the manifest is fetched
	* Several other events: `cached` (first cache of manifest), `checking` (manifest update check began), `downloading` (update was found and resources are being downloaded), `noupdate` (first manifest download done or checking done and manifest not changed), `obsolete` (manifest response is 404 or 410)

* Supported in IE 10, Firefox 16, Chrome 23, Safari 5.1, Opera 12.1, iOS Safari 3.2, Android 2.1.

#### Geolocation API

The Geolocation API allows you to access geographical location information via JavaScript. It is exposed via the `window.navigator.geolocation` object.

The following `geolocation` members are useful:

* `getCurrentPosition(successCallback, errorCallback, options)`: Async call to get the current position. The successCallback is called with a `Geoposition` object, or the errorCallback is called with an `error` object providing a code like `error.PERMISSION_DENIED`, `error.POSITION_UNAVAILABLE`, or `error.TIMEOUT`. The position object's `coords` member gives latitude, longitude, altitude, heading, speed, and accuracy (in meters) information.  Options can be provided for maximumAge (milliseconds) and enableHighAccuracy (can be affected by permissions).
* `watchPosition(...)`: has the same signature as getCurrentPosition but returns an integer of the `watchId` which can be used to cancel the watch activity. The successCallback will be called whenever the position changes.
* `clearWatch(watchId)`: stops watching position and will no longer call the callback for the watch set up with the `watchPosition` that returned `watchId`.

### Establish the scope of objects and variables.

#### Define the lifetime of variables

All JavaScript objects and variables have scope and lifetime. Some that are provided by the browser have global scope and infinite lifetime, like `document` and `window`; other variables have local scope and limited lifetimes.

More lifetime notes:

* Locally-scoped objects are created and destroyed each time their functions execute.

* Globally-scoped objects live forever.

* A function executed in an asynchronous context still has access to the variables from its scope, even if the function that defines its scope has finished executing. This is called a closure.

#### Keep objects out of the global namespace

Techniques are available to keep variables and functions out of the global namespace:

* Always declare variables and functions (hereafter "objects") with the `var` keyword.
* Always declare objects within the context of a function. 
* The above principal is expanded in what is generally referred to as the "module pattern". This refers to the use of an anonymous (key to avoid adding an identifier to the global namespace) Immediately-Invoked Function Expression (IIFE) to define a closure for the scope of the module. All of the following structures work to accomplish this goal.

```
var x = 5;

(function(){
	var x = 10;
}());

(function(){
	var x = 20;
})();

(function($){
	$('#container').text('hi');
	var x = 30;
}(jQuery));	// assumes jQuery script already included.

console.log(x); // "5"
```

#### Use the “this” keyword to reference an object that fired an event

The `this` keyword has some wrinkles in JavaScript. In the classic Object-Oriented model, `this` always refers to the current object instance. This is not so simple in JavaScript:

* In the global scope (outside any function) or when invoked within a globally-scoped function, `this` refers to the "global object", usually the same as `window`.
* In the context of a method (function member of an object), `this` refers to the object.
* In the context of a constructor, `this` refers to the function object being created.
* In the context of an event handler attached via jQuery's `on`, `this` refers to the DOM object that triggered the event.
* **Key for this objective**: In the context of an event handler attached via `addEventListener`, `attachEvent` (IE) - `this` refers to the object that fired the event.

#### Scope variables locally and globally

More scope notes:

* There are two scopes, global and local. Variables and functions with local scope are declared within a function and are accessible only within the body of that function (this includes nested functions); globally-scoped objects are declared outside a function and are accessible everywhere. There is no such thing as block scope.

* JavaScript performs variable hoisting - this means that variables are treated as having been declared at the top of the function, regardless of the line where they are actually declared.

* Special case: a variable named inside a function without the `var` keyword has global scope, but does not exist until that function is invoked.

### Create and implement objects and methods

#### Implement native objects

A native JavaScript object is created as follows:

```
var myObject = {
	stringMember: "xyz",
	intMember: 1,
	functionMember: function(thing) {
		console.log(thing);
	}
};
```
You can also create a new Object instance and then add members to it:

```
var myObject = new Object();
myObject.stringMember = "xyz";
```

More complex objects can be implemented using function constructors. This allows more control over the accessibility of the members of the object.

```
var Person = function(firstName, lastName) {
	var _privateInt = 5;
	var exports = {
		firstName: firstName,
		lastName: lastName
	}
	return exports;
};

var alice = new Person("alice", "jones");
```

Members of the object can then be accessed, e.g. `myObject.intMember = 2`.

#### Create custom objects and custom properties for native objects using prototypes and functions

There are several native objects, including:

`Number, Boolean, String, Array, Date, Math, RegExp`

A function can be added to an individual instance variable:

```
var d = new Date();
d.logIt = function() { console.log(this); };
```

A function can be added to the **prototype** of all objects created from the base function. These functions will be accessible on all objects created from that function, even those created before the function was added to the prototype.

```
var d = new Date();
if (!Date.prototype.logId) {
	Date.prototype.logIt = function() { console.log(this); };
}
```

#### Inherit from an object

Traditionally, inheritance has been accomplished as follows:

```
var Building = function(stories) {
	this.stories = stories;
	return this;
};
Building.prototype.writeStories = function() {console.log(this.stories); };

var House = function(stories, squareFeet) {
	Building.call(this, stories);
	this.squareFeet = squareFeet;
	return this;
}
House.prototype = new Building();
House.prototype.constructor = House;
House.prototype.dump = function() { console.log(this.stories + " " + this.squareFeet);};

var h = new House(2, 2500);
h.dump();
```

Inheriting from an object can be accomplished in modern browsers via `Object.create(proto)`.

```
var Building = function(stories) {
	this.stories = stories;
	return this;
};
Building.prototype.writeStories = function() {console.log(this.stories); };

var House = function(stories, squareFeet) {
	Building.call(this, stories);
	this.squareFeet = squareFeet;
	return this;
}
House.prototype = Object.create(Building.prototype);
House.prototype.dump = function() { console.log(this.stories + " " + this.squareFeet);};

var h = new House(3, 3300);
h.dump();

```
# Fin.

This concludes the first of the four objectives - "Implement and Manipulate Document Structures and Objects"