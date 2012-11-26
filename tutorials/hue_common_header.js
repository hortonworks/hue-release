// auto login and anonymous users

function removeCookie() {
    document.cookie = "added=;path=/;expires=Thu, 01-Jan-1970 00:00:01 GMT";
}

function setCookie() {
    document.cookie = "added=1;path=/;";
}

function handleAutoLogin() {
    // change drop-down menu for anonymous user
    username =  document.getElementById("usernameDropdown").getElementsByTagName("a")[0].text.trim();
    var isAnonymous = username == "AnonymousUser";
    if (isAnonymous) {
        var profileRef = document.getElementsByClassName("userProfile")[0];
        profileRef.text = "Create new user";
        profileRef.href="/useradmin/users/new";
    }

    var isAddingUser = document.location.pathname=="/useradmin/users/new";
    if (isAddingUser && isAnonymous) {
        document.getElementById("editForm").onsubmit = function(){
            setCookie();
            return true;
        }

        if ((document.getElementsByClassName("errorlist").length) > 0) {
            // remove cookie (error while creating)
            removeCookie();
        }
    }

    isAddedSuccessfully = $.cookie("added") !== null;
    if (isAddedSuccessfully) {
        removeCookie();
        setTimeout(function(){window.location = "/accounts/logout/"}, 100);
    }

}
