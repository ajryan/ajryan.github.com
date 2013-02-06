---
layout: post
title: "A Windows Store (WinRT) TFS Work Item Browser"
date: 2013-02-04 13:55
comments: true
categories: [development, tfs, winrt]
published: true
---

It's time to dive into Windows Store application development. I've developed several tools for the Team Foundation Server (TFS) ecosystem, so I think an appropriate first project that will intersect my existing skill set would be a TFS Work Item browser.<!--more-->

## The Plan

{% img right /images/tfsworkitems_start_icon.png 'TFS Work Items start screen icon' 'TFS Work Items start screen icon' %}

The app will be a simple work item browser. After entering your TFS server connection information, you'll be presented with a list of Team Projects. Select a Team Project and browse through Work Items. This will allow me to explore navigation, paging, presentation, and other new idioms in the WinRT platform.

There is an interesting wrinkle here: the TFS API client assemblies are not usable from WinRT. A brief attempt at hitting the TFS ASMX services directly proved too frustrating to waste time on - after all, the goal is to push my Windows Store app skills. This led me to the decision to host a TFS proxy on [AppHarbor](http://appharbor.com) that would provide a simple ASP.NET Web API endpoint for retrieving Work Items, which should be simple to access from WinRT. Another option for proxying to TFS could have been the [OData Service for Team Foundation Server](http://blogs.msdn.com/b/briankel/archive/2013/01/07/odata-service-for-team-foundation-server-v2.aspx), except that it is configured to connect only to a single server. I want my app's users to be able to connect an arbitrary TFS server, which would require them to set up the OData service themselves. I opted instead to stand up a small service that allows connection to any TFS server and provides just enough functions for my app.

You can find the source for the [TfsWorkItems](http://github.com/ajryan/TfsWorkItems) work item browser and [TfsProxy](http://github.com/ajryan/TfsProxy) API proxy at my [Github profile](http://github.com/ajryan).

The app itself is available for testing in this [ZIP archive](/assets/TfsWorkItems_1.0.0.0_AnyCPU_Test.zip). Extract, and then run the `Add-AppDevPackage.ps1` PowerShell script to install the app.

## Web API Proxy

As described above, in order to get to the TFS data from WinRT, I will stand up a simple Web API service with methods for retrieving Team Projects and Work Items. I created a Web API project and added controllers named `ProjectsController` and `WorkItemsController`. Along the way, I am using the handy [Postman](https://chrome.google.com/webstore/detail/postman-rest-client/fdmmgilgnpjigdojojpjoooidkmcomcm) REST Client extension for Chrome to hit my service methods as I build them out. Fiddler or curl would be just as effective.

### TFS Connection

The first thing I need is a connection to TFS - this requires a TFS URI, username, and password. Both of my controllers will require a connection, so I will compose this dependency to avoid cluttering all of the API calls with the TFS connection information. This will be implemented via an action filter that provides a TFS Connection in the current HttpContext.

My `TfsBasicAuthenticationAttribute` action filter passes the request headers to a `UserDataPrincipal` (`IPrincipal`) that provides a factory method named `InitFromHeaders`. This method handles the parsing of the connection information from the request headers. If no principal is returned, or if connecting to TFS with the given connection information fails, an HTTP 401 Unauthorized response is returned. When a connection issue occurs, the specific reason for failure is provided in the response content.

{% codeblock TfsBasicAuthenticationAttribute lang:csharp %}

public class TfsBasicAuthenticationAttribute : ActionFilterAttribute
{
    public override void OnActionExecuting(HttpActionContext actionContext)
    {
        var userDataPrincipal = HttpContext.Current.User as UserDataPrincipal;
        if (userDataPrincipal == null)
        {
            userDataPrincipal = UserDataPrincipal.InitFromHeaders(actionContext.Request.Headers);
        }

        if (userDataPrincipal == null)
        {
            SetUnauthorizedResponse(actionContext);
            return;
        }

        try
        {
            var configUri = new Uri(userDataPrincipal.TfsUrl);

            var provider = userDataPrincipal.GetCredentialsProvider();
            var tfsConfigServer = new TfsConfigurationServer(configUri, provider.GetCredentials(null, null), provider);

            tfsConfigServer.EnsureAuthenticated();

            HttpContext.Current.Items["TFS_CONFIG_SERVER"] = tfsConfigServer;
        }
        catch (TeamFoundationServerUnauthorizedException ex)
        {
            SetUnauthorizedResponse(actionContext, ex.Message);
            return;
        }

        HttpContext.Current.User = userDataPrincipal;

        base.OnActionExecuting(actionContext);
    }

    private void SetUnauthorizedResponse(HttpActionContext actionContext, string message = null)
    {
        string messageValue = message ?? "Authorization (Basic) and TfsUrl headers are required.";
        actionContext.Response = actionContext.Request.CreateResponse(HttpStatusCode.Unauthorized, new { Message = messageValue });

        string tfsUrl = actionContext.Request.Headers.GetTfsUrl();
        if (!String.IsNullOrWhiteSpace(tfsUrl))
        {
            actionContext.Response.Headers.Add(
                "WWW-Authenticate", 
                String.Format("Basic realm=\"{0}\"", tfsUrl));
        }
    }
}

{% endcodeblock %}

{% blockquote %}

Note that in the SetUnauthorizedResponse method, I am adding the WWW-Authenticate header with the realm set to the TFS URL. Responding with a combination of HTTP 401 and this header is the standard for negotiating Basic Authentication. The WinJS.xhr wrapper for XMLHttpRequest handles this negotiation by automatically prompting for username and password in a modal popup, and then re-issuing the request with the Authorization header correctly encoded for Basic Authentication.

{% endblockquote %}

The `UserDataPrincipal` class used here implements `IPrincipal` and in its `InitFromHeaders` method, extracts the username, password, and TFS URL from the HTTP headers. The username and password are retrieved from the HTTP Authorization header using the Basic Authentication standard, and the TFS URL is expected in a separate HTTP header named TfsUrl. Upon authenticating with the TFS Configuration Server, its instance is stored in the current HTTP context. The `UserDataPrincipal` class also supplies an `ICredentialsProvider` to the `TfsConfigurationServer` constructor, which is the interface for providing the domain credentials.

### Retrieving the Team Projects list

After applying the `TfsBasicAuthorization` attribute to the `ProjectsController`, I have access to the `TfsConfigurationServer` for retrieving information about Team Projects on the server. The highest level of organization within Team Foundation Server is a "Project Collection" that contains one or more Team Projects. Project Collections are accessed by by querying the configuration server's `CatalogNode` for children with resource type `ProjectCollection`. For each Team Project Collection node, I get its `WorkItemStore` service and iterate its `Projects` collection looking for Team Projects where the authorized user has Work Item read rights. This method returns a list of `TeamProjectInfo` data transfer objects. Note that for each Team Project, I am including a list of the available Work Item Types. This will be leveraged for filtering in the app.

{% codeblock ProjectsController lang:csharp %}

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
                        CollectionName = collectionName,
                        CollectionId = collectionId.ToString(),
                        ProjectName = project.Name,
                        ProjectUri = project.Uri.ToString(),
                        WorkItemTypes = project.WorkItemTypes
                            .Cast<WorkItemType>()
                            .Select(wit => wit.Name)
                            .OrderBy(name => name)
                            .ToList()
                    };
                    projects.Add(projectInfo);
                }
            }
        }

        return projects;
    }
}
{% endcodeblock %}

