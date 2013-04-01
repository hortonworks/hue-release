$(document).ready(function () {
	  var delay;
      // Initialize CodeMirror editor with a nice html5 canvas demo.

		
      var editor = CodeMirror.fromTextArea(document.getElementById('vis_code'), {
        mode: 'text/html',
        tabMode: 'indent',
        onChange: function() {
        	clearTimeout(delay);
        	delay = setTimeout(updatePreview, 700);
        }
      });

      function updatePreview() {
        var previewFrame = document.getElementById('preview');
        var preview =  previewFrame.contentDocument ||  previewFrame.contentWindow.document;

        preview.open();
        preview.write(editor.getValue());
        preview.close();
      }
	  $('a[href="#visualizations"]').live('click',function(){updatePreview(); editor.refresh();});
      setTimeout(updatePreview, 700);
});