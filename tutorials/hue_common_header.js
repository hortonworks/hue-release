// auto login and anonymous users
function handleAutoLogin() {
    //
}


if(window.top != window) {
    //we are in frame
    var l = document.location;
    document.createElement("img").src =
            l.protocol + "//" + l.hostname + ":8888" + "/sync/?loc=" +
            escape(document.location.href);
}
