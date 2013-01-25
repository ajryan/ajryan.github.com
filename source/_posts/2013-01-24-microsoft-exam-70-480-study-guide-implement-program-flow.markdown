---
layout: post
title: "Microsoft Exam 70-480 Study Guide: Implement Program Flow"
date: 2013-01-24 15:43
comments: true
categories: [study, web]
---

Let's pick up the 70-480 study guide with the second objective: Implement Program Flow.<!--more-->

## Implement program flow

{% blockquote %}
Iterate across collections and array items; manage program decisions by using switch statements, if/then, and operators; evaluate expressions.
{% endblockquote %}

* Iterating a collection or array:

```
for (item in collection) {
	console.log(item);
}

for (var i = 0; i < collection.length; i++) {
	var item = collection[i];
	console.log(item);
}

// NOT SUPPOTED IN IE
collection.forEach(item, index) {
	console.log(item + " at " + index);
}

$.each(collection, function(index, item) {
	console.log(item + " at " + index);
});
```

* Switch statement

```
function(stringVar) {
	switch (stringVar) {
		case "one":
			console.log(1);
			break;
		case "two":
			console.log(2);
			break;
		default:
			console.log(999);
	}
}
```
* If/then/else

```
if (condition) {
	// do a thing
}
else if (differentCondition) {
	// do another thing
}
else {
	// nothing at all
}
```

* JavaScript supports a similar set of comparison and assignment operators as other modern languages. Some special ones to watch for:

```
var x = condition? "yes" : no;

function returnsUndefined {
	return void(5+5);
}

var y = (5, 6); // y = 6;

delete collection[4]; // collection[4] returns undefined

var x = new Date();
x instanceof Date; // true

typeof variable; // returns function, string, number, boolean, object, or undefined
```

* Evaluate expressions

```
eval("console.log('evaluated');");
```

* 

## Raise and handle an event

{% blockquote %}
Handle common events exposed by DOM (OnBlur, OnFocus, OnClick); declare and handle bubbled events; handle an event by using an anonymous function
{% endblockquote %}

* Handling events

```
window.onload = (function(){
	alert('window load');
});

window.addEventListener('load', function(event) {
	alert('window load');
}, false);

var myButton = document.getElementById('button1');
myButton.addEventListener('click', function (event) {
	alert('clicked');
}, false);

$(window).on('click', 'div', function(event) {
	$(this).text = "changed text at " + new Date();
})

```

The third argument to addEventListener indicates whether you want to get the event in the *capture* stage. The capture stage begins at the HTML element and progresses through to the target, then the bubble stage flows from the target back to the HTML element. Using a combination of capture and `Event.stopPropagation` will allow you to grab an event before it reaches its actual target.

Event.preventDefault can be used to stop the default action from being invoked.

## Implement exception handling

{% blockquote %}
Set and respond to error codes; throw an exception; request for null checks; implement try-catch-finally blocks
{% endblockquote %}

To set an error:

`throw new Error(100, "Yes sir");`

Internet Explorer will treat the first argument as error number and second as description. Other browsers may support only a message.

You can get global errors

```
window.addEventListener('error', function(e) {
	console.log(e);
}, false);
```

Try/catch:

```
try {
	// do stuff
}
catch (e) {
	console.log(e.name);
	console.log(e.number);
	console.log(e.message);
	console.log(e.description);

	// can check (e instanceof TypeError) etc
}
finally {
	// all done
}

```
## Implement a callback

{% blockquote %}
Receive messages from the HTML5 WebSocket API; use jQuery to make an AJAX call; wire up an event; implement a callback by using anonymous functions; handle the “this” pointer
{% endblockquote %}

To receive messages from the WebSocket API, first create a new WebSocket object using the ws protocol. Attach event handlers 

```
var socket = new WebSocket("ws://my-host.com"); // optional protocols param 2
socket.onopen = function (openEvent) {
	console.log('opened');
};
socket.onmessage = function (messageEvent) {
	console.log(messageEvent.data); // this can be Blob, String (included serialized JSON), or ArrayBuffer
};
// similar callbacks for onerror and onclose

// events will fire after something is sent
socket.send("let's get started");

// in some event handler:
socket.close();
```

Making an AJAX call with jQuery is done as follows:

```
$.ajax(
	'http://my-host.com/rest-endpoint',
	{
		type: 'POST',
		data: {
			val1: 2,	// this will become a query string
			val2: 3		// for POST, should probably JSON.stringify
		},
		success: function (data) {
			// do something with it
		},
		error: function (e) { 
			// error
		}
	});
```

The ajax method returns a Promise interface (jqXhr in this case), so the event handlers can also be hooked up as:

```
	$.ajax(...)
		.done(function(data){})
		.fail(function(error){});
```

The `this` pointer was addressed in other study guide posts.

## Create a web worker process

{% blockquote %}
Start and stop a web worker; pass data to a web worker; configure timeouts and intervals on the web worker; register an event listener for the web worker; limitations of a web worker
{% endblockquote %}

Here is a web worker sample:

```
// in the page HTML

var worker = new Worker('worker.js');
worker.onmessage = function(event) {
	console.log(event.data);
}
worker.postMessage('Hello.');

// and in the worker.js file

self.addEventListener('message', function(event) {
	self.postMessage('post back to the window's listener);
}, false);
```

Other web worker notes:

* Event data can be an object and is sent a serialized copy - modifying the object in one context will not change it in the other
* The `self` keyword is the global context in the worker js file
* There is no DOM, window, or document in the worker script
* The nav, location, XMLHttpRequest, and cache APIs can be accessed