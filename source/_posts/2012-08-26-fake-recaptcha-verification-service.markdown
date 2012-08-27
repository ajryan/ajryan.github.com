---
layout: post
title: "Fake reCAPTCHA Verification Service"
date: 2012-08-26 03:05
comments: true
categories: [asp.net-mvc, testing, recaptcha]
---

When testing a website that uses the reCAPTCHA service, it can be a mighty pain to repeatedly enter the verification code. I created a quick-and-dirty ASP.NET MVC site that "fakes" the Google api-verify.recaptcha.net service to allow quick testing.<!--more-->

## Installation

1. Clone my RecaptchaFake repository from `http://github.com/ajryan/RecaptchaFake`, build it, and serve it at **`http://localhost:80/verify`** using IIS or IIS Express.

2. Edit your hosts file (`c:\windows\system32\drivers\etc\hosts` - run Notepad as Administrator for permission to save the file). Add the following entry:

```
127.0.0.1    api-verify.recaptcha.net
```

## Use

With the site served as described above, simply enter `true` or `false` in the reCAPTCHA challenge textbox and the fake service will reply with the same. Enter something different and the service will fall back on the CaptchaResult appSettings value in Web.config.