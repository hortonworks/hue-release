// auto login and anonymous uses

// change drop-down menu for anonymous user
var isAnonymous = document.getElementById("usernameDropdown").innerText.trim()=="AnonymousUser";
if (isAnonymous) {
    var profileRef = document.getElementsByClassName("userProfile")[0];
    profileRef.innerText = "Create new user";
    profileRef.href="/useradmin/users/new";
}

var isAddingUser = document.location.pathname=="/useradmin/users/new";
if (isAddingUser && isAnonymous) {
    document.getElementById("editForm").onsubmit = function(){
        $.cookie("added","1");
        return true;
    }

    if (document.getElementsByClassName("errorlist").length) > 0 {
        // remove cookie (error while creating)
        document.cookie="added=;expires=Thu, 01 Jan 1970 00:00:01 GMT;"
    }
}

var isAddedSuccessfully = $.cookie("added") !== null;
if (isAddedSuccessfully && isAnonymous) {
    window.location = "/accounts/logout/";
}


// save user steps in tutorials
if(window.top != window) {
    document.createElement("img").src = "http://ec2-75-101-213-8.compute-1.amazonaws.com:8888/sync/?loc=" +
    escape(document.location.href);
}