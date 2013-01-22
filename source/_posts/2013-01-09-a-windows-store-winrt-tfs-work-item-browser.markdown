---
layout: post
title: "A Windows Store (WinRT) TFS Work Item Browser"
date: 2013-01-09 09:09
comments: true
categories: [development, tfs, winrt]
published: false
---

It's time to dive into Windows Store application development. I've developed several tools for the TFS (Team Foundation Server) ecosystem, so I thought an appropriate first project that will intersect my existing skill set would be a TFS Work Item browser.<!--more-->

## The Plan

The app will be a simple work item browser. After entering your TFS server connection information, you'll be presented with a list of Team Projects. Select a Team Project and browse through Work Items. This will allow me to explore navigation, paging, presentation, and other new idioms in the WinRT platform.

There is an interesting wrinkle here: the TFS API client assemblies are not usable from WinRT. A brief attempt at hitting the TFS ASMX services directly proved too frustrating to waste time on - after all, the goal is to push my Windows Store app skills. This led me to the decision to host a TFS proxy on [AppHarbor](http://appharbor.com) that would provide a simple ASP.NET Web API endpoint for retrieving Work Items, which should be simple to access from WinRT

## Implementation

## Web API Proxy

I have an existing service hosted on AppHarbor, so I cracked open the solution and added two new Web API controllers named `ProjectsController`  and `WorkItemsController`. Along the way, I am using the handy [Postman](https://chrome.google.com/webstore/detail/postman-rest-client/fdmmgilgnpjigdojojpjoooidkmcomcm) REST Client extension for Chrome to hit my service endpoints as I build them out. Fiddler or curl would be just as effective.

### TFS Connection

The first thing required when querying TFS is a connection - this requires a TFS URI, username and password. Both of my controllers will require a connection, so I will compose this dependency. To avoid cluttering all of the API calls with the TFS connection information, I will implement an action filter that leverages the HTTP Basic Authorization standard to collect the TFS URI, username, and password. It will then provide a TFS Connection in the current HttpContext.

My ActionFilterAttribute delegates the Authorization header to a UserDataPrincipal (IPrincipal) that handles the Authorization header. If no principal is returned, or if connecting to TFS with the given conneciton information fails, an HTTP 401 Unauthorized is returned. When a connection issue occurs, the specific reason for failure is provided in the response content.

```
public class TfsBasicAuthenticationAttribute : ActionFilterAttribute
{
    public override void OnActionExecuting(HttpActionContext actionContext)
    {
        var userDataPrincipal = UserDataPrincipal.InitFromHeaders(actionContext.Request.Headers);

        if (userDataPrincipal == null)
        {
            SetUnauthorizedResponse(actionContext);
            return;
        }

        try
        {
            var configUri = new Uri(userDataPrincipal.TfsUrl);
            var tfsConfigServer = new TfsConfigurationServer(configUri, userDataPrincipal.GetCredentialsProvider());
            tfsConfigServer.EnsureAuthenticated();
            tfsConfigServer.Authenticate();

            HttpContext.Current.Items["TFS_CONFIG_SERVER"] = tfsConfigServer;
        }
        catch (Exception ex)
        {
            if (ex is UriFormatException || ex is WebException || ex is TeamFoundationServiceUnavailableException)
            {
                SetUnauthorizedResponse(actionContext, ex.Message);
                return;
            }
            throw;
        }

        HttpContext.Current.User = userDataPrincipal;

        base.OnActionExecuting(actionContext);
    }

    private static void SetUnauthorizedResponse(HttpActionContext actionContext, string message = null)
    {
        string messageValue = message ?? "Authorization (Basic) and TfsUrl headers are required.";
        actionContext.Response = actionContext.Request.CreateResponse(HttpStatusCode.Unauthorized, new { Message = messageValue });
    }
}
```

The `UserDataPrincipal` class above implements `IPrincipal` and in its `InitFromHeaders` method, extracts the username, password, and TFS URL from the HTTP headers. The username and password are retrieved from the HTTP Authorization header using the Basic Authentication standard, and the TFS URL is expected in a separate HTTP header named TfsUrl. Upon authorization with the TFS Configuration Server, its instance is stored in the current HTTP context.

### Retrieving the Team Projects list

After applying the `TfsBasicAuthorization` attribute to our ProjectsController, we have access to the TfsConfigurationServer for retrieving information about Team Projects on the server. These are retrieved by retrieving the CatalogNode for children with resource type ProjectCollection. We then iterate the Team Project Collections and return a list of our `TeamProjectInfo` data transfer object for each child Team Project for which the authorized user has Work Item read rights.

```
[TfsBasicAuthentication]
public class ProjectsController : ApiController
{
    // GET api/projects
    public IEnumerable<TeamProjectInfo> Get()
    {
        var configServer = (TfsConfigurationServer) HttpContext.Current.Items["TFS_CONFIG_SERVER"];
        var collections = configServer.CatalogNode.QueryChildren(
            new Guid[] { CatalogResourceTypes.ProjectCollection }, false, CatalogQueryOptions.None);

        var projects = new List<TeamProjectInfo>();
        foreach (var collectionNode in collections)
        {
            var collectionId = new Guid(collectionNode.Resource.Properties["InstanceId"]);
            var collection = configServer.GetTeamProjectCollection(collectionId);
            var workItemStore = collection.GetService<WorkItemStore>();
            foreach (Project project in workItemStore.Projects)
            {
                if (project.HasWorkItemReadRights)
                {
                    var projectInfo = new TeamProjectInfo
                    {
                        Collection = collection.Name,
                        Name = project.Name,
                        Uri = project.Uri.ToString()
                    };
                    projects.Add(projectInfo);
                }
            }
        }

        return projects;
    }
}
```

### Displaying the Team Projects list

Now that we have a proxy capable of returning a list of accessible Team Projects, it's time to get started on the Windows Store app. I began with the JavaScript Split View project template. This provides a data.js file with sample data hard-coded inside. The data is in the shape of Groups with Items inside each group. This meshes well with Team Projects containing Work Items.

The first task is to replace the sample Group data with TeamProjectInfo instances retrieved from our proxy. Along the way, I would also like to develop a way to inject the URL of the proxy - I'd prefer to develop against the proxy I'm hosting locally in IIS Express, but have the deployed app communicate with the "production" proxy hosted at AppHarbor.

Making the request

* WinJS.xhr makes projects request with no username/password
* Web API Filter response with WWW-Authenticate
* WinRT prompts for credentials and retries the request
* A Forms auth cookie is returned // TODO: remove this and check if auth is still stored
* Apparently, either WinRT is caching the credentials or the auth cookie is working - clicking a project is not prompting for credentials

Displaying the results

* Modify the data.js template to provide just the projects as a simple list

### Displaying the Work Items list

* Clicking a project invokes the getWorkItems method on the data class
* Fetch the WorkItems

### App settings

Up until now I have hard-coded the TFS URL, but obviously users are going to want to point the app at their own servers. This is accomplished with the WinJS.UI.SettingsFlyout control, which we hook up in the WinJS.Application.onsettings callback:

This is a simple page that allows the user to enter a TFS address.


### Polishing the appearance

### Roadblocks and Solutions

#### Snag 1: Secure XHR against IIS

Here's where I hit my first snag - Windows Store apps require ALL HTTPS server certificates to be trusted. I hit this message when attempting to use WinJS.xhr against my local IIS Express-hosted service:

```
SCRIPT7002: XMLHttpRequest: Network Error 0x800c0019, Security certificate required to access this resource is invalid.
```

I found a helpful [blog post](http://robrich.org/archive/2012/06/04/Moving-to-IIS-Express-and-https.aspx) (see Step 7) that described how to install the IIS Express certificate in the local store so that it is trusted by the Windows Store app. In the deployed environment, this won't be an issue, since AppHarbor supplies an HTTPS certificate from an already-trusted authority.

#### Snag 2: Fiddler with WinRT apps

http://blogs.msdn.com/b/fiddler/archive/2011/12/10/fiddler-windows-8-apps-enable-loopback-network-isolation-exemption.aspx

#### Snag 3: Dynamic content in InnerHTML

http://go.microsoft.com/fwlink/?LinkID=247104

I am dynamically checking for HTML content and setting text or innerHtml appropriately - depending on the version of the TFS Project Template, this may be plain text or HTML.

### Other Tips and Take-aways

* Deploying to and debugging on Surface: http://elybob.wordpress.com/2012/12/19/step-by-step-to-deploying-app-to-surface/

### Future

* Content URIs: handle the vsts content URI for loading an individual work item.