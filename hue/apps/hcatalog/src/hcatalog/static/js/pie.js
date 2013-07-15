function piechart(csvfile,xAxis,yAxis,num)
{
(num>4)?num=4:((num>2)?num=2:num=1.2);
var l = yAxis.length;
var n = 0;

var width = 1200,
    height = 600/num,
    radius = Math.min(width, height) / 2.2 ;
 
var color = d3.scale.category20c();
 
 
var arc = d3.svg.arc()
    .outerRadius(radius - 10)
    .innerRadius(0);

var pie = d3.layout.pie()
    .sort(null)
    .value(function(d) {return (isNaN(d[yAxis[k]]))?0:(d[yAxis[k]]); });
 
var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);
var block = [];

for(k=0;k<l;k++)
{
/*defining blocks to the each yAxis*/
block[k] = svg.append("g")
    .attr("transform", "translate(" + (radius*2*(k+0.5)) + ","+radius+")");
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
	.append("div")
	.attr("class","show_legend_wrap")
	
	showlegend
	.append("input")
	.attr("type","checkbox")
	.attr("checked",true)
	.attr("class","showlegend")
	showlegend
	.append("span")
	.html("legend");	
	 
/*adding legend*/   
var legend = d3.select("body").append("div").attr("class","legend");

$('.spin').show();
d3.csv(csvfile, function(error, data) {
	$('.spin').hide();
	var dt = [];
	min = 0;
	max = (data.length-1);
	var collen = parseInt(max/4)+1;
	$('.legend_wrap').css("height",(max/3)*24);
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
			var temp = isNaN(dt[j][yAxis[t]])?0:parseFloat(dt[j][yAxis[t]])
			y[t] += temp; 
		}
		
	}
	var lg = legend.append("table").selectAll("td").data(dt).enter().append("td");
	for(k=0;k<collen;k++)
	$("table>td:eq(0),table>td:eq(1),table>td:eq(2),table>td:eq(3)").wrapAll("<tr></tr>");
	
	lg.append("div")
	.style({"display":"inline-block",
			"background-color":function(d) {return color(d[xAxis]);},
			"width":"13px",
			"height":"13px"
			});
	
	lg.append("span")
	.attr("class", function(d) {return d[xAxis]; })
	.style({"font-size":function(d){ return "8pt"},
			"width":"13px",
			"height":"13px"
			})
	.html(function(d) {return d[xAxis]; });
	
	for(k=0;k<l;k++)
	{
		var g = block[k].selectAll(".arc")
		.data(pie(dt))
		.enter().append("g")
		.attr("class", "arc");
	 
		g.append("path")
		  .attr("d", arc)
		  .attr("rel", function(d) {return d.data[xAxis]+" "+d.data[yAxis[k]]+" "+((d.data[yAxis[k]]/y[k])*100).toFixed(3)+"%"; })
		  .style("fill", function(d) { return color(d.data[xAxis]); });
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
	$(".arc").mouseover(function(e){
		hoverlegend(e,$(this));
	});
	
	$(".arc").mouseleave(function(){
		hidehover($(this))
	});
	
	$(".showlegend").click(function(){$(".legend").toggle()});
});
}