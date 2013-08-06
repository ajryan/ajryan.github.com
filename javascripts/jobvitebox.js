(function($) {
    "use strict";

    // utility function to get raw JobVite data
    $.extend({
        getJobViteData: function(companyId, jobCallback, errorCallback) {
            var $self = this,

                yqlUrl = "http://query.yahooapis.com/v1/public/yql",
                query = "select * from xml where url='http://www.jobvite.com/CompanyJobs/Xml.aspx?c=" +
                         companyId +
                        "' and itemPath='result.job'",

                ajaxOptions = {
                    url: yqlUrl,
                    dataType: 'jsonp',
                    async: true,
                    data: {
                        q: query,
                        format: 'json',
                        env: 'store://datatables.org/alltableswithkeys',
                        callback: '?'
                    },
                    success: function(json) {
                        if (!json.query || json.query.count < 1 || !json.query.results || !json.query.results.job) {
                            if (errorCallback) {
                                errorCallback("No jobs found for company Id " + companyId)
                            }
                        }
                        else {
                            jobCallback(json.query.results.job);
                        }
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        if (errorCallback) {
                            errorCallback(textStatus);
                        }
                    },
                    timeout: 10000
                };

            $.ajax(ajaxOptions);

            return $self.toReturn;
        }
    });

    // jQuery plugin to display JobVite data
    $.fn.jobViteBox = function(companyId, after) {
        var $this = this;
        return $this.each(function() {
            $this.text('loading...');
            $.getJobViteData(
                companyId,
                function(jobs) {
                    var html = '';
                    $.each(jobs, function(i, job) {
                        if (job.region === 'West')
                        {
                            var description = job.briefdescription || job.description.substring(0, 200);
                            html +=
                                '<div class="jobvite-job">' +
                                    '<span class="jobvite-jobtitle"><a href="' + job['detail-url'] + '" class="jobvite-jobdetaillink">' +  job.title + '</a></span>' +
                                    '<span class="jobvite-joblocation">' + job.location + '</span>' +
                                    '<span class="jobvite-jobdescription">' + description + '</span>' +
                                    '<span class="jobvite-jobapply"><a href="' + job['apply-url'] + '" class="jobvite-jobapplylink">Apply</a></span>' +
                                '</div>';
                        }
                    });
                    
                    $this.html(html);

                    if (after)
                        after();
                },
                function(errorMessage) {
                    $this.html('<div class="jobvite-error">' + errorMessage + '</div>');
                }
            );
        });
    };

})(jQuery);