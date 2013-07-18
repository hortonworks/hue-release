function chart(x,y,min,max)
{
	x = x;
	y = y;
	n = y.length;
	map = {};
	formin = [];
	seriesData = [[]];
	palette = new Rickshaw.Color.Palette( { scheme: 'colorwheel' } );
	graphwidth = 900;
	var section = 100,
		density = 1;

	getData = function(d,i) {
		var val = [];
		for(var k=0;k<n;k++)
		{
			seriesData.push([]);
			val = (isNaN(parseInt(d[y[k]])))?0:parseInt(d[y[k]]);
			seriesData[k].push({x: i, y: val});
			formin[i] = val;
		}
		map[i] = d[x];
	}

	getScale = function(){
		section = parseInt(d3.select('#slider .ui-slider-range').node().style.width);
		density = formin.length/graphwidth;
		if ((scl = parseInt(density/100*section))==0) scl=1;
		return scl;
	}

	setGraph = function(type,unstack) {
		var format = function(n){
			return map[n];
		}

		var graphSeries = [], 
			locked = false;

		for (var k=0;k<n;k++) 
			graphSeries.push({color: palette.color() , data: seriesData[k], name: y[k]});

		graph = new Rickshaw.Graph({
			element: document.getElementById("chart"),
			width: graphwidth,
			height: 350,
			renderer: type,
			unstack: unstack,
			min: Math.min.apply(Math,formin),
			series: graphSeries
		});


		legend = new Rickshaw.Graph.Legend({graph: graph, element: document.querySelector('#legend')});
		shelving = new Rickshaw.Graph.Behavior.Series.Toggle({graph: graph, legend: legend});
		hoverDetail = new Rickshaw.Graph.HoverDetail({graph: graph});
		scale = new Rickshaw.Graph.Smoother({graph:graph});
		slider = new Rickshaw.Graph.RangeSlider({graph: graph, element: document.getElementById("slider")});
		yAxis = new Rickshaw.Graph.Axis.Y({
			graph: graph,
			orientation: 'left',
			element: document.getElementById('y_axis')
		});
		xAxis = new Rickshaw.Graph.Axis.X( {
			graph: graph,
			orientation: 'bottom',
			element: document.getElementById('x_axis'),
			tickFormat:format

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

	this.redraw = function (type, stacked) {
		if (typeof graph == 'undefined') {
			return false;
		} else {
			graph.configure({
				renderer: type,
				unstack: stacked
			});
			graph.update();
		}
	}
	
	this.paint = function(csvfile,type,stacked){
		$('.spin').show();
		d3.csv(csvfile,function(dataset){
			$('.spin').hide();
			dataset.forEach(function(d,i){getData(d,i);});
			setGraph(type,stacked);
		});
	};
}
