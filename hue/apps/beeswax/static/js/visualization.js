$(document).ready(function () {
	var delay;
	var blankcsv = true;
	/* in ie 9 iframe can't work with included js/css files, so we have to input javascript code into iframe's body*/
	var styles = '<style>';
	var lib = '<script>';
	if (jQuery.browser.msie == true) { 
		$.get('/static/ext/js/jquery/jquery-1.8.1.min.js', function(data) {lib += data;});
		$.get('/beeswax/static/js/jquery-ui.min.js', function(data) {lib += data;});
		$.get('/beeswax/static/js/d3.v3.min.js', function(data) {lib += data;});
		$.get('/beeswax/static/js/lib/d3.layout.min.js', function(data) {lib += data;});
		$.get('/beeswax/static/js/lib/rickshaw.min.js', function(data) {lib += data;});
		$.get('/beeswax/static/js/lib/jquery.csv-0.71.min.js', function(data) {lib += data;});
		$.get('/beeswax/static/js/chart.js', function(data) {lib += data;});			
		$.get('/beeswax/static/js/pie.js', function(data) {lib += data;});
		$.get('/beeswax/static/css/detail.css', function(data) {styles += data;});
		$.get('/beeswax/static/css/graph.css', function(data) {styles += data;});
		$.get('/beeswax/static/css/legend.css', function(data) {styles += data;});
		$.get('/beeswax/static/css/chart.css', function(data) {styles += data;});
		$.get('/beeswax/static/css/jquery-ui.css', function(data) {styles += data;});
	}

	/* 
		somehow mozilla change checked type with every page reload
		but 'pie' value on page load is buggy
	*/
	if (jQuery.browser.mozilla){
		$('input[name=type][value=area]').attr('checked',true);
	}

	var previewFrame = document.getElementById('preview');	
	var preview =  previewFrame.contentDocument ||  previewFrame.contentWindow.document;

	var csvfile = $('input[name=visualize_csv]').attr('value');
	/*file conrtaining all needed js files to work with charts*/
	var include = '<script src="/beeswax/static/js/include.js"></script>';

    function updatePreview() {

    	if (blankcsv) { 
    		return false; 
    	}

		/*geting all variables from form to built chart*/
		var type = $('input[name=type]:checked').attr('value');
		var stacked = $('input[name=stacked]:checked').attr('value');
		var xAxis = $('select[name=xAxis]').find(":selected").text();
		var i = 0;
		var n = 0;	  
		var yAxis = [];
		$('input[name=yAxis]:checked').each(function(){
			yAxis[i] ='"'+$(this).attr('value')+'"';
			i++;
		});
		var numcharts = i;
		preview.open();
			var build_chart_file = '<div class="spin">Loading data...<img src="/static/art/spinner.gif" width="16" height="16"></div>';

			if(type == "pie") {
				//including additional library for pie chart
				build_chart_file += '<script src="/beeswax/static/js/pie.js"></script>';
				build_chart_file += "<script>piechart('"+csvfile+"','"+xAxis+"',["+yAxis+"],"+numcharts+");</script>";
			} else {
				build_chart_file += '<script>var c = new chart("'+xAxis+'",['+yAxis+']);</script>';
				build_chart_file += "<script>c.paint('"+csvfile+"','"+type+"',"+stacked+");</script>";
			}
			
			if (jQuery.browser.msie == true) { 
				styles += '</style>';
				lib += '</script><div class="chart_wrap"><div id="legend"></div><div id="y_axis"></div><div id="chart"></div><div id="slider"></div><div id="x_axis"></div></div>';
				preview.write(lib+styles+include+build_chart_file);
			} else {
				preview.write(include+build_chart_file);
			}
		preview.close();
    }

    function redrawPreview () {
    	if (blankcsv) { 
    		return false; 
    	}
		var rdscript = preview.createElement('script');
		rdscript.textContent = "c.redraw('"+$('input[name=type]:checked').attr('value')+"',"+$('input[name=stacked]:checked').attr('value')+");";
		preview.body.removeChild(preview.body.childNodes[preview.body.childNodes.length-1]);
		preview.body.appendChild(rdscript);
    }
	
	/*the code below disables yAxis columns with not number values*/
	var yAxis = [];
	var i=0;
	$('input[name=yAxis]').each(function(){
		yAxis[i] =$(this).attr('value');
		i++;
	});

	$.ajax({
        type: "GET",
        url: csvfile+3,
        dataType: "text",
        success: function(data) {
			var csvdata = $.csv.toObjects(data);
			if (csvdata.length==0) {
				blankcsv = true;
				return false;
			} else {
				blankcsv = false;
			}
			
			for(var j = 0; j < i; j++) {
				for(var m = 0; m < 3; m++) {
					if(isNaN(csvdata[m][yAxis[j]]))	{
						$('input[value='+yAxis[j]+']').attr('disabled',true).attr('checked',false);
					} else {
						$('input[value='+yAxis[j]+']').removeAttr('disabled');
					}
				}
			}
			$('.y_axis input:enabled').attr('checked',true);
			$('.y_axis input[value='+$('select[name=xAxis]').find(":selected").text()+']').attr('checked',false);
			updatePreview();
		}
    });

	$('a[href="#visualizations"]').live('click',function(){
		/*
		  Bug, in mozilla. 
		  Rickshaw can't draw invisible charts, 
		  so let's redraw them when we go to visualizations tab
		*/
		if(jQuery.browser.mozilla){
			preview.open();
			preview.write();
			preview.close();
			updatePreview();
		}
	});
     
	 /*functions for updating chart on changing different features*/
	var needupdate;
	$('input[name=type]').click(function(){
		if($.inArray($(this).val(),['line','scatterplot','pie']) >= 0) {
			$('input[name=stacked]').attr('disabled',true);
			$('input[value=true]').attr('checked',true);
		} else {
			$('input[name=stacked]').attr('disabled',false);
		}
		if ($(this).attr('value')=='pie') {
			updatePreview();
			needupdate = true;
		} else {
			if (!needupdate) {
				redrawPreview();
			} else {
				updatePreview();
			};
			needupdate = false;
		}
	});	
	$('input[name=stacked]').click(function(){redrawPreview()});
	$('input[name=yAxis]').click(function(){updatePreview()});
	$('select[name=xAxis]').change(function(){
		$('.y_axis input:enabled').attr('checked',true);
		$('.y_axis input[value='+$('select[name=xAxis]').find(":selected").text()+']').attr('checked',false);
		updatePreview();
	});
});
