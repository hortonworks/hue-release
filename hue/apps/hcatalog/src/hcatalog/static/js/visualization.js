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
			
			$.get('/hcatalog/static/js/pie.js', function(data) {
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
     /* var editor = CodeMirror.fromTextArea(document.getElementById('vis_code'), {
        mode: 'text/html',
        tabMode: 'indent',
        onChange: function() {
        	clearTimeout(delay);
        	delay = setTimeout(updatePreview, 700);
        }
      });
	editor.refresh();*/

	  
      function updatePreview() {
	    var previewFrame = document.getElementById('preview');	
		var preview =  previewFrame.contentDocument ||  previewFrame.contentWindow.document;
		var type = $('input[name=type]:checked').attr('value');
		var stacked = $('input[name=stacked]:checked').attr('value');
		var xAxis = $('select[name=xAxis]').find(":selected").text();
		var yAxis = [];
		var i = 0;
		var n = 0;
		$('input[name=yAxis]:checked').each(function(){
			yAxis[i] ='"'+$(this).attr('value')+'"';
			i++;
		});
		var csvfile = $('input[name=csv]').attr('value');
			if(type=='pie')
			{
				$('select[name=minlimit]').attr('disabled',false);
				$('select[name=maxlimit]').attr('disabled',false);
			}
			else
			{
				$('select[name=minlimit]').attr('disabled',true);
				$('select[name=maxlimit]').attr('disabled',true);
			}
		
		preview.open();

			var build_chart_file = '';
			var include = '<script src="/hcatalog/static/js/include.js"></script>';
			if(type=="pie")
			{
				var min = $('select[name=minlimit]').find(":selected").text();
				var max = $('select[name=maxlimit]').find(":selected").text();
				build_chart_file += '<script src="/hcatalog/static/js/pie.js"></script>';
				build_chart_file += "<script>piechart('"+csvfile+"','"+xAxis+"',["+yAxis+"],'"+min+"','"+max+"');</script>";
	/*			if (!$('select.pielimits').hasClass('g')){
				 $.ajax({
					type: "GET",
					url: csvfile,
					success: function(data) 
					{ 
						var data = $.csv.toObjects(data);
						n = data.length;
						alert(n);
							for(i=0; i<n; i++) 
							{
								$('.pielimits').addClass('g').append('<option value="'+i+'">'+i+'</option>');
							}
							$('.pielimits:eq(1)>option:eq('+(n-1)+')').attr('selected',true);
					}
				 });
				 }*/

			}
			else
			{
				build_chart_file += '<script>var c = new chart("'+xAxis+'",['+yAxis+']);</script>';
				build_chart_file += "<script>c.paint('"+csvfile+"','"+type+"',"+stacked+");</script>";
			}
			
			if (jQuery.browser.msie == true) { 
			styles += '</style>';
			lib += '</script><div class="chart_wrap"><div id="y_axis"></div><div id="chart"></div><div id="slider"></div><div id="x_axis"></div><div id="legend"></div></div>';
			preview.write(lib+styles+include+build_chart_file);
			}
			else
			{
				preview.write(include+build_chart_file);
			}
		
		preview.close();
      }
	  
	  $('a[href="#visualizations"]').live('click',function(){/*editor.refresh();*/if(jQuery.browser.mozilla){preview.open(); preview.write();preview.close(); updatePreview();}});
      setTimeout(updatePreview, 700);
	  
	  
		$('input[name=type]').click(function(){
			if(($(this).attr('value')=='line') || ($(this).attr('value')=='scatterplot')||($(this).attr('value')=='pie'))
			{
				$('input[name=stacked]').attr('disabled',true);
				$('input[value=true]').attr('checked',true);
			}
			else
			{
				$('input[name=stacked]').attr('disabled',false);
			}
			updatePreview()
		});
		$('input[name=stacked]').click(function(){updatePreview()});
		$('input[name=yAxis]').click(function(){updatePreview()});
		$('select[name=xAxis]').change(function(){
			$('input[name=yAxis]').attr('disabled',false);
			$('input[value='+$('select[name=xAxis]').find(":selected").text()+']').attr('disabled',true).attr('checked',false);
			updatePreview();
		});
		$('select[name=minlimit]').change(function(){updatePreview()});
		$('select[name=maxlimit]').change(function(){updatePreview()});
});