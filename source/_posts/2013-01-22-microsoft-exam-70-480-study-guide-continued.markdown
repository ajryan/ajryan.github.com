---
layout: post
title: "Microsoft Exam 70-480 study guide continued: DOM manipulation"
date: 2013-01-22 15:39
comments: true
categories: [study, web]
---

This is a continuation of my study guide for Microsoft Exam 70-480, working toward the Microsoft Certified Solutions Developer (MCSD): Web Applications certification. We are now tackling the **Write code that interacts with UI controls** objective, specifically DOM modification.<!--more-->

## Implement and Manipulate Document Structures and Objects (24%)

### Write code that interacts with UI controls ###

#### Programmatically add and modify HTML elements

In general, the HTML DOM API or jQuery will be used to manipulate the page structure. It is important to understand the underlying native APIs - jQuery makes our code concise and cross-browser compatible, but a knowledge of what is happening under the covers will help you write more efficient jQuery. Moreover, there are times when you can accomplish something simple with the native API without the need to pull down jQuery.

In the following samples, I will give the native implementation, followed by its jQuery equivalent.

* The `document` object is a node that represents the entire HTML document (including the head). Everything in the DOM is a node. It's important to differentiate between nodes and elements: all elements are nodes, but not all nodes are elements. For example, a `div` element may have an `id` attribute - the attribute is a node, but not an element.

* To get a single element by its ID:

```
	document.getElementById('elementId') ==> HTMLElement
	$('#elementId') ==> object ==> jQuery object
```

* To get an array of elements by tag name:

```
	document.getElementsByTagName('div') ==> HTMLCollection / NodeList
	$('div') ==> jQuery[]
```

* To get an array of elements by name (most useful for inputs):

```
	document.getElementsByName('myInput') ==> HTMLCollection / NodeList
	$('[name="myInput"]') ==> jQuery[]
```

* To get an array of elements by CSS class:

```
	document.getElementsByClassName('cool-class') ==> HTMLCollection / NodeList
	$('.cool-class') ==> jQuery[]
```

* To traverse between nodes, once you have a node reference:

```
	var domNode = document.getElementById('elementId');
	// note parentElement can be used but not *all* nodes are elements
	var domParent = domNode.parentNode;
	// note that childNodes may include inter-tag text, children returns only elements
	var domFirstChild = domNode.childNodes[0];
	var domFirstElement = domNode.children[0];

	var jqNode = $('#elementId');
	var jqParent = jqNode.parent();
	var jqFirstChild = jqNode.children()[0];
```

* Important properties of a DOM node:

	* `nodeType`: Integer (enum) representing the type of node. 1 = Element, 2 = Attribute, 3 = Text, 8 = Comment, 9 = Document
	* `nodeName`: Name of the node. For tag elements, the tag name. For text content, #text.
	* `nodeValue`: Value of the node. For elements, null. For text, the text itself, and for attributes, the attribute value.
	* `childNodes`: Collection of children
	* `parentNode`: Parent
	* `firstChild`, `lastChild`, `nextSibling`, `previousSibling`: self-explanatory
	* jQuery equivalents:

```
	var element = $('#container');
	var firstChild = element.children(':first');
	var lastChild = element.children(':last');
	var nextSibling = element.next();
	var previousSibling = element.prev();
```

* Element nodes may have one or more attributes. To access them, the `attributes` member is used. Attributes are not considered children of a node.

* Access all attributes of an element:

```
	var div = document.getElementById('container');
	var attribs = div.attributes;

	// no jQuery equivalent
```

* Get and set the value of a particular attribute:

```
	var div = document.getElementById('container');
	var val = div.attributes['id'].value;
	val = div.getAttribute('id');
	var valNode = div.getAttributeNode('id');
	div.attributes['id'].value = 'newValue';
	div.setAttribute('id', 'newValue');

	var jqDiv = $('#container');
	var jqVal = jqDiv.attr('id');
	jqdiv.attr('id', 'newValue');
```

* Check if an attribute exists:

```
	var hasId = element.hasAttribute('id');
	var jqHasId = (element.attr('id') !== undefined);
```

* Remove attribute:

```
	element.removeAttribute('id');
	element.removeAttributeNode(element.getAttributeNode('id'));

	jqElement.removeAttr('id');
```

Now we have covered accessing and inspecting page elements via the DOM API and jQuery - it's time to delve into modifying the structure of the page: adding, removing, and changing the contents of elements.

* Once you have a node reference, you can change its value. Tag nodes do not usually have values, but their first child will usually be a text node with value equal to the text content.

* To change a tag's inner text:

```
	var par = document.getElementById('paragraph1');
	par.firstChild.nodeValue = 'Changed text';

	var jqPar = $('#paragraph1');
	jqPar.text('Changed text');
```

* To add an element to the DOM tree, you need to create an element, set any required attributes, and then append it to as the last child of an existing node:

```
	var newNode = document.createElement('img');
	newNode.setAttribute('src', 'https://www.google.com/images/srpr/logo3w.png');
	var body = document.getElementsByTagName('body')[0];
	body.appendChild(newNode);

	$('body').append('<img src="https://www.google.com/images/srpr/logo3w.png"/>');
```

* Adding additional inner text to a span, div, or p tag is accomplished as follows. Note that jQuery `append` is equally effective for HTML or text:

```
	var par = document.getElementById('paragraph1');
	par.appendChild(document.createTextNode('Additional paragraph text here'));

	$('#paragraph1').append('Additional paragraph text here')
```

* You can also insert an element as a sibling before an existing node:
```
	var newNode = document.createElement('img');
	newNode.setAttribute('src', 'https://www.google.com/images/srpr/logo3w.png');
	var body = document.getElementsByTagName('body')[0];
	body.insertBefore(newNode, document.getElementById('container'));

	$('container').before('<img src="https://www.google.com/images/srpr/logo3w.png"/>');
	$('body').prepend('img src="https://www.google.com/images/srpr/logo3w.png"/');
```

* Take care to note the differences between `appendChild` and `insertBefore`. A node added with `appendChild` will be the last node contained by the target. Calling `insertBefore` has the signature container.insertBefore(nodeToInsert, nodeThatWillBeAfter) - in this case as well, nodeToInsert will be a child of the target, but it will be the prior sibling to nodeThatWillBeAfter.

* To remove an element from the DOM:

```
	var body = document.getElementsByTagName('body')[0];
	var removedElement = body.removeChild(document.getElementById('container'));

	$('#container').remove();
```

* To replace an existing element:

```
	var body = document.getElementsByTagName('body')[0];
	var newNode = document.createElement('img');
	newNode.setAttribute('src', 'https://www.google.com/images/srpr/logo3w.png');
	var oldNode = document.getElementById('container');
	body.replaceChild(oldNode, newNode);

	$('#container').replaceWith('<img src="https://www.google.com/images/srpr/logo3w.png"/>');
```

* In both the DOM and jQuery, you can move an element by getting a reference to it and then calling one of the above insertion/replacement methods. A node cannot exist at two places in the DOM, so it will automatically be removed from its previous location.

* jQuery in total provides `after`, `before`, `append`, `prepend`, `replaceWith`, `wrap`, `wrapInner`, and `wrapAll` for DOM manipulation - these methods are called on the selector for the existing element(s) with the new content as an argument. Companion methods `insertAfter`, `insertBefore`, `appendTo`, `prependTo`, and `replaceAll` are targeted to the new content with the target selector as an argument. The odd man out is `remove`, which is targeted to a selector for content to be removed.

## 'Til Next Time

That will conclude DOM manipulation. We'll pick up next time with media, canvas, and SVG.