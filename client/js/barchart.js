function queryTweetsData(cb){
    $.getJSON("/tweets", function(dataJson) { 
        //console.log(dataJson);
        if (dataJson.length === 0){
            console.log("No data returned!");
        }
        cb(dataJson);
    });
}

$(document).ready(function() {
	function createBarChart(data){
		var margin = {top: 30, right: 70, bottom: 80, left: 50},
			width = 1000 - margin.left - margin.right,
			height = 400 - margin.top - margin.bottom,
			padding = 20;

		function colores_google(n) {
			var colores_g = ["#3366cc", "#dc3912", "#ff9900", "#109618", 
				"#990099", "#0099c6", "#dd4477", "#66aa00", "#b82e2e", "#316395",
				"#994499", "#22aa99", "#aaaa11", "#6633cc", "#e67300", "#8b0707",
				"#651067", "#329262", "#5574a6", "#3b3eac"];
			return colores_g[n % colores_g.length];
		}

		//get value from Positive key
		function getPositiveValue(valueArray){
			var returnValue = 0;
			for (var i = valueArray.length - 1; i >= 0; i--) {
				if (valueArray[i].key === "Positive") {
					returnValue = valueArray[i].values;
				}
			}
			return returnValue;
		}

		//get value from Negative key
		function getNegativeValue(valueArray){
			var returnValue = 0;
			for (var i = valueArray.length - 1; i >= 0; i--) {
				if (valueArray[i].key === "Negative") {
					returnValue = valueArray[i].values;
				}
			}
			return returnValue;
		}

		var parseDate = d3.time.format("%Y-%m-%d %H:%M:%S").parse;
		var formatDate = d3.time.format("%Y-%m-%d");

		var	yScale = d3.scale.linear()
			.range([height/2, padding])
			.nice();
		var	yScale2 = d3.scale.linear()
			.range([height/2,height-padding])
			.nice();

		var x = d3.scale.ordinal()
			.rangeRoundBands([0, width- margin.left - margin.right], .1);

		var xAxis = d3.svg.axis()
			.scale(x)
			.orient("bottom")
			.ticks(20)
			.tickPadding(10);

		var yAxis = d3.svg.axis()
			.scale(yScale)
			.orient("left")
			.tickPadding(10)
			.ticks(5)
		    .tickFormat(d3.format("d"));
		var yAxis2 = d3.svg.axis()
			.scale(yScale2)
			.orient("left")
			.tickPadding(10)
			.ticks(5)
		    .tickFormat(d3.format("d"));

		//function for create grid on upper y axis
		function make_y_axis_upper() {        
			return d3.svg.axis()
			.scale(yScale)
			.orient("left")
			.ticks(5);
		}
		//function for create grid on lower y axis
		function make_y_axis_lower() {        
			return d3.svg.axis()
			.scale(yScale2)
			.orient("left")
			.ticks(5);
		}

		var positiveTip = d3.tip()
			.attr('class', 'd3-tip')
			.offset([-10, 0])
			.html(function(d) {
				return "<strong> Date:</strong> " + d.key + "<br />" +"<strong> Positive: </strong>"+ getPositiveValue(d.values)+
				"<br />"+"<strong> Total: </strong>"+ (getPositiveValue(d.values)+getNegativeValue(d.values));
			});

		var negativeTip = d3.tip()
			.attr('class', 'd3-tip')
			.offset([-10, 0])
			.html(function(d) {
				return "<strong> Date:</strong> " + d.key + "<br />" +"<strong> Negative: </strong>"+ getNegativeValue(d.values)+
				"<br />"+"<strong> Total: </strong>"+ (getPositiveValue(d.values)+getNegativeValue(d.values));
			});

		var svg = d3.select("#barChart")
			.append("svg")
			.attr("width", width + margin.left + margin.right)
			.attr("height", height + margin.top + margin.bottom)
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


		data.forEach(function(d){
			d.date = formatDate(parseDate(d.date));
			d.date2 = parseDate(d.date);
			d.sentimental = (d.weight > 0 ? "Positive" : (d.weight < 0 ? "Negative" : "Nautual")); //sentiment
		});
		//console.log(data);
		//create nested data by using date as first key and sentimental as second key
		var nested_data = d3.nest()
			.key(function(d){
				return d.date;
			}).sortKeys(d3.ascending)
			.key(function(d){
				return d.sentimental;
			})
			.rollup(function(leaves) { return leaves.length; })
			.entries(data);

		//console.log(nested_data);

		//find max value on each polarity
		var maxYUpper = 0;
		var maxYLower = 0;
		nested_data.forEach(function(d,i) {
			d.values.forEach(function(d,i){
				if (d.key === "Positive") {
					if (d.values > maxYUpper) {
						maxYUpper = d.values;
					}
				}else{
					if (d.values > maxYLower) {
						maxYLower = d.values;
					}
				}
			});
		});
		 
		var maxY = 0;
		if (maxYLower < maxYUpper) {
			maxY = maxYUpper;
		}else{
			maxY = maxYLower;
		}
		maxY = maxY+Math.ceil(maxY*0.1)
		// set y-axis domain
		yScale.domain([0,maxY]);
		yScale2.domain([0,maxY]);

	  	//find and assign  tick value for x axis
	  	var domain = nested_data.map(function(d) { return d.key; });
	  	x.domain(domain);
	  	if (nested_data.length > 10) {
		  	var ticks = domain.filter(function(v, i) { return i % 4 === 0; });
		  	xAxis.tickValues(ticks);
	  	}
	  	
	  	//create x-axis
	  	svg.append("g")
		  	.attr("class", "axis x")
		  	.attr("transform", "translate("+ (padding + 30) +"," + (height - padding) + ")")
		  	.call(xAxis)
		  	.selectAll('text');
		//create upper y axis
		svg.append('g')
			.attr('class', 'axis y')
			.call(yAxis)
			.attr("transform", "translate(" + (padding + 30) + ",0)");
		//create lower y axis
		svg.append('g')
			.attr('class', 'axis y')
			.call(yAxis2)
			.attr("transform", "translate(" + (padding + 30) + ",0)")
			.append("text")
			.attr("transform", "rotate(-90)")
			.attr("y", -margin.left)
			.attr("dy", ".71em")
			.style("text-anchor", "end")
			.text("Tweet Count");

		//create grid for upper y axis
		svg.append("g")         
			.attr("class", "grid y1")
			.call(make_y_axis_upper()
				.tickSize(-width+margin.left+margin.right , 0, 0)
				.tickFormat("")
				)
			.attr("transform", "translate("  + (padding + 30) + ",0)");

		//create grid for lower y axis
		svg.append("g")         
			.attr("class", "grid y2")
			.call(make_y_axis_lower()
				.tickSize(-width+margin.left+margin.right , 0, 0)
				.tickFormat("")
				)
			.attr("transform", "translate("  + (padding + 30) + ",0)");

		//create upper bar(positive)
		svg.selectAll("bar")
			.data(nested_data)
			.enter().append("rect")
			.style("fill", colores_google(0))
			.attr("x", function(d) { return x(d.key); })
			.attr("width", x.rangeBand())
			.attr("y", function(d) {
				return yScale(getPositiveValue(d.values));
			})
			.attr("height", function(d) { return height/2 - yScale(getPositiveValue(d.values)); })
			.attr("transform", "translate(" + (padding+30) + ","+(-0)+")")
			.on('mouseover',positiveTip.show)
			.on('mouseout', positiveTip.hide);

		svg.call(positiveTip);

		//create lower bar(negative)
		svg.selectAll("bar")
			.data(nested_data)
			.enter().append("rect")
			.style("fill", colores_google(1))
			.attr("x", function(d) { return x(d.key); })
			.attr("width", x.rangeBand())
			.attr("y", function(d) {
				return height/2+getNegativeValue(d.values) - getNegativeValue(d.values);
			})
			.attr("height", function(d) { 
				return yScale2(getNegativeValue(d.values)) - height/2; })
			.attr("transform", "translate(" + (padding + 30) + ","+(-0)+")")
			.on('mouseover',negativeTip.show)
			.on('mouseout', negativeTip.hide);

		svg.call(negativeTip);

	    //create legend
	    var legend_array = ["Positive","Negative"];
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
		    .text(function(d) { return d; });
	}
	queryTweetsData(createBarChart);
});