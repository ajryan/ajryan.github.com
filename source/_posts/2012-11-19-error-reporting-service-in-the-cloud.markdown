---
layout: post
title: "Error Reporting Service in the Cloud"
date: 2012-11-19 09:45
comments: true
categories: [asp.net, ravendb, cloud]
---

I just published a release of my open source [TFS Test Steps Editor](http://teststepseditor.codeplex.com) project that can now report application errors to me. To accomplish this, I developed a very simple error reporting service hosted at [AppHarbor](http://appharbor.com/). When an unhandled exception occurs, a dialog appears offering to report the error. When the user confirms, the exception dump is posted to my cloud service which saves it to a database and emails it to me. Below is a rundown of the steps I took to quickly get it up and running.<!--more-->

## Overview

The service is hosted in an ASP.NET MVC 4 application. It has a single `ErrorReportingController` with a a single POST endpoint `Report` that accepts only a string for the error report body. When the API is called, the error report is stored in RavenDB via the RavenHQ cloud service and emailed to me via SendGrid. The great thing is that the only thing deployed with my app is logic - storage and email are all handled by services.

The following sections provide a rough outline of the steps required to get it all working. I consider this spike a "proof of concept," as it has plenty of hard-coded constants and no unit tests (which I would accomplish via injection of the SendGrid dependency and use of the in-memory RavenDB server).

### Set up the required services

1. Sign up for an AppHarbor account and create an application.
2. Set up AppHarbor to build and deploy the solution when it is pushed to GitHub. Note that AppHarbor will automatically detect which project should be deployed, as long as the solution contains only a single Web Application.
3. Add the RavenHQ (for storing error reports) and SendGrid (for emailing error reports) add-ons. Note that this adds entries in the *Configuration variables* section for the RavenDB connection string and SendGrid username and password.

### API Logic

The `ErrorReportingController.Report` method looks like this:

```
[HttpPost]
public ActionResult Report(string errorReport)
{
    SendEmail(errorReport);
    StoreInRaven(errorReport);

    return Json("Successful email.");
}
```

The code for sending an email creates a SendGrid email message and delivers it using the `SendGridMail.Transport.REST` API. The API requires a username and password, which I load from Web.config. AppHarbor automatically pushes these values into Web.config when you deploy, so these values are only stored securely with your AppHarbor account and live as dummy values in source control:

```
private static void SendEmail(string errorReport)
{
    var message = SendGrid.GenerateInstance();
    message.From = new MailAddress("my@email.com");
    message.AddTo("my@email.com");
    message.Subject = "TFS Test Steps Editor Error";
    message.Text = errorReport;

    var username = ConfigurationManager.AppSettings["SENDGRID_USERNAME"];
    var password = ConfigurationManager.AppSettings["SENDGRID_PASSWORD"];
    var restTransport = REST.GetInstance(new NetworkCredential(username, password));

    restTransport.Deliver(message);
}
```

The code for persisting the error report creates an `ErrorReport` instance, opens a RavenDB session, and stores the error report:

```
private static void StoreInRaven(string errorReportText)
{
    var errorReport = new ErrorReport
    {
        ReportedDateTime = DateTime.UtcNow,
        Source = "HTTP Post",
        Text = errorReportText
    };

    using (var session = MvcApplication.Store.OpenSession())
    {
        session.Store(errorReport);
        session.SaveChanges();
    }
}
```

Note the use of `MvcApplication.Store`. This is simply a static property defined on the `MvcApplication` class in `Global.asax.cs` and initialized in `Application_Start`using the Web.config appSettings value automatically set by AppHarbor.

### Hooking unhandled exceptions and sending error reports

The final piece is the actual sending of error reports. TFS Test Steps Editor is a Windows Forms application, so I use the following code in the `Program.Main` method to get access to unhandled exceptions:

```
Application.SetUnhandledExceptionMode(UnhandledExceptionMode.ThrowException);
AppDomain.CurrentDomain.UnhandledException += (sender, unhandledExceptionEventArgs) =>
{
    if (_HandlingThreadEx) return;

    lock (_ExLock)
    {
        if (_HandlingThreadEx) return;
        _HandlingThreadEx = true;

        var reporter = new ExceptionReporter(unhandledExceptionEventArgs.ExceptionObject);
        reporter.ReportException();
    }
};
```

The lock and guard ensures that we don't enter an infinite loop if an exception occurs while sending the error report.

The ExceptionReporter class logs the exception and presents a dialog asking whether the user wants to email an exception report. If the user confirms, my Error Reporting service is called. Here is the relevant snippet. The logBody variable is a string set by flushing the current NLog file and then reading its text:

```
var wrapper = (AsyncTargetWrapper) LogManager.Configuration.FindTargetByName("logFile");
wrapper.Flush(x => { });

var fileTarget = (FileTarget) wrapper.WrappedTarget;
fileTarget.Flush(x => { });
var fileNameLayout = (SimpleLayout) fileTarget.FileName;
var fileName = fileNameLayout.Render(new LogEventInfo()).Replace(@"/", @"\");
string logBody = File.ReadAllText(fileName);

string body = String.Format(
    "Message: {0}\r\n\r\nDump: {1}\r\n\r\nLog Body:\r\n{2}",
    _messageTextBox.Text,
    _detailTextBox.Text,
    logBody);

string bodyEncoded = "errorReport=" + HttpUtility.UrlEncode(body);
var bodyBytes = Encoding.UTF8.GetBytes(bodyEncoded);

var request = WebRequest.Create("http://myservice.apphb.com/ErrorReporting/Report");
request.Method = "POST";
request.ContentType = "application/x-www-form-urlencoded";
request.ContentLength = bodyBytes.Length;

var requestStream = request.GetRequestStream();
requestStream.Write(bodyBytes, 0, bodyBytes.Length);
requestStream.Close();

string responseBody = "";
var response = (HttpWebResponse) request.GetResponse();
using (var responseStream = response.GetResponseStream())
{

    using (var reader = new StreamReader(responseStream, Encoding.UTF8))
    {
        string line;
        while ((line = reader.ReadLine()) != null)
            responseBody += line;
    }
}

if (String.IsNullOrWhiteSpace(responseBody))
    responseBody = "<no response from server>";

MessageBox.Show("Send error report: " + responseBody.Replace("\"", String.Empty));
```

## Conclusion

This was a fun exercise that let me explore the integration of several cloud services while providing some value to my end users. I've already received several error reports that I can turn into tangible improvements in the TFS Test Steps Editor. Making it easy for your users to report errors lets them help each other. There is a class of "annoying but I can get around it" error that often goes unreported, but in aggregate causes a lot of pain.

AppHarbor makes things really easy. While its UI is not as slick or modern as Azure's, I find it more intuitive to use than the Azure Web Sites featured, mostly because there are fewer knobs to twiddle. Obviously Azure provides a lot more out of the box, but for these simple purposes, AppHarbor is a perfect fit. And if you need some of the features that Azure has out-of-box, the AppHarbor add-on ecosystem is quite rich, not to mention the bevy of other cloud services that are easily integrated even without a native add-on.

After implementing this minimal, non-configurable service, I have been inspired to develop a generic, open service that could be used by other developers. Development of that service has begun in [my GitHub repo](http://github.com/ajryan/ErrorGun) and is being tested at [http://errorgun.apphb.com](http://errorgun.apphb.com).