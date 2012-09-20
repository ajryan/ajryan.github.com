---
layout: post
title: "Better checkin comments"
date: 2012-09-20 09:39
comments: true
categories: [development, source control]
---
Good source control checkin (commit) comments can be a major time-saver. It's important to remember that your checkin comments have a large audience and a long lifetime.<!--more-->

I rely on email alerts to get a quick overview of the work accomplished by our offshore team overnight. I want to get a feel for the volume of work accomplished and to identify any risky changes that should be reviewed right away. Quality comments make the difference between a glance through subject lines versus opening diffs to understand the nature of the changes.

The other activity greatly affected by comment quality is browsing source control history to locate the origin of a change. When I see a long list of "updated," "fixed," "changes," I know I'm in for an arduous hunt.

## Terrible comments:

* Updated
* Changed
* Fixed
* Updates
* Checkin

Terrible comments don't explain anything at all. Obviously you updated, changed, or fixed something. And you *really* obviously checked in!

## Bad comments:

* Updated MyClass
* Fixed Bug 5598
* Changes to authentication

Bad commenters tend to explain where or why they made changes, but not both. The "how" is usually completely missing.

## Good comments:

* Bug 5598 - locking to fix race condition on settings initialization in MyClass
* User Story 3355 - implement Save in Widget class

Good comments have two to three components:

1. Why - The reason the change was made, e.g. the Bug or Story number.
2. Where - The location of the change, usually a class or module name.
3. How - Required for Bug fixes. Explain the way the change solves the Bug.