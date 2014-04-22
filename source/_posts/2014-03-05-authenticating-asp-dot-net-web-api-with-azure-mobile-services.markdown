---
layout: post
title: "Authenticating ASP.NET Web API with Azure Mobile Services"
date: 2014-03-05 09:56
comments: true
categories: [development, web api, azure mobile services, authentication]
---

Azure Mobile Services provides a really easy way to integrate social login into web, mobile, and desktop applications. At Magenic, we're using it in our client apps for the [Modern Apps Live!](http://modernappslive.com/Events/Las-Vegas-2014/Home.aspx) conference demo application called [MyVote](http://myvotelive.com). The web application and the native mobile clients share a common Web API backend deployed to a Web Role on Azure Cloud Services. For most of the Web API methods, we only want to allow calls from users who have successfully authenticated with Azure Mobile Services. Let's dig into what it takes to develop a Web API authentication handler that verifies claims issued by Azure Mobile Services.<!--more-->

## Scenario ##

This authentication method applies to the following scenario:

* Azure Mobile Services is set up for Social Authentication. See [here](http://azure.microsoft.com/en-us/documentation/articles/mobile-services-html-get-started-users/) for instructions.
* Users authenticate on the client (browser) side using the Azure Mobile Services JavaScript SDK. The latest SDK at the time of this writing is version 1.1.3, and can be found [here](http://ajax.aspnetcdn.com/ajax/mobileservices/MobileServices.Web-1.1.3.min.js).
* You have ASP.NET Web API services that you want to expose only to users who have authenticated with Azure Mobile Services.

Normally we are authenticating users on the same system that issues credentials - think standard ASP.NET membership stuff. In this case, our Web API system needs to trust credentials issued by a third party.

## Method ##

Here is a quick refresher on login with Azure Mobile Services:

{% codeblock ZuMo Authentication lang:javascript %}
var zumoUrl = "https://your-zumo-service.azure-mobile.net";
var zumoKey = "your-zumo-application-key";
var client = new WindowsAzure.MobileServiceClient(zumoUrl, zumoKey);

// options are facebook, twitter, microsoft, or google.
// you must set up each provider in the azure management portal.
client.login("facebook").then(function() {
	alert('login succeeded');
}, function(error) {
	alert(error);
});
{% endcodeblock %}

When a user successfully logs in with Azure Mobile Services, the `client.currentUser` field is set. This in turn exposes a `mobileServiceAuthenticationToken` field, which is a JSON Web Token (JWT). JWT is an [emerging standard](http://tools.ietf.org/html/draft-ietf-oauth-json-web-token-07) for representing authentication information. It is used by many OAuth implementations, including Azure Mobile Services.

In order to verify that users have truly authenticated with Azure Mobile Services, we will rely on a "[shared secret](http://en.wikipedia.org/wiki/Shared_secret)" known only to Azure Mobile Services and to us. The JWT issued to the user is cryptographically signed by Azure Mobile Services using the Master Key unique to our service instance. We have access to this key via the management portal, and we can use it in our Web API code to verify that a JWT was truly issued and signed by our Azure Mobile Services instance.

Here's a quick diagram that sums it up:

 {% img /images/zumo_auth.PNG 'Zumo Auth' 'Zumo Auth' %}

The standard for a client to present a JWT for authentication to a server is to set the request's Authorization header to "Bearer <JWT>" where <JWT> is the actual Base64-encoded JSON Web Token. MyVote is using AngularJS, so I set up an HTTP interceptor to set the header on every request:

{% codeblock AngularJS Authorization Header Interceptor lang:javascript %}
MyVote.App = angular.module('MyVoteApp', ['ngRoute', 'ngResource']);

MyVote.App.factory('zumoAuthInterceptor', function () {
    return {
        request: function (config) {
            if (Globals.zumoUserKey) {
                config.headers['Authorization'] = 'Bearer ' + MyVote.Services.AuthService.zumoUserKey;
            }
            return config;
        }
    };
});

MyVote.App.config([
    '$routeProvider', '$httpProvider',
    function ($routeProvider, $httpProvider) {
        $httpProvider.interceptors.push('zumoAuthInterceptor');
        // -- snip -- other config stuff here -- //
    }
]);
{% endcodeblock %}

On the server side, authentication is implemented in Web API via a delegating handler. The process begins here:

{% codeblock JWT Handler lang:csharp %}
protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
{
    // browser sends OPTIONS requests to check CORS and will not include Authorization header
    // allow these requests to flow through with the response from the CORS handler
    if (request.Method != HttpMethod.Options)
    {
        string token;
        if (TryRetrieveToken(request, out token))
        {
            try
            {
                var jwt = new JsonWebToken(token, new Dictionary<int, string> {{0, _masterKey}});
                jwt.Validate(validateExpiration: true);

                MyVoteAuthentication.SetCurrentPrincipal(new MyVotePrincipal(jwt.Claims.UserId));
            }
            catch (JsonWebTokenException)
            {
            }
        }
    }
    return base.SendAsync(request, cancellationToken);
}
{% endcodeblock %}

In the `SendAsync` override, we attempt to validate the JWT. If it is valid, we call `MyVoteAuthentication.SetCurrentPrincipal` which sets `HttpContext.Current.User`. This allows us to simply add the `[Authorize]` attribute to Web API controllers or actions where we want to require Azure Mobile authentication. Note the `_masterKey` field that is included in the `JsonWebToken` contructor call. This is the Azure Mobile Services Master Key (shared secret) that we trust as the cryptographic signer of valid JWTs.

The relevant bit inside `JsonWebToken` that validates the signature follows:

{% codeblock JsonWebToken.ValidateSignature lang:csharp %}
private void ValidateSignature()
{
    // Derive signing key, Signing key = SHA256(secret + "JWTSig")
    byte[] bytes = _UTF8Encoder.GetBytes(_signatureKey + "JWTSig");
    byte[] signingKey = _Sha256Provider.ComputeHash(bytes);

    // UFT-8 representation of the JWT envelope.claim segment
    byte[] input = _UTF8Encoder.GetBytes(_envelopeTokenSegment + "." + _claimsTokenSegment);

    // calculate an HMAC SHA-256 MAC
    using (var hashProvider = new HMACSHA256(signingKey))
    {
        byte[] myHashValue = hashProvider.ComputeHash(input);
        string base64UrlEncodedHash = Base64UrlEncode(myHashValue);
        if (base64UrlEncodedHash != Signature)
            throw new JsonWebTokenException("Signature does not match.");
    }
}
{% endcodeblock %}

I borrowed liberally from the [Windows Live SDK sample](https://github.com/liveservices/LiveSDK/blob/master/Samples/Asp.net/AuthenticationTokenSample/JsonWebToken.cs) for this. There is one gotcha - the JWT spec indicates that a claims "exp" member should be expressed as a double, but Azure Mobile Services uses an integer.

You can find all of the JWT authentication-related code in the MyVote GitHub repository, in the [MyVote.AppServer.Auth](https://github.com/Magenic/MyVote/tree/master/src/MyVote.AppServer/Auth) namespace.

**WARNING**: Do not expose your Azure Mobile Services Master Key! For example, DON'T put the key in `appSettings` in your Web.config and then host your code on GitHub. You should rely on the secure configuration facility supplied by your hosting environment. If your Web API is hosted in Azure via Web Sites or Cloud Services, you can securely set `appSettings` values from within the management portal.