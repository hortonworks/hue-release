function chart(x,y,min,max)
{
	x = x;
	y = y;
	n = y.length;
	map = {};
	formin = [];
	seriesData = [[]];
	palette = new Rickshaw.Color.Palette( { scheme: 'colorwheel' } );

	getData = function(d,i)
	{
		for(var k=0;k<n;k++)
		{
			seriesData.push([]);
			seriesData[k].push({x: i, y: (isNaN(d[y[k]]))?0:parseInt(d[y[k]])});
			formin[i] = parseInt(d[y[k]]);	
		}
		map[i] = d[x];
	}

	setGraph = function(type,unstack)
	{
		graph = new Rickshaw.Graph({
			element: document.getElementById("chart"),
			width: 900,
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
		
		graph.min = Math.min.apply( Math, formin ) -1;

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

		graph.render();
		
		slider = new Rickshaw.Graph.RangeSlider({
			graph: graph,
			element: document.getElementById('slider')
		});
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