### Retrieving a Work Items list

When the app user selects a Team Project, we want to display a list of Work Items in the project. This is implemented in the `WorkItemsController` on the Web API proxy service. The `Get` method requires the `collectionId` and `projectName` parameters, and returns a page of 10 work items, in the form of a `WorkItemInfo` data transfer object. The optional `page` parameter allows retrieving a particular page of work items, and the optional `workItemType` parameter allows filtering by work item type (e.g. Bug, Requirement, Task, etc).

{% codeblock WorkItemsController lang:csharp %}
[TfsBasicAuthentication]
public class WorkItemsController : ApiController
{
    // GET api/workitems
    public IEnumerable<WorkItemInfo> Get(string collectionId, string projectName, int page = 0, string workItemType = "All")
    {
        if (String.IsNullOrWhiteSpace(collectionId) || String.IsNullOrWhiteSpace(projectName))
        {
            throw new HttpResponseException(
                new HttpResponseMessage(HttpStatusCode.NotFound) { Content = new StringContent("collectionUri and projectName are required") });
        }

        var configServer = (TfsConfigurationServer)HttpContext.Current.Items["TFS_CONFIG_SERVER"];
        var collection = configServer.GetTeamProjectCollection(new Guid(collectionId));

        var workItemStore = collection.GetService<WorkItemStore>();
        var wiql = String.Format("Select * From WorkItems Where [System.TeamProject] = '{0}'", projectName);
        if (!String.IsNullOrWhiteSpace(workItemType) &&
            !workItemType.Equals("All", StringComparison.OrdinalIgnoreCase))
        {
            wiql += String.Format(" AND [System.WorkItemType] = '{0}'", workItemType);
        }
        var query = workItemStore.Query(wiql);

        return query
            .Cast<WorkItem>()
            .Skip(10 * page)
            .Take(10)
            .Select(WorkItemInfoBuilder.Build)
            .ToArray();
    }
}
{% endcodeblock %}

