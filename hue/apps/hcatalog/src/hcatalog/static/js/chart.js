function chart(x,y,min,max)
{
	this.x = x;
	this.y = y;
	this.n = y.length;
	var map = {};
	this.formin = [];
	this.seriesData = [[]];
	this.palette = new Rickshaw.Color.Palette( { scheme: 'colorwheel' } );

	this.getData = function(d,i)
	{
		for(var k=0;k<this.n;k++)
		{
			this.seriesData.push([]);
			this.seriesData[k].push({x: i, y: parseFloat(d[this.y[k]])});
			this.formin[i] = parseInt(d[this.y[k]]);	
			
		}
		map[i] = d[this.x];
	}
	

	this.setGraph = function(type,unstack)
	{
		this.graph = new Rickshaw.Graph({
			element: document.getElementById("chart"),
			width: 900,
			height: 350,
			renderer: type,
			unstack: unstack,
			series:
			[{
				color: this.palette.color(),
				data: this.seriesData[0],
				name: this.y[0]
			}]
		});
		
		this.graph.min = Math.min.apply( Math, this.formin ) -1;

		for(var k=1;k<this.n;k++)
		this.graph.series.push({color: this.palette.color() , data: this.seriesData[k], name: this.y[k]});

		this.legend = new Rickshaw.Graph.Legend({
			graph: this.graph,
			element: document.querySelector('#legend')
		});

		this.hoverDetail = new Rickshaw.Graph.HoverDetail( {
			graph: this.graph
		});

		this.yAxis = new Rickshaw.Graph.Axis.Y({
			graph: this.graph,
			orientation: 'left',
			element: document.getElementById('y_axis')
		});
		var format = function(n)
		{
			return map[n];
		}
		this.xAxis = new Rickshaw.Graph.Axis.X( {
			graph: this.graph,
			orientation: 'bottom',
			element: document.getElementById('x_axis'),
			tickFormat:format

		});
		this.yAxis.min = 60;
		this.graph.render();

		this.slider = new Rickshaw.Graph.RangeSlider({
			graph: this.graph,
			element: document.getElementById('slider')
		});
	} 
	
	this.paint = function(csvfile,type,stacked){
	d3.csv(csvfile,function(dataset){dataset.forEach(function(d,i){c.getData(d,i);});c.setGraph(type,stacked);});};
}




