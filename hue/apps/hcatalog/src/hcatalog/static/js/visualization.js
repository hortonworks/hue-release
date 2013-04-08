$(document).ready(function () {
		var delay;
		var styles = '<style>';
		var lib = '<script>';
		if (jQuery.browser.msie == true) { 
		

			$.get('/static/ext/js/jquery/jquery-1.8.1.min.js', function(data) {
				lib += data;
			});
			$.get('/hcatalog/static/js/jquery-ui.min.js', function(data) {
				lib += data;
			});
			$.get('/hcatalog/static/js/d3.v3.min.js', function(data) {
				lib += data;
			});
			$.get('/hcatalog/static/js/lib/d3.layout.min.js', function(data) {
				lib += data;
			});
			$.get('/hcatalog/static/js/lib/rickshaw.min.js', function(data) {
				lib += data;
			});
			$.get('/hcatalog/static/js/chart.js', function(data) {
				lib += data;
			});

	
			$.get('/hcatalog/static/css/detail.css', function(data) {
				styles += data;
			});
			$.get('/hcatalog/static/css/graph.css', function(data) {
				styles += data;
			});
			$.get('/hcatalog/static/css/legend.css', function(data) {
				styles += data;
			});
			$.get('/hcatalog/static/css/chart.css', function(data) {
				styles += data;
			});
			$.get('/hcatalog/static/css/jquery-ui.css', function(data) {
				styles += data;
			});
		}
	  // Initialize CodeMirror editor with a nice html5 canvas demo.
      var editor = CodeMirror.fromTextArea(document.getElementById('vis_code'), {
        mode: 'text/html',
        tabMode: 'indent',
        onChange: function() {
        	clearTimeout(delay);
        	delay = setTimeout(updatePreview, 700);
        }
      });

	  var previewFrame = document.getElementById('preview');	
	  var preview =  previewFrame.contentDocument ||  previewFrame.contentWindow.document;
      function updatePreview() {
		preview.open();
		if (jQuery.browser.msie == true) { 
			styles += '</style>';
			lib += '</script><div class="chart_wrap"><div id="y_axis"></div><div id="chart"></div><div id="slider"></div><div id="x_axis"></div><div id="legend"></div></div>';
			preview.write(lib+styles+editor.getValue());
		}
		else
		{
			var include = '<script src="/hcatalog/static/js/include.js"></script>';
			preview.write(include+editor.getValue());
		}
		preview.close();
      }
	  $('a[href="#visualizations"]').live('click',function(){  editor.refresh(); });
      setTimeout(updatePreview, 700);
});