
$(document).ready(function(){

var pig_editor = CodeMirror.fromTextArea(document.getElementById("id_pig_script"), {
    lineNumbers: true,
    matchBrackets: true,
    indentUnit: 4,
    mode: "text/x-pig",
    onCursorActivity: function() {
        pig_editor.matchHighlight("CodeMirror-matchhighlight");
    },
    extraKeys: {"Ctrl-Space": function(cm) {CodeMirror.simpleHint(cm, CodeMirror.pigHint);  }}
});


});


var python_editor = CodeMirror.fromTextArea(document.getElementById("python_code"), {
    mode: {name: "python",
           version: 2,
           singleLineStringErrors: true},
    lineNumbers: true,
    indentUnit: 4,
    smartIndent: true,
    tabMode: "shift",
    matchBrackets: true,
    mode: "text/x-python",

});
    


$(".inptext").bind(
    'change', function(){
	$('.intolimit').attr('value', $(this).val())
    });
$(".email").bind(
    'change', function(){
	if($(this).attr('checked') == 'checked')
	{$('.intoemail').attr('value', 'checked')}
	else
	{$('.intoemail').attr('value', 'no checked')};
    });
$("#displayText").click(function() {
    var ele = document.getElementById("toggleText");
    var text = document.getElementById("displayText");
    if(ele.style.display == "block") {
        ele.style.display = "none";
    }
    else {
        ele.style.display = "block";
    }
});
$(".udf_register").click(function() {
    $('#id_pig_script').text('REGISTER ' + $(this).attr('value') + '\n' + $('#id_pig_script').val());
    $('.CodeMirror').hide()
    var editor = CodeMirror.fromTextArea(document.getElementById("id_pig_script"), {
        lineNumbers: true,
        matchBrackets: true,
        indentUnit: 4,
        mode: "text/x-pig"
    });
});

$(document).ready(function(){
    $("#pig_helper>li>a").live('click', function(){
        if($(this).data("python"))
            {
                $("#python_textarea").show();
                
                python_editor.refresh();
            }
        var cur_val = pig_editor.getValue();
        if (cur_val) cur_val += "\n";
        pig_editor.setValue(cur_val+$(this).text());
        return false;
    });
    
    $("#pig_script_form").submit(function(){
        pig_editor.save();
        python_editor.save();
        return true;
    });
});
