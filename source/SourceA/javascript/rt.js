// Global variables
var PLOT_WINDOW_SIZE = 50;

// Methods
function initLineChart(properties){
	data = properties.data;

	// Set the basic properties of the plot
	// Margins
	var margin = { top: 30, right: 20, bottom: 30, left: 50 };
	var width = 500 - margin.left - margin.right;
	var height = 270 - margin.top - margin.bottom;
	properties.margin = margin;
	properties.width = width;
	properties.height = height;

	// Scales
	var x = d3.time.scale().range([0, width]);
	var y = d3.scale.linear().range([height, 0]);
	x.domain(d3.extent(data, function(d) { return d.date; }));
	y.domain(d3.extent(data, function(d) { return d.value; }));
	properties.x = x;
	properties.y = y;

	// Axes
	var xAxis = d3.svg.axis().scale(x).orient("bottom").ticks(5);
	var yAxis = d3.svg.axis().scale(y).orient("left");
	properties.xAxis = xAxis;
	properties.yAxis = yAxis;

	// Define the line
	var line = d3.svg.line()
	 	//.interpolate("basis")
	    .x(function(d) { return x(d.date); })
	    .y(function(d) { return y(d.value); });
	 properties.line = line;


	// Adds the svg canvas
	//var svg = d3.select("#linechart_svg")
	var svg = d3.select("#"+properties.svgName)
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom);

	var chart = svg
	    .append("g")
	    .attr("id", properties.svgName+"tsChart")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	chart.append("defs").append("clipPath")
	    .attr("id", properties.svgName+"clip")
	  .append("rect")
	    .attr("width", width)
	    .attr("height", height);

    // Add the X Axis
    chart.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    // Add the Y Axis
    chart.append("g")
        .attr("class", "y axis")
        .call(yAxis);

	var path = chart.append("g")
	    .attr("clip-path", "url(#{clip})".replace("#{clip}","#"+properties.svgName+"clip"))
	  .append("path")
	  	.attr("class", "line")
	  	.datum(data)
	    .attr("d", line)
	    .attr("transform", null);
}

function updateLineChart(properties) {
	data = properties.data;
	newData = properties.newData;

	var ld0 = data[data.length-1].date;
	var ld1 = newData[newData.length-1].date;

	// Append newData
	for (var i = 0; i < newData.length; i++) {
	 	data.push(newData[i]);
	} 

    // Properties
    var x = properties.x;
    var y = properties.y;
	var xAxis = properties.xAxis;
	var yAxis = properties.yAxis;
	var line = properties.line;

	//Always update the y axis to the new data
	y.domain(d3.extent(data, function(d) { return d.value; }));
	//Update the x axis ONLY if the size of the window is small and no transition will be executed
	if(data.length <= PLOT_WINDOW_SIZE){
		x.domain(d3.extent(data, function(d) { return d.date; }));
	}

	// Redraw the new line (using the old x axis)  
	var svg = d3.select("#"+properties.svgName);
	var chart = svg.select("#"+properties.svgName+"tsChart");

	var path = chart.select("path.line")
	    .datum(data)
	    .attr("d", line)
	    .attr("transform", null);

	// Slide it to the left.
	if(data.length > PLOT_WINDOW_SIZE){
		var minDate = new Date(d3.min(data, function(d) { return d.date; }));
		//minDate.setDate(minDate.getDate()-10);
		minDate.setTime(minDate.getTime()-(ld1-ld0));

		chart.select("path.line")
			.transition()
		    .duration(750)
		    .ease("linear")
		    .attr("transform", "translate(" + x(minDate) + ",0)")
		    ;
    }

    // Update X and Y Axises
    chart = chart.transition();
    chart.select(".x.axis") // change the x axis
        .duration(750)
        .ease("linear")
        .call(xAxis);
    chart.select(".y.axis") // change the y axis
        .duration(750)
        .ease("linear")
        .call(yAxis);

    // Update the x axis to the new data
    if (data.length > PLOT_WINDOW_SIZE){
		for (i = 0; i < data.length-PLOT_WINDOW_SIZE; i++) {
			data.shift();
		}

		x.domain(d3.extent(data, function(d) { return d.date; }));
	}
}



dateFormat = d3.time.format("%Y-%m-%d %H:%M:%S");

function queryInitialData(cb) { 
   
	//var strLastDate = $('#txt_last_date').val(); 
	var strLastDate = ""; 
	var req_url = "/rtdata?lastDate={1}".replace("{1}", strLastDate); 
   
	$.getJSON(req_url, function(dataJson) { 

		// Parse data   
		var data = []; 
		$.each(dataJson, function(key, row) { 
			data.push( { date: dateFormat.parse(row.date), 
				temperature:+row.temperature,
				wind_speed:+row.wind_speed,
				pressure:+row.pressure,
				solar_radiation:+row.solar_radiation,
				air_humidity:+row.air_humidity,
				soil_temperature:+row.soil_temperature
			} ); 
		}); 

		if (data.length === 0){ console.log("No items returned!"); return; } 
	 	
		$('#txt_last_date').val( dateFormat( data[data.length-1].date ) );		
		cb(data);		
	}); 
}