The `WorkItemStore.Query` method returns a late-bound `IEnumerable` that allows the use of `Skip` and `Take` for efficient paging. The `WorkItemInfoBuilder` helper class takes care of mapping the TFS `WorkItem` class to the `WorkItemInfo` data transfer object.

## The Windows Store App

{% img left /images/split_app.png 'Split App template' 'Split App template' %}

Now that we have a proxy that makes the TFS API accessible from WinRT, it's time to get started on the Windows Store app. I began with the JavaScript Split App project template. This template provides a basic app frame and bootstrapper (default.html / default.js), navigation handler (navigator.js), data provider (data.js), and provides two screens for interaction: an "items" screen and a "split" screen. The data provider is set up to return static, hard-coded sample data.

The home screen of the app is the "items" screen, which would be more appropriately named "groups." The items screen presents a list of top-level item groups as horizontally-scrolling tiles. Selecting an item group tile navigates to the "split" screen that presents a list-detail view of the individual items within the selected group. The overall shape of this data and navigation scheme (groups containing items) meshes well with Team Projects containing lists of Work Items. I plan to break one more level out of the hierarchy: Team Projects are found within Team Project Collections (as seen above), so rather than the simple grid view on the main screen, I will use a grouped grid view with the team projects grouped by collection.

### Connection Preferences

Before I can replace the sample data with live TFS data, I need to be able to provide the proxy with the URL of the TFS server. This is going to be a per-user setting, so I will add a settings command for displaying a flyout where the user can set the TFS URL. The user will invoke the Charms sidebar, and then click Settings to see my app's settings, which will include this custom command. Adding a settings command is accomplished by handling the `WinJS.Application.onsettings` event as seen here:

{% codeblock Settings command lang:csharp %}
WinJS.Application.onsettings = function (e) {
    e.detail.applicationcommands = { "connection": { title: "Connection", href: "/pages/preferences/preferences.html" } };
    WinJS.UI.SettingsFlyout.populateSettings(e);
};
{% endcodeblock %}

This adds a command to the settings flyout labeled "Connection" which will navigate to a flyout with the provided href. The markup for a flyout is simple - a top-level `div` inside the body for the flyout itself, with a back button and a label/input for the TFS URL.

