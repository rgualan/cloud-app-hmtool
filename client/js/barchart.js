var margin = {top: 30, right: 70, bottom: 80, left: 50},
width = 1000 - margin.left - margin.right,
height = 400 - margin.top - margin.bottom,
padding = 20;

function colores_google(n) {
	var colores_g = ["#3366cc", "#dc3912", "#ff9900", "#109618", "#990099", "#0099c6", "#dd4477", "#66aa00", "#b82e2e", "#316395", "#994499", "#22aa99", "#aaaa11", "#6633cc", "#e67300", "#8b0707", "#651067", "#329262", "#5574a6", "#3b3eac"];
	return colores_g[n % colores_g.length];
}

var parseDate = d3.time.format("%d/%m/%Y %H:%M").parse;
var formatDate = d3.time.format("%Y/%m/%d");

var	yScale = d3.scale.linear()
	.range([height/2, padding])
	.nice();
var	yScale2 = d3.scale.linear()
	.range([height/2,height-padding])
	.nice();

var x = d3.scale.ordinal()
.rangeRou	ndBands([0, width- margin.left - margin.right], .1);

var xAxis = d3.svg.axis()
	.scale(x)
	.orient("bottom")
	.tickSize(2)
	.ticks(20)
	.tickPadding(10)

var yAxis = d3.svg.axis()
	.scale(yScale)
	.orient("left")
	.tickSize(2)
	.tickPadding(10)
	.ticks(5);
var yAxis2 = d3.svg.axis()
	.scale(yScale2)
	.orient("left")
	.tickSize(2)
	.tickPadding(10)
	.ticks(5);

function make_y_axis1() {        
	return d3.svg.axis()
	.scale(yScale)
	.orient("left")
	.ticks(5)
}
function make_y_axis2() {        
	return d3.svg.axis()
	.scale(yScale2)
	.orient("left")
	.ticks(5)
}

var happyTip = d3.tip()
	.attr('class', 'd3-tip')
	.offset([-10, 0])
	.html(function(d) {
		return "<strong> Date:</strong> " + d.key + "<br />" +"<strong> Happy: </strong>"+ getHappyValue(d.values)+
		"<br />"+"<strong> Total: </strong>"+ (getHappyValue(d.values)+getUnhappyValue(d.values));
	});

var unhappyTip = d3.tip()
	.attr('class', 'd3-tip')
	.offset([-10, 0])
	.html(function(d) {
		return "<strong> Date:</strong> " + d.key + "<br />" +"<strong> Unhappy: </strong>"+ getUnhappyValue(d.values)+
		"<br />"+"<strong> Total: </strong>"+ (getHappyValue(d.values)+getUnhappyValue(d.values));
	});

var svg = d3.select("body")
	.append("svg")
	.attr("width", width + margin.left + margin.right)
	.attr("height", height + margin.top + margin.bottom)
	.attr("transform", "translate(" + 0 + "," + 410 + ")");

				// d3.json('/tweets', function(csv_data) { 
