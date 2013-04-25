function ping_hive_job(job_id, on_success_url) {
    var url = '/hcatalog/ping_hive_job/';
    $.get(url + job_id + "/",
        function (data) {
            if (data.exitValue && data.status) {
                if (data.status.failureInfo && data.status.failureInfo != 'NA') {
                    showMainError(data.status.failureInfo);
                    return;
                }
            }
            if (data.completed || (data.status && data.status.jobComplete)) {
                window.location.replace(on_success_url);
                return;
            }
            pingHiveJobTimer = window.setTimeout("ping_hive_job('" + job_id + "', '" + on_success_url + "');", 2000);
        }, "json");
}