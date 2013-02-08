---
layout: post
title: "Updated WinHaste hastebin client"
date: 2013-02-08 13:17
comments: true
categories: [tools, open source]
---

I just pushed a small update to my [WinHaste](https://github.com/ajryan/WinHaste) hastebin client ([binary](http://ajryan-github-downloads.s3.amazonaws.com/WinHaste.exe)). [Hastebin](http://hastebin.com/) is a cool, minimal, login-free alternative to Pastebin. Now, when a command's output is being piped to WinHaste, the output will be echoed to the console. This is especially handy if you are running an interactive command, so you aren't entering values "blind."<!--more-->

WinHaste supports piped or interactive entry - if you enter `WinHaste.exe` with no arguments, it will read user input from the console until an end-of-file `^Z` character is entered. In this mode, Windows already writes user input to the console, so echoing within WinHaste would result in doubling every character typed. I ran across a nice technique in [this StackOverflow answer](http://stackoverflow.com/a/9712392/1042) for checking whether the current input stream is piped or interactive:

{% codeblock lang:csharp %}
private static bool IsInputPiped()
{
    try
    {
        var tmp = Console.KeyAvailable;
        return false;
    }
    catch (InvalidOperationException)
    {
        return true;
    }
}
{% endcodeblock %}

I navigated into the disassembly of the `Console.KeyAvailable` (thanks, ReSharper!) found found the following:

{% codeblock lang:csharp %}
bool r = Win32Native.PeekConsoleInput(ConsoleInputHandle, out ir, 1, out numEventsRead); 
if (!r) { 
    int errorCode = Marshal.GetLastWin32Error();
    if (errorCode == Win32Native.ERROR_INVALID_HANDLE) 
        throw new InvalidOperationException(Environment.GetResourceString("InvalidOperation_ConsoleKeyAvailableOnFile"));
    __Error.WinIOError(errorCode, "stdin");
}
{% endcodeblock %}

So, I could P/Invoke PeekConsoleInput myself, but this works fine for me!