d3.csv("../data/weather_tweets2.csv",function(csv_data){
	csv_data.forEach(function(d){
		d.date = formatDate(parseDate(d.created_at));
		d.date2 = parseDate(d.created_at);
		d.sentimental = (d.weight > 0 ? (d.weight > 5 ? "Happy" : "Happy") : (d.weight < -5 ? "Unhappy" : "Unhappy"));
	});
	console.log(csv_data);
	//create nested data by using date as first key and sentimental as second key
	var nested_data = d3.nest()
		.key(function(d){
			return d.date
		}).sortKeys(d3.ascending)
		.key(function(d){
			return d.sentimental
		})
		.rollup(function(leaves) { return leaves.length; })
		.entries(csv_data);

	console.log(nested_data);

	  //find max value on each sentimental
	var maxY = 0;
	var maxY2 = 0;
	nested_data.forEach(function(d,i) {
		d.values.forEach(function(d,i){
			if (d.key === "Happy") {
				if (d.values > maxY) {
					maxY = d.values;
				};
			}else{
				if (d.values > maxY2) {
					minY2 = d.values;
				};
			};
		})
	});
	  
	if (maxY2<maxY) {
		maxY2 = maxY
	}else{
		maxY = maxY2
	};

	yScale.domain([0,maxY+1]);
	yScale2.domain([0,maxY2+1]);

  	//find tick value for x axis
  	var domain = nested_data.map(function(d) { return d.key; });
  	x.domain(domain);
  	var ticks = domain.filter(function(v, i) { return i % 20 === 0; });
  	xAxis.tickValues(ticks);

  	svg.append("g")
	  	.attr("class", "x axis")
	  	.attr("transform", "translate("+ (padding + 30) +"," + (height - padding) + ")")
	  	.call(xAxis)
	  	.selectAll('text')
	  	.style("font-size","14px")
		// .style("text-anchor", "end")
	 	// .style("color", "#333")
	 	// .attr("dx", "-.8em")
	 	// .attr("dy", "-.55em")
		// .attr("transform", "rotate(-90)" );
	//upper y axis
	svg.append('g')
		.attr('class', 'y axis')
		.call(yAxis)
		.attr("transform", "translate(" + (padding + 30) + ",0)");
		//lower y axis
	svg.append('g')
		.attr('class', 'y axis2')
		.call(yAxis2)
		.attr("transform", "translate(" + (padding + 30) + ",0)")
		.append("text")
		.attr("transform", "rotate(-90)")
		.attr("y", -margin.left)
		.attr("dy", ".71em")
		.style("text-anchor", "end")
		.text("Tweet Count");

	//grid for upper y axis
	svg.append("g")         
		.attr("class", "grid y1")
		.call(make_y_axis1()
			.tickSize(-width+margin.left+margin.right , 0, 0)
			.tickFormat("")
			)
		.attr("transform", "translate("  + (padding + 30) + ",0)");

	//grid for lower y axis
	svg.append("g")         
		.attr("class", "grid y2")
		.call(make_y_axis2()
			.tickSize(-width+margin.left+margin.right , 0, 0)
			.tickFormat("")
			)
		.attr("transform", "translate("  + (padding + 30) + ",0)");

		//create upper bar(happy)
	svg.selectAll("bar")
		.data(nested_data)
		.enter().append("rect")
		.style("fill", colores_google(0))
		.attr("x", function(d) { return x(d.key); })
		.attr("width", x.rangeBand())
		.attr("y", function(d) {
			return yScale(getHappyValue(d.values))
		})
		.attr("height", function(d) { return height/2 - yScale(getHappyValue(d.values)); })
		.attr("transform", "translate(" + (padding+30) + ","+(-0)+")")
		.on('mouseover',happyTip.show)
		.on('mouseout', happyTip.hide);

	svg.call(happyTip);

		//create lower bar(unhappy)
	svg.selectAll("bar")
		.data(nested_data)
		.enter().append("rect")
		.style("fill", colores_google(1))
		.attr("x", function(d) { return x(d.key); })
		.attr("width", x.rangeBand())
		.attr("y", function(d) {
			return height/2+getUnhappyValue(d.values) -1;
		})
		.attr("height", function(d) { 
			return yScale2(getUnhappyValue(d.values)) - height/2; })
		.attr("transform", "translate(" + (padding + 30) + ","+(-0)+")")
		.on('mouseover',unhappyTip.show)
		.on('mouseout', unhappyTip.hide);

	svg.call(unhappyTip);

    //create legend
    var legend_array = ["Happy","Unhappy"]
    var legend = svg.selectAll(".legend")
	    .data(legend_array.slice())
	    .enter().append("g")
	    .attr("class", "legend")
	    .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

    legend.append("rect")
	    .attr("x", width +5)
	    .attr("width", 18)
	    .attr("height", 18)
	    .style("fill", function(d,i) { return colores_google(i);});

    legend.append("text")
	    .attr("x", width)
	    .attr("y", 9)
	    .attr("dy", ".35em")
	    .style("text-anchor", "end")
	    .style("font-size","14px")
	    .text(function(d) { return d; });
});

function getHappyValue(valueArray){
	var returnValue = 0;
	for (var i = valueArray.length - 1; i >= 0; i--) {
		if (valueArray[i].key === "Happy") {
			returnValue = valueArray[i].values;
		};
	};
	return returnValue;
}

function getUnhappyValue(valueArray){
	var returnValue = 0;
	for (var i = valueArray.length - 1; i >= 0; i--) {
		if (valueArray[i].key === "Unhappy") {
			returnValue = valueArray[i].values;
		};
	};
	return returnValue;
}