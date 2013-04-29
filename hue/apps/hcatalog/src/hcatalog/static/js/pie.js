function piechart(csvfile,xAxis,yAxis,min,max)
{
var l = yAxis.length;
var n = 0;

var width = 1200,
    height = 250,
    radius = Math.min(width, height) / 2.5;
 
var color = d3.scale.category20c();
color = d3.scale.category20();
//var color = d3.scale.ordinal().range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);
 
var arc = d3.svg.arc()
    .outerRadius(radius - 10)
    .innerRadius(0);

var pie = d3.layout.pie()
    .sort(null)
    .value(function(d) {return d[yAxis[k]]; });
 
var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);
var block = [];

for(k=0;k<l;k++)
{
var h = 0;
/*defining blocks to the each yAxis*/
block[k] = svg.append("g")
    .attr("transform", "translate(" + (radius*2*(k+1)) + ", "+ (h+100) +")");
	block[k].append("text")
	.attr("y",(radius+10) )
	.text(function(d) {return yAxis[k]; });
}
/*adding label to the iframe*/   
var pielabel = d3.select("body")
	.append("span")
	.attr("class","pielabel")
	.html("test");
	
/*button to show legend*/
var showlegend = d3.select("body")
	.append("a")
	.attr("href","#")
	.attr("class","showlegend")
	.html("legend");	
	
/*adding legend*/   
var legend = d3.select("body")
	.append("svg")
	.attr("width", 1500)
	.append("g")
	.attr("class","legend");


   
d3.csv(csvfile, function(error, data) {
	var dt = [];
	min = min?min:0;
	max = max?max:(data.length-1);
	y = new Array();
	for(t = 0;t<l; t++)
	{
		y[t] = 0;
	}
	for(var i = min, j = 0; i <= max; i++,j++)
	{
		dt[j] = data[i];
		for(t = 0;t<l; t++)
		{
			y[t] += parseFloat(dt[j][yAxis[t]]); 
		}
	}
	var i = 0;
	var lg = legend.attr("transform", "translate(50,10)")
	.selectAll("g")
	.data(dt)
	.enter()
	.append("g");
	
	lg.append("rect")
	.attr("rx", 2)
    .attr("ry", 2)
    .attr("x", function(d,i) {return -13+(i%3)*radius*5;} )
    .attr("y", function(d,i) {return 20*parseInt(i/3);})
    .attr("width", 13)
    .attr("height", 13)
	.style("fill", function(d) { return color(d[xAxis]); });
	
	lg.append("text")
	.attr("rx", 2)
    .attr("ry", 2)
    .attr("x", function(d,i){return (i%3)*radius*5;})
    .attr("y", function(d,i) {return 20*parseInt(i/3)+10;})
	.attr("class", function(d) {return d[xAxis]; })
	.text(function(d) {return d[xAxis]; });
	
	for(k=0;k<l;k++)
	{
		var g = block[k].selectAll(".arc")
		.data(pie(dt))
		.enter().append("g")
		.attr("class", "arc");
		//.attr("rel", function(d){ return d.data[xAxis]});
	 
		g.append("path")
		  .attr("d", arc)
		  .attr("rel", function(d) { return d.data[xAxis]+" "+d.data[yAxis[k]]+" "+((d.data[yAxis[k]]/y[k])*100).toFixed(2)+"%"; })
		  .style("fill", function(d) { return color(d.data[xAxis]); });
	}
	 
	 
	var hoverlegend = function(e,obj){
		pielabel.html(obj.find("path").attr("rel")); 
		obj.find("path").css("stroke","#3EA211"); 
		$(".pielabel").css({display:"block",left:e.pageX,top:e.pageY});
	}
	
	var hidehover = function(obj){
		obj.find("path").css("stroke","none"); 
		$(".pielabel").css("display","none");
	}
	/*adding a label to the pie chart*/ 
	$(".arc").mouseover(function(e){
		hoverlegend(e,$(this));
	});
	
	$(".arc").mouseleave(function(){
		hidehover($(this))
	});
	
	$(".showlegend").click(function(){$(".legend").slideToggle()});
});
}