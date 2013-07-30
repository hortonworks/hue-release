function chart(xarg,yarg,numchart) {

	var csvdata;

	x_name = xarg;
	y_array = yarg;
	numchart = numchart;

	paintgraph = function (type,stacked) {
		if (csvdata.length > 0) {
			if ($.inArray(type,['area', 'bar', 'line', 'scatterplot'])>-1) {
				setGraph(type,stacked);
			} else {
				piechart(x_name,y_array,numchart)
			}
		}
	}

	sortGraph = function (axis, dir) {
		if (!axis) return false;
		csvdata.sort(function (a, b){
		  var av = (a[axis].toLowerCase()=='null')?0:parseInt(a[axis])
		  var bv = (b[axis].toLowerCase()=='null')?0:parseInt(b[axis])
		  if (dir) {
		  	res = ((av < bv) ? -1 : ((av > bv) ? 1 : 0));
		  } else {
		  	res = ((av > bv) ? -1 : ((av < bv) ? 1 : 0));
		  }
		  return res;
		});
	}

	setGraph = function(type,unstack) {

		var n = y_array.length,
			map = {},
			seriesData = [],
			section = 100,
			density = 1,
			graphwidth = 900,
			palette = new Rickshaw.Color.Palette( { scheme: 'colorwheel' } ),
			graphSeries = [], 
			locked = false;

		getData = function (csvdata) {
			seriesData = [];
			map = {};
			for(var k=0;k<n;k++) {
				seriesData.push([]);
			}
			csvdata.forEach(function(d,i) {
				var val=0;
				for(var k=0;k<n;k++)
				{
					val = (isNaN(parseInt(d[y_array[k]])))?0:parseInt(d[y_array[k]]);
					seriesData[k].push({x: i, y: val});
				}
				map[i] = d[x_name];
			});
		}

		getScale = function(){
			section = parseInt(d3.select('#slider .ui-slider-range').node().style.width);
			density = csvdata.length/graphwidth;
			if ((scl = parseInt(density/100*section))==0) scl=1;
			return scl;
		}
		
		format = function(n){
			return map[n];
		}
		
		getData(csvdata);

		for (var k=0;k<n;k++) 
			graphSeries.push({color: palette.color() , data: seriesData[k], name: y_array[k]});

		graph = new Rickshaw.Graph({
			element: document.getElementById("chart"),
			width: graphwidth,
			height: 350,
			renderer: type,
			unstack: unstack,
			series: graphSeries
		});


		legend = new Rickshaw.Graph.Legend({graph: graph, element: document.querySelector('#legend')});
		shelving = new Rickshaw.Graph.Behavior.Series.Toggle({graph: graph, legend: legend});
		hoverDetail = new Rickshaw.Graph.HoverDetail({
			graph: graph,
			formatter: function(series, x, y) {
				var swatch = '<span class="detail_swatch" style="background-color: ' + series.color + '"></span>';
				var xelement = '<span class="xelement">'+x_name+': ' + format(x); + '</span>';
				var yelement = '<span class="yelement">'+series.name + ": " + parseInt(y)  +'</span>'
				var content = swatch + yelement +  '<br>' + xelement;
				return content;
			}});
		scale = new Rickshaw.Graph.Smoother({graph:graph});
		slider = new Rickshaw.Graph.RangeSlider({graph: graph, element: document.getElementById("slider")});

		xAxis = new Rickshaw.Graph.Axis.X({
			graph: graph,
			orientation: 'bottom',
			element: document.getElementById('x_axis'),
			tickFormat:format
		});
		yAxis = new Rickshaw.Graph.Axis.Y({
			graph: graph,
			orientation: 'left',
			element: document.getElementById('y_axis')
		});

		graph.onUpdate(function() {
			if (!locked){
				locked = true;
				setTimeout(function() {
					scale.setScale(this.getScale());
					locked = false;
				},100)
			}
		});

		graph.render();
	}



	piechart = function(x_pie,y_pie,num) {
		(num>4)?num=4:((num>2)?num=2:num=1.2);
		var l = y_pie.length,
			n = 0,
			width = 1200,
		    height = 600/num,
		    radius = Math.min(width, height) / 2.2,
			color = d3.scale.category20c();
			arc = d3.svg.arc().outerRadius(radius - 10).innerRadius(0),
			pie = d3.layout.pie().sort(null).value(function(d){return (isNaN(d[y_pie[k]]))?0:(d[y_pie[k]]);}),
			svg = d3.select(".pie_warp").append("svg").attr("width", width).attr("height", height),
			block = [];
		for(k=0;k<l;k++) {
			/*defining blocks to the each y_pie*/
			block[k] = svg.append("g").attr("transform", "translate(" + (radius*2*(k+0.5)) + ","+radius+")"); 
			block[k].append("text").attr("y",(radius+10) ).text(function(d) {return y_pie[k];});
		} 
		/*adding label to the iframe*/   
		var pielabel = d3.select(".pie_warp").append("span").attr("class","pielabel").html("test");
		/*button to show legend*/
		var showlegend = d3.select(".pie_warp").append("div").attr("class","show_legend_wrap");
			showlegend.append("input").attr("type","checkbox").attr("checked",true).attr("class","showlegend");
			showlegend.append("span").html("legend");
		/*adding legend*/   
		var legend = d3.select(".pie_warp").append("div").attr("class","legend");
		/*build pie*/
		var dt = [];
		min = 0;
		max = (csvdata.length-1);
		var collen = parseInt(max/4)+1;
		$('.legend_wrap').css("height",(max/3)*24);
		j = new Array();
		for(t = 0;t<l; t++) {
			j[t] = 0;
		}
		for(var i = min, j = 0; i <= max; i++,j++) {
			dt[j] = csvdata[i];
			for(t = 0;t<l; t++) {
				var temp = isNaN(dt[j][y_pie[t]])?0:parseFloat(dt[j][y_pie[t]])
				j[t] += temp; 
			}
		}
		var lg = legend.append("table").selectAll("td").data(dt).enter().append("td");
		for(k=0;k<collen;k++)
			$("table>td:eq(0),table>td:eq(1),table>td:eq(2),table>td:eq(3)").wrapAll("<tr></tr>");
		
		lg.append("div").style({
			"display":"inline-block", 
			"background-color":function(d) {return color(d[x_pie]);}, 
			"width":"13px", 
			"height":"13px"});
		lg.append("span").attr("class", function(d) {return d[x_pie]; })
			.style({"font-size":function(d){ return "8pt"}, "width":"13px", "height":"13px"})
			.html(function(d) {return d[x_pie];});
		
		for(k=0;k<l;k++) {
			var g = block[k].selectAll(".arc").data(pie(dt)).enter().append("g").attr("class", "arc");
			g.append("path").attr("d", arc)
				.attr("rel", function(d) {return d.data[x_pie]+" "+d.data[y_pie[k]]+" "+((d.data[y_pie[k]]/j[k])*100).toFixed(3)+"%"; })
				.style("fill", function(d) { return color(d.data[x_pie]); });
		}
			 
		//functions to show/hide label 
		var hoverlegend = function(e,obj){
			pielabel.html(obj.find("path").attr("rel")); 
			obj.find("path").css("stroke","#3EA211"); 
			$(".pielabel").css({display:"block",left:((e.pageX-$(".pielabel").width()>0)?(e.pageX-$(".pielabel").width()):0),top:e.pageY-$(".pielabel").height()});
		}
			
		var hidehover = function(obj){
			obj.find("path").css("stroke","none"); 
			$(".pielabel").css("display","none");
		}
		/*adding a label to the pie chart*/ 
		$(".arc").mouseover(function(e){hoverlegend(e,$(this));});
		$(".arc").mouseleave(function(){hidehover($(this));});
		$(".showlegend").click(function(){$(".legend").toggle()});
	}

	this.prepareData = function(csvfile,type,stacked){
		$('.spin').show();
		d3.csv(csvfile, function(dataset){
			$('.spin').hide();
			csvdata = dataset;
			if(window.getComputedStyle($('#chart')[0], null)){
				paintgraph(type,stacked);
			}
		});
	}

	this.redraw = function (type, stacked) {
		if (typeof graph == 'undefined') {
			if (csvdata.length>0) {
				paintgraph(type,stacked);
			};
		} else {
			if (type == "pie") {
				$('.chart_wrap').hide();
				$('.pie_warp').show();
				if ($('.pie_warp').children().length == 0) {
					piechart(x_name,y_array,numchart);
				};
			} else {
				$('.pie_warp').hide();
				$('.chart_wrap').show();
				if ($('#chart').children().length == 0) {
					paintgraph(type,stacked);
				} else {
					graph.configure({
						renderer: type,
						unstack: stacked
					});
					graph.render();
				}
			}
		}
	}

	this.resort = function (axis, dir,type,stacked) {
		if (!axis) return false;
		sortGraph(axis, dir);
		$('.chart_wrap').replaceWith('<div class="chart_wrap"><div id="legend"></div><div id="y_axis"></div><div id="chart"></div><div id="slider"></div><div id="x_axis"></div></div>');
		$('.pie_warp').replaceWith('<div class="pie_warp"></div>');
		paintgraph(type,stacked)
	}
}
