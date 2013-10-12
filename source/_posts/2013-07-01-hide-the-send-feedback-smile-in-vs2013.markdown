---
layout: post
title: "Hide the &quot;send feedback&quot; smile in VS2013"
date: 2013-07-01 14:39
comments: true
categories: 
---

Here's a quick tip for those of you who've jumped into the Visual Studio 2013 Preview: hiding the "send feedback" smiley-face button in the upper-right of the window. I find it very distracting, and I know how to find the Connect site if I need to file a bug report. I searched the `HKEY_CURRENT_USER` Registry hive under `Software\Microsoft\VisualStudio\12.0_Config` for "feedback" and found a key named `{F66FBC48-9AE4-41DC-B1AF-0D64F0F54A07}` under `MainWindowFrameControls`. Its default value was "Feedback Button," which sounded like what I was looking for. After backing up the key to disk, I deleted the key and re-started Visual Studio. No more smiley!

Delete `HKEY_CURRENT_USER\Software\Microsoft\VisualStudio\12.0_Config\MainWindowFrameControls\{F66FBC48-9AE4-41DC-B1AF-0D64F0F54A07}`.<!--more-->

{% img /images/vs2013_smiley_reg.png 'VS2013 Feedback registry location' 'VS2013 Feedback registry location' %}