function pingHiveJob(job_id, on_success_url) {
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
            pingHiveJobTimer = window.setTimeout("pingHiveJob('" + job_id + "', '" + on_success_url + "');", 2000);
        }, "json");
}

function decodeUnicodeCharacters(str) {
    var r = /\\u([\d\w]{4})/gi;
    return unescape(str.replace(r, function (match, grp) {
        return String.fromCharCode(parseInt(grp, 16));
    })
    );
}