function querySyntheticData(cb, error) { 
	var strLastDate = $('#txt_last_date_2').val(); 
	//var strLastDate = ""; 
	var req_url = "/srtconsumer?lastDate={1}".replace("{1}", strLastDate); 
   
	$.getJSON(req_url, function(dataJson) { 

		// Parse data   
		var data = []; 
		$.each(dataJson, function(key, row) { 
			data.push( { date: dateFormat.parse(row.date), 
				value:+row.value
			} ); 
		}); 

		if (data.length === 0){ 
			//console.log("No items returned!"); 
			error(); 
		}else{
			$('#txt_last_date_2').val( dateFormat( data[data.length-1].date ) );		
			cb(data);		
		}  	
	}); 
}

function queryNewData(cb) { 
   
	var strLastDate = $('#txt_last_date').val(); 

	if(strLastDate.trim().length === 0){
		console.log("Error: Parameter lastDate was not found!");
		return;
	}

	var req_url = "/rtdata?lastDate={1}".replace("{1}", strLastDate); 
   
	$.getJSON(req_url, function(dataJson) { 

		// Parse data   
		var data = []; 
		$.each(dataJson, function(key, row) { 
			data.push( { date: dateFormat.parse(row.date), 
				temperature:+row.temperature,
				wind_speed:+row.wind_speed,
				pressure:+row.pressure,
				solar_radiation:+row.solar_radiation,
				air_humidity:+row.air_humidity,
				soil_temperature:+row.soil_temperature
			} ); 
		}); 

		if (data.length === 0){ console.log("No items returned!"); return; } 

		$('#txt_last_date').val( dateFormat( data[data.length-1].date ) );

		cb(data);
	}); 
} 

function getVariable(cdata, variableName){
	data = [];	
	$.each(cdata, function(key, row) { 
		data.push( { date: row.date, value:row[variableName] } ); 
	});

	return data;
}

function updatePlots(temperatureProp,pressureProp,solarRadProp){
			queryNewData(function(newData){
				temperatureData = getVariable(newData, "temperature");
				pressureData = getVariable(newData, "pressure");
				solarRadData = getVariable(newData, "solar_radiation");

				temperatureProp.newData = temperatureData;
				pressureProp.newData = pressureData;
				solarRadProp.newData = solarRadData;
				updateLineChart(temperatureProp);
				updateLineChart(pressureProp);
				updateLineChart(solarRadProp);

				// Recursive execution:
				setTimeout(updatePlots(temperatureProp,pressureProp,solarRadProp), 5000);
			});
}

$(document).ready(function() {

	queryInitialData(function (cdata){
		// Divide data
		temperatureData = getVariable(cdata, "temperature");
		pressureData = getVariable(cdata, "pressure");
		solarRadData = getVariable(cdata, "solar_radiation");

		// Create plots
		temperatureProp = {svgName: "linechart_svg", data: temperatureData};
		pressureProp = {svgName: "linechart2_svg", data: pressureData};
		solarRadProp = {svgName: "linechart3_svg", data: solarRadData};

		initLineChart(temperatureProp);
		initLineChart(pressureProp);
		initLineChart(solarRadProp);

		(function poll(){
		   setTimeout(function(){
			   	queryNewData(function(newData){
					temperatureData = getVariable(newData, "temperature");
					pressureData = getVariable(newData, "pressure");
					solarRadData = getVariable(newData, "solar_radiation");

					temperatureProp.newData = temperatureData;
					pressureProp.newData = pressureData;
					solarRadProp.newData = solarRadData;
					updateLineChart(temperatureProp);
					updateLineChart(pressureProp);
					updateLineChart(solarRadProp);

					poll();
				});
		  }, 1000);
		})();
	});


	var initialized = false;
	var syntheticProp = {svgName: "linechart_synthetic_svg"};
	(function poll2(){
		//console.log("Polling...");
		setTimeout(function(){
			var temp = d3.select("#linechart_synthetic_svgtsChart"); 
			if (temp && temp[0] && temp[0][0]){
				initialized = true;
			}

			querySyntheticData(function (data){				
				if (!initialized){
					// Initialize plot
					syntheticProp.data= data;
					initLineChart(syntheticProp);
					initialized = true;	
				}else{
					syntheticProp.newData = data;
					updateLineChart(syntheticProp);
				}

				poll2();
			}, function(){
				poll2();
			});

		}, 1000);
	})();

});