{% codeblock Preferences.html lang:html %}
<div data-win-control="WinJS.UI.SettingsFlyout"
     id="programmaticInvocationSettingsFlyout" 
     aria-label="App Settings Flyout"
     data-win-options="{settingsCommandId:'connection',width:'narrow'}">
    
    <div class="win-ui-dark win-header">
        <button type="button" onclick="WinJS.UI.SettingsFlyout.show()" class="win-backbutton"></button>
        <div class="win-label">Preferences</div>
    </div>
    <div class="win-content">
        <div class="win-settings-section">
            <h3>TFS Connection</h3>
            <p>Enter the address of your TFS Server. It must be publicly accessible on the internet for the TFS Work Items proxy service to access it. Usually this URL will end in /tfs.</p>
            <label>TFS URL</label>
            <input type="url" id="tfsUrl" aria-label="Enter TFS URL" placeholder="https://account.visualstudio.com/tfs" />
        </div>
    </div>
</div>
{% endcodeblock %}

In the JavaScript code-behind for the flyout, I added event listeners for `blur` and `keyup` on the `tfsUrl` input. The standard for Windows Store apps is for settings to take effect immediately, so when the user focuses away from the input or presses the Enter key, I will immediately store and react to the change.

### Getting the Team Projects list

Now that the user has a way to specify the TFS URL, I can finally go fetch some live data. Windows Store apps are expected to launch as instantly as possible, so blocking while loading data at startup is not an option &mdash; control needs to be returned to the UI thread right away. In the `data.js` data provider, I will set up the `Data` namespace with an empty Team Projects list, then make an asynchronous call to fetch the Team Projects list from the proxy. The UI will bind to the team projects list so that once the asynchronous call returns and the list is filled, the UI binding will trigger it to be updated with the populated list.

Here you can see the definition of the Data namespace. Note that the `Windows.ApplicationModel.DesignMode.designModeEnabled` property is checked to determine if the code is being invoked in design mode. This is to allow the use of sample data when editing the views in Blend, but to fetch real data from the network when the app is actually running. When in design mode, `Data.dataService` is set to the static `SampleDataService` class; when not in design mode, `Data.dataService` is set to an instance of the `WebDataService` class. The call to `Data.loadProjects()` will return immediately to avoid blocking app startup, as you will see in the next code sample.

<a id="data"></a>
{% codeblock Data.js initialization lang:js %}
var
        projectList = new WinJS.Binding.List(),
        designMode = Windows.ApplicationModel.DesignMode.designModeEnabled,
        webDataService = new WebDataService("https://tfsproxy.apphb.com");

    WinJS.Namespace.define("Data", {
        projects: projectList,
        groupedProjects: projectList.createGrouped(WebDataService.getProjectGroupKey, WebDataService.getProjectGroupData, WebDataService.compareProjectGroups),
        dataService: designMode? SampleDataService : webDataService,
        processingEvent: "processingEvent",
        processingStatus: false,
        processingMessage: "",
        loadProjects: function () {
            this.dataService.getTeamProjects(this.projects);
        },
        raiseProcessing: function (value, message) {
            this.processingStatus = value;
            this.processingMessage = message || "";
            WinJS.Application.queueEvent({ type: Data.processingEvent, processing: value });
        }
    });

    Data.loadProjects();
{% endcodeblock %}

The `WebDataService` class provides access to the proxy for retrieving Team Projects and Work Items. It leverages the `WinJS.xhr` method to make asynchronous HTTP requests to the proxy. Note that if the `Settings.tfsUrl` property is not set, no call to the service is made and the list remains empty.

