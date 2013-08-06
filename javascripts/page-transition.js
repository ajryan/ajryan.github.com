// Log function, via html5 boilerplate.
window.log = function() {
  log.history = log.history || [];
  log.history.push(arguments);
  arguments.callee = arguments.callee.caller;  
  if(this.console) console.log( Array.prototype.slice.call(arguments) );
};
(function(b){function c(){}for(var d="assert,count,debug,dir,dirxml,error,exception,group,groupCollapsed,groupEnd,info,log,markTimeline,profile,profileEnd,time,timeEnd,trace,warn".split(","),a;a=d.pop();)b[a]=b[a]||c})(window.console=window.console||{});


var roleName = 'main',
    opts = {
        contentRole: roleName,
        getContentHolder: function() { return $('[role=' + roleName + ']'); },
        // all links with our special transition attribute.
        $navLinks: $('nav a[transition-link]'),
        transitionHandler: function(name, $to, $from, cb) {
            $from.hide(name, { direction: 'left', easing: 'easeOutQuad' }, 350, function() {
                // Transition in the to element
                opts.getContentHolder().append($to);
                $to.show(name, {direction: 'right', easing: 'easeOutQuad'}, 350, function() {
                    // Remove the from element
                    $from.detach();
                    if ($.isFunction(cb)) { cb(); }
                });
            });
        },
        transitioning: false
    },
    pageLoadSettings = {
        type: "get",
        data: undefined,
        reloadPage: false,
        role: roleName,
        showLoadMsg: true,
    },
    loadPage = function(url, options) {
        var deferred = $.Deferred(),
            settings = $.extend({}, pageLoadSettings, options),
            page = null, // The DOM element holder for the fetched page.
            fileUrl = url; // Might want to massage the url in the future.
            
        $.ajax({
            url: fileUrl,
            type: settings.type,
            data: settings.data,
            dataType: "html",
            success: function(html) {
                var all = $('<div />'),
                    contentSelector = '[role=' + settings.role + ']';
                    
                // workaround to allow scripts to execute when included in page divs
                all.get(0).innerHTML = html;
                
                // Find the content in the other page.
                if (!all.has(contentSelector)) {
                    deferred.reject(url, options);
                    return;
                }
                
                page = all.find('[role=' + settings.role + ']').first().contents();

                deferred.resolve(page, fileUrl);
            },
            error: function() {
                deferred.reject(url, options);
            }
        });
        
        return deferred.promise();
    };
    

// If we support css transitions, set our alternate transition handler.
if (Modernizr.csstransitions) {
    log("CSS transitions supported.");
    // animation complete callback
    $.fn.animationComplete = function(callback) {
        if (Modernizr.csstransitions) {
            return $(this).one('webkitAnimationEnd', callback);
        }
        else {
            // defer execution for consistency between webkit/non webkit
            setTimeout(callback, 0);
            return $(this);
        }
    };
    opts.transitionHandler = function(name, $to, $from, cb) {
        $from.addClass('slide out');
        
        $from.animationComplete(function() {
            $from.detach();
            opts.getContentHolder().append($to);
            $to.addClass('slide in');
        });
        $to.animationComplete( function() {
            if($.isFunction(cb)) { cb(); }
        });
    };
}

// Attach click handlers for all links with our special transition attribute.
opts.$navLinks.click(function(e) {
    // Prevent navigation
    e.preventDefault();
    
    // prevent re-entry while processing transition
    if (opts.transitioning===true)
        return;

    opts.transitioning = true;

    // toggle the selected menu item.
    $('nav .selected').toggleClass('selected', 350);
    var that = this;
    setTimeout(function() {
        $(that).parent().addClass('selected', 350);
    }, 360);
    
    var pageUrl = $(this).attr('href');
    log(pageUrl);
    
    loadPage(pageUrl)
        .done(function($newPageContents, url) {
            var $oldContentHolder = opts.getContentHolder().wrapInner('<div class="pageWrap"></div>'),
                $oldContent = $oldContentHolder.children().first(),
                $newContent = $('<div class="newPageWrap"></div>').append($newPageContents),
                transitionName = 'slide';
            
            opts.transitionHandler(
                transitionName,
                $newContent, 
                $oldContent, 
                function() {
                    $newContent.contents().unwrap();
                    opts.transitioning = false;
                });
        })
        .fail(function(url) {
            opts.transitioning = false;
            alert('Error getting page');
        });
});
