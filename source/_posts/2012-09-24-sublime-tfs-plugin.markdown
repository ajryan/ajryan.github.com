---
layout: post
title: "Sublime TFS plugin"
date: 2012-09-24 09:38
comments: true
categories: [tools, sublime-text, tfs]
---

Here's a nice plugin for Sublime Text: [Sublime TFS](https://bitbucket.org/CDuke/sublime-tfs/wiki/Home), by Denis Kulikov. It provides TFS integration right in the editor.<!--more-->

Sublime TFS will auto-check-out modified files (a must since files in TFS are readonly until checked out), and provides commands for Add, Delete, History, Check in, Check out, Undo, Get latest, and Compare with latest, available when the current file is under version control (except Add, obviously).

I made a small contribution to the project, adding support for the TFS Power Tools "Annotate" feature (commonly known as "blame"). I have one major complaint about the Annotate output from TFPT, though: you can't open a changeset view by clicking a changeset number. I'm considering using the `/noprompt` option and dumping the Annotate output into a Sublime Text buffer, then providing the ability to open a changeset view from the buffer. Sounds like fun!
