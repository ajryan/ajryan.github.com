---
layout: post
title: "CSharpreter plugin for Sublime Text"
date: 2012-08-26 22:20
comments: true
categories: [tools, sublime-text, c-sharp]
---

I have been really loving the [Sublime Text](http://www.sublimetext.com/) editor lately. It's quick, featureful, and extensible.

I write a lot of C#, and I often find myself wanting to check the behavior of a certain method or operator. My go-to tool for this has been [SnippetCompiler](http://www.sliver.com/dotnet/SnippetCompiler/), but now I'm trying to eliminate as many reasons for leaving my editor as possible. So, I created a plugin for Sublime Text that is inspired by SnippetCompiler - it takes the selected text and shoves it inside the main routine of a simple C# console app, builds it, and runs it. You can customize the "usings" and the boilerplate code auto-inserted at the end of the `Main` routine (currently prints a short message and reads a key).

You can find the plugin on [GitHub](https://github.com/ajryan/CSharpreter). Details follow.

## Enter the CSharpreter Sublime Text plugin

CSharpreter compiles and executes fragments of C# code. The currently-selected text (or entire contents of the view, if no text is selected) is injected into the body of the Main routine of a C# console application. MSBuild is invoked and the executable is run in a shell window. This plugin has only been tested on Windows, but *may* be compatible with Mono's XBuild.

With the default settings, your code will be injected into a program defined as follows:

```
using System;
using System.Collections.Generic;
using System.Linq;

class Program
{ 
  static void Main(string[] args)
  {
    // YOUR TEXT HERE
    
    Console.WriteLine();
    Console.WriteLine("Press any key to exit...");
    Console.ReadKey();
  }
}
```

## Commands

* CSharpreter: Interpret - Execute the currently-selected text, or with no selected text, the entire contents of the view.
* CSharpreter: Cleanup - Delete the %temp%\CSharpreter folder, where temporary source and binaries are written.

## Settings

In the CSharpreter package folder, edit c_sharpreter.sublime-settings file to modify the defaults.

* msbuild_path - Path to the MSBuild executable
* default_usings - List of namespaces to inject at the top of the source file.
* main_end - List of statements to inject at the end of the Main method.

```
{
	"msbuild_path": "C:/Windows/Microsoft.NET/Framework/v4.0.30319/MSBuild.exe",
	"default_usings":
	[
		"System", "System.Collections.Generic", "System.Linq"
	],
	"main_end":
	[
		"Console.WriteLine();",
		"Console.WriteLine(\"Press any key to exit...\");",
		"Console.ReadKey();"
	]
}
```

## Installation

Clone this repository into your Sublime Text packages folder.

**Windows 7 / Vista and above**

    C:\Users\<username>\AppData\Roaming\Sublime Text 2\Packages

**Windows XP**

    C:\Documents and Settings\<username>\Application Data\Sublime Text 2\Packages