{% codeblock WebDataService.getTeamProjects lang:js %}
getTeamProjects: function (list) {
    list.dataSource.beginEdits();
    while (list.length > 0) list.pop();

    if (!Settings.tfsUrl) {
        Data.processingMessage = "Please open the Settings charm, select Connection, and enter your TFS server URL.";
        return;
    }

    Data.raiseProcessing(true, "Retrieving Team Projects list...");

    WinJS.xhr({
        type: "GET",
        url: this.apiBaseUrl + "/api/projects",
        headers: { TfsUrl: Settings.tfsUrl }
    })
    .done(
        function (result) {
            Data.raiseProcessing(false);
                var responseJson = JSON.parse(result.responseText);
                responseJson.forEach(function (project) {
                    list.push(project);
                });
                list.dataSource.endEdits();
        }
    );
}
{% endcodeblock %}

{% img right /images/xhr_auth.png 'WinJS.xhr authentication' 'WinJS.xhr authentication' %}

The following sequence occurs when making the request to the proxy:

* WinJS.xhr makes the initial GET request to /api/projects with no authentication information
* The custom Web API ActionFilter responds with HTTP 401 and the WWW-Authenticate header
* WinRT recognizes the Basic auth negotiation, prompts for credentials, and retries the request
* For the remainder of the app session, WinRT remembers the entered credentials and includes them in future requests to the same domain

Once the request is successfully completed, the JSON response is parsed and the `TeamProjectInfo` records are pushed into the list, triggering a data-binding refresh.

### Displaying the Team Projects list

