function getCookie(c_name) {
  var i,x,y,ARRcookies=document.cookie.split(";");
  for (i=0;i<ARRcookies.length;i++)
  {
    x=ARRcookies[i].substr(0,ARRcookies[i].indexOf("="));
    y=ARRcookies[i].substr(ARRcookies[i].indexOf("=")+1);
    x=x.replace(/^\s+|\s+$/g,"");
    if (x==c_name)
      {
      return unescape(y);
      }
    }
}

old_sid = getCookie("sessionid")
function check_cookies() {
    new_sid = getCookie("sessionid")
    if (old_sid != new_sid) {
        top.location.reload()
    }
}

setInterval(check_cookies, 1000);