function chart(x,y,min,max)
{
	x = x;
	y = y;
	n = y.length;
	map = {};
	formin = [];
	seriesData = [[]];
	palette = new Rickshaw.Color.Palette( { scheme: 'colorwheel' } );
	val = [];
	graphwidth = 900;
	var locked = false,
		section = 100,
		density = 1;

	getData = function(d,i)
	{
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
		difarr = [];
		$.each($(d3.select('#slider').node()).find('a'),function (i,el) {
			difarr[i] = parseInt(el.style.left);
		});
		section = difarr[1]-difarr[0];
		density = formin.length/graphwidth;
		return (parseInt((density/100)*section)==0)?1:parseInt((density/100)*section);
	}

	setGraph = function(type,unstack)
	{
		graph = new Rickshaw.Graph({
			element: document.getElementById("chart"),
			width: graphwidth,
			height: 350,
			renderer: type,
			unstack: unstack,
			series:
			[{
				color: palette.color(),
				data: seriesData[0],
				name: y[0]
			}]
		});
		
		graph.min = Math.min.apply(Math,formin);

		for(var k=1;k<n;k++)
		graph.series.push({color: palette.color() , data: seriesData[k], name: y[k]});

		legend = new Rickshaw.Graph.Legend({
			graph: graph,
			element: document.querySelector('#legend')
		});
		
		shelving = new Rickshaw.Graph.Behavior.Series.Toggle({
			graph: graph,
			legend: legend
		});

		hoverDetail = new Rickshaw.Graph.HoverDetail( {
			graph: graph
		});

		yAxis = new Rickshaw.Graph.Axis.Y({
			graph: graph,
			orientation: 'left',
			element: document.getElementById('y_axis')
		});
		
		var format = function(n)
		{
			return map[n];
		}
		
		xAxis = new Rickshaw.Graph.Axis.X( {
			graph: graph,
			orientation: 'bottom',
			element: document.getElementById('x_axis'),
			tickFormat:format

		});

		scale = new Rickshaw.Graph.Smoother({graph:graph});

		slider = new Rickshaw.Graph.RangeSlider({
			graph: graph,
			element: document.getElementById('slider')
		});

		graph.render();

		scale.setScale(this.getScale());

		graph.onUpdate(function() {
			if (!locked){
				locked = true;
				setTimeout(function() {
					scale.setScale(this.getScale());
					locked = false;
				},100)
			}
		});
	}

	this.redraw = function (type, unstack) {
		if (typeof graph == 'undefined'){
			return false;
		};
		graph.configure({
			renderer: type,
			unstack: unstack
		});
		graph.render();
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