Note in the [Data namespace](#data) above, the `groupedProjects` property is provided. This is a grouped view of the Team Projects, with the Team Project Collection name used as the group key. In the items page, I made some modifications so that Team Projects would be displayed in groups by their collection. I also simplified the item template markup to simply display the Team Project name.

{% codeblock items.html %}
<div class="itemtemplate" data-win-control="WinJS.Binding.Template">
    <div class="item">
        <h4 class="workitem-title" data-win-bind="textContent: ProjectName"></h4>
    </div>
</div>

<div class="itemspage fragment">
    <header aria-label="Header content" role="banner">
        <button class="win-backbutton" aria-label="Back" disabled type="button"></button>
        <h1 class="titlearea win-type-ellipsis">
            <span class="pagetitle">TFS Work Items</span>
        </h1>
    </header>
    <section aria-label="Main content" role="main">
        <div
            class="itemslist win-selectionstylefilled" 
            aria-label="List of groups" 
            data-win-control="WinJS.UI.ListView" 
            data-win-options="{ selectionMode: 'none', layout: {type: WinJS.UI.GridLayout} }">
        </div>
    </section>
</div>
{% endcodeblock %}

There is not much code at all in the codebehind for this page, simply setting up the data binding and hooking the `oniteminvoked` event to trigger navigation to the Work Item list for the selected item. Because the ListView layout type has been set to `WinJS.UI.GridLayout` in the markup, the items in the list are automatically displayed in groups when the `groupDataSource` of the ListView is set.

{% codeblock items.js %}
ui.Pages.define("/pages/items/items.html", {

    ready: function (element, options) {

        var listView = element.querySelector(".itemslist").winControl;
        listView.itemDataSource = Data.groupedProjects.dataSource;
        listView.groupDataSource = Data.groupedProjects.groups.dataSource;
        listView.itemTemplate = element.querySelector(".itemtemplate");
        listView.oniteminvoked = function (args) {
            var project = Data.projects.getAt(args.detail.itemIndex);
            WinJS.Navigation.navigate("/pages/split/split.html", { project: project });
        };
        
        this._initializeLayout(listView, Windows.UI.ViewManagement.ApplicationView.value);
        listView.element.focus();
    },
    // ...
{% endcodeblock %}

So, putting it all together, here's what the app's home screen looks like:

{% img /images/items.png 'Team Projects grouped display' 'Team Projects grouped display' %}

### Getting and Displaying Work Items

Selecting a Team Project on the items screen navigates to the split screen, with the `project` property of the options parameter set to the selected project. This is transformed by the framework into the arguments to the `ready` function of the split page. The split page has a lot more functionality than the items page -- it needs to support:

* Selection of a work item to display its details
* Browsing to the next page of work items (a page of 10 at a time is returned by the proxy)
* Browsing to the preview page of work items
* Filtering the list of work items by type (e.g. Bug, Requirement, Task, etc.)

The `ready` function takes care of binding the App Bar commands, filling the filtering select control with work item types, and initiating the fetch of Work Items from the proxy.

{% codeblock ready in split.js lang:js %}
ready: function (element, options) {
    var self = this;

    self._project = options ? options.project;
    self._itemSelectionIndex = (options && "selectedIndex" in options) ? options.selectedIndex : -1;

    element.querySelector("header[role=banner] .pagetitle").textContent = self._project.ProjectName;

    document.getElementById("cmdPrev").addEventListener("click", self._prevWorkItemPage.bind(this), false);
    document.getElementById("cmdNext").addEventListener("click", self._nextWorkItemPage.bind(this), false);
    document.getElementById("cmdFilter").addEventListener("click", function() {
        var flyOut = document.getElementById("filterFlyout").winControl;
        flyOut.show(this, "top");
    });
    
    // fill the work item type select with the available types and listen for selection
    var workItemTypeSelect = document.getElementById("workItemTypeSelect");
    self._project.WorkItemTypes.forEach(function (workItemType) {
        var option = document.createElement("option");
        option.textContent = workItemType;
        option.value = workItemType;
        workItemTypeSelect.add(option);
    });
    workItemTypeSelect.onchange = function (event) {
        var currentValue = this.value;
        self._pageNumber = 0;
        this._itemSelectionIndex = -1;
        self._workItemTypeFilter = currentValue;
        document.getElementById("appbar").winControl.hide();
        self._getWorkItems();
    };
    
    self._getWorkItems();
}
{% endcodeblock %}

The `_getWorkItems` function is triggered when the view is first loaded, as well as when a different page or filter is requested. It passes the parameters for page number and work item type to the proxy, and then fills the data-bound work item list with the response. The work item list and detail sections are faded out while processing. Code in the `default.js` bootstrapper hooks to the `Data` namespace's processing event and shows an indeterminate progress bar and status message when the event is raised. By fading out the primary sections, we allow the progress bar to be easily seen.

{% codeblock _getWorkItems in split.js lang:js %}
_getWorkItems: function() {
    var self = this;

    // fade list and workitem while loading
    WinJS.UI.Animation.fadeOut([[document.querySelector(".workitem-detail-section")], [document.querySelector(".workitem-list-section")]]);
    
    var listView = document.querySelector(".workitem-list").winControl;

    Data.dataService.getWorkItems(self._project, self._pageNumber, self._workItemTypeFilter).then(function (workItems) {
        self._workItems = workItems;
        
        // Set up the work item ListView.
        listView.itemDataSource = self._workItems.dataSource;
        listView.itemTemplate = document.querySelector(".workitem-template");
        listView.onselectionchanged = self._selectionChanged.bind(self);
        listView.layout = new ui.ListLayout();

        self._updateVisibility();

        if (self._isSingleColumn()) {
            if (self._itemSelectionIndex >= 0) {
                // for single-column detail view, load the article and change page title to Work Item title
                self._loadArticleDetails();
                WinJS.UI.Animation.fadeIn([[document.querySelector(".workitem-detail-section")], [document.querySelector(".workitem-list-section")]]);
            }
        } else {
            listView.selection.set(Math.max(self._itemSelectionIndex, 0));
            WinJS.UI.Animation.fadeIn(document.querySelector(".workitem-list-section"));
        }
    });
    
}
{% endcodeblock %}

Note the use of the `_isSingleColumn` utility function - depending on the orientation or snapped state of the app, the view may be filled with the article details - in that case, we immediately load the current article details after the work items are retrieved; when in full landscape view, we set the selection in the list view knowing that our `_selectionChanged` handler will be triggered for loading the article.

{% img /images/split.png 'Work Items display' 'Work Items display' %}

The markup for the split page provides formatting for the work item list and detail view. It is not heavily modified from the Split App template, although the item images have been removed and additional binding fields have been added for the most important Work Item properties. At the bottom of the display area, a ListView is used to display a generic list of field name-value pairs - this is because work item templates can be heavily customized, and it is not possible to anticipate the names of the fields a user could define.

{% codeblock split.html %}
<!-- Template for Work Item nav list -->
<div class="workitem-template" data-win-control="WinJS.Binding.Template">
    <div class="workitem">
        <div class="workitem-id"><h2 data-win-bind="textContent: Id"></h2></div>
        <div class="workitem-info">
            <h3 class="workitem-title win-type-ellipsis"><span data-win-bind="textContent: WorkItemType"></span>: <span data-win-bind="textContent: Title"></span></h3>
            <h4 class="workitem-state win-type-ellipsis" data-win-bind="textContent: State"></h4>
            <h6 class="workitem-assignedto win-type-ellipsis" data-win-bind="textContent: AssignedTo"></h6>
        </div>
    </div>
</div>

<!-- Template for individual work item fields list -->
<div class="field-template" data-win-control="WinJS.Binding.Template">
    <div class="field-pair">
        <div class="field-name win-type-ellipsis" data-win-bind="textContent: Name"></div>
        <div class="field-value win-type-ellipsis" data-win-bind="textContent: Value"></div>
    </div>
</div>

<!-- The content that will be loaded and displayed. -->
<div class="splitpage fragment">
    <header aria-label="Header content" role="banner">
        <button class="win-backbutton" aria-label="Back" disabled type="button"></button>
        <h1 class="titlearea win-type-ellipsis">
            <span class="pagetitle">Temp title</span>
        </h1>
    </header>
    <div class="workitem-list-section" aria-label="List column">
        <div class="workitem-list win-selectionstylefilled" 
             aria-label="List of this Team Project's Work Items" 
             data-win-control="WinJS.UI.ListView" 
             data-win-options="{itemTemplate:select('.workitem-template'), selectionMode:'single', swipeBehavior:'none', tapBehavior:'toggleSelect'}">
        </div>
    </div>
    <article class="workitem-detail-section" aria-atomic="true" aria-label="Work Item detail column" aria-live="assertive">
        <header>
            <div class="workitem-id"><h2 data-win-bind="textContent: Id"></h2></div>
            <div class="workitem-title"><h2 class="win-type-ellipsis"><span data-win-bind="textContent: WorkItemType"></span>: <span data-win-bind="textContent: Title"></span></h2></div>
            <div class="header-left">
                <h4 class="workitem-subtitle"><span data-win-bind="textContent: State"></span> (<span data-win-bind="textContent: Reason"></span>)</h4>
                <h6 class="workitem-subtitle" data-win-bind="textContent: AssignedTo"></h6>
            </div>
            <div class="header-right">
                <h4 class="workitem-subtitle" data-win-bind="textContent: Area"></h4>
                <h6 class="workitem-subtitle" data-win-bind="textContent: Iteration"></h6>
            </div>
        </header>
        <div class="workitem-description"></div> <!-- content is set in code due to need to convert to static HTML -->
        <div class="workitem-history"></div>
        <div class="workitem-otherfields">
            <div class="workitem-field-list" data-win-control="WinJS.UI.ListView" data-win-options="{selectionMode:'none', swipeBehavior:'none', tapBehavior:'none'}"></div>
        </div>
    </article>
</div>
<div id="appbar" data-win-control="WinJS.UI.AppBar">
    <button data-win-control="WinJS.UI.AppBarCommand" data-win-options="{id:'cmdPrev', label:'Previous Page', icon:'previous', section:'selection'}" type="button"></button>
    <button data-win-control="WinJS.UI.AppBarCommand" data-win-options="{id:'cmdNext', label:'Next Page', icon:'next', section:'selection'}" type="button"></button>
    <button data-win-control="WinJS.UI.AppBarCommand" data-win-options="{id:'cmdFilter', label:'Filter', icon:'filter', section:'selection'}" type="button"></button>
</div>
<div id="filterFlyout" data-win-control="WinJS.UI.Flyout" data-win-options="{anchor:'cmdFilterButton'}">
    <label for="workItemTypeSelect">Work Item Type</label>
    <select id="workItemTypeSelect">
        <option value="All">All</option>
    </select>
</div>
{% endcodeblock %}

The `split.html` markup also provides the App Bar for the page (defining the page and filter commands) as well as the flyout that is displayed when the filter command is invoked. The flyout simply contains a `label` and `select` list that is populated (as seen above) with the work item types available in the current project.

## Wrapping Up

So, there you have it - a (very simple) TFS Work Item browser. This was a great learning exercise: it pushed my JavaScript skills and was a nice tour of some of the common features of the platform. While I'm happy with the insights I've gained into WinRT and with this app as a sample, I think it could take a more dynamic approach to browsing and viewing work items. The work item detail display does not seem to me to conform to the Windows Store design guidelines. I would like to consult with some of my UX colleagues for ideas about how to present the work item details in a way that is natural to the platform.

### Future Plans

Here are some other potential ways to extend the app in the future

* Work Item Queries: returning a list of work items sorted ascending by ID is not very useful - most TFS users access work items using pre-defined work item queries. 
* Content URIs: handle the vsts content URI for loading an individual work item.
* Leverage the Work Item Type definition to determine (and possibly reflect the layout definition of) the important custom work item fields.
* Display the Work Item details in a format more appropriate to a Windows Store app.
* Search, Sharing, and Print contracts.
* Allow simple modification actions, like assignment and state change; or, allow full editing.

### Miscellaneous Tips

I ran into some issues along the way that don't fit right in with the narrative above, but are worth sharing.

#### Tip 1: Secure XHR against IIS

Windows Store apps require all HTTPS server certificates to be trusted. I hit this message when attempting to use `WinJS.xhr` against my local IIS Express-hosted service:

`SCRIPT7002: XMLHttpRequest: Network Error 0x800c0019, Security certificate required to access this resource is invalid.`

I found a helpful [blog post](http://robrich.org/archive/2012/06/04/Moving-to-IIS-Express-and-https.aspx) (see Step 7) that described how to install the IIS Express certificate in the local store so that it is trusted by the Windows Store app. In the deployed environment, this won't be an issue, since AppHarbor supplies an HTTPS certificate from an already-trusted authority.

#### Tip 2: Fiddler with WinRT apps

By default, WinRT security prevents Fiddler from intercepting network traffic from Windows Store apps. This [post](http://blogs.msdn.com/b/fiddler/archive/2011/12/10/fiddler-windows-8-apps-enable-loopback-network-isolation-exemption.aspx) explained how to work around the issue.

#### Tip 3: Dynamic content in InnerHTML

The Description and History work item fields will often contain HTML content. WinRT will throw a security error if you attempt to set the `innerHTML` property of an element to a string with certain attributes set. This [article](http://msdn.microsoft.com/en-us/library/windows/apps/hh849625.aspx) explains techniques for dealing with potentially dangerous content. The particular technique that I used was the `window.toStaticHTML` method for cleaning text before assigning it to an `innerHTML` property.

#### Tip 4: Deploying to and Debugging on Surface

To auto-deploy and test the app on my Microsoft Surface, directly from Visual Studio 2012, I followed the steps provided in this [article](http://elybob.wordpress.com/2012/12/19/step-by-step-to-deploying-app-to-surface/). My colleague Rocky Lhotka also has a good [article](http://www.lhotka.net/weblog/TestingAWinRTAppOnASurfaceRT.aspx) about packaging an app with a PowerShell script to allow distributing an app package for short-term side-loaded testing.
