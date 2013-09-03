$(document).ready(function(){

$.ajaxSetup({
    error: function(xhr){$.jHueNotify.error(xhr.statusText);}
});

});
