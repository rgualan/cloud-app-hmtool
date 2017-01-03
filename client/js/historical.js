var dateFormat = d3.time.format("%Y-%m-%d %H:%M:%S");

function createXYWrapper(data, variable){
	var xyData = [];
	var dataWrapper;

	data.forEach(function(d){
		xyData.push({x: dateFormat.parse(d.date), y: +d[variable] });
	});

	dataWrapper =  [{
        values: xyData,
        key: variable
        //color: "#ff7f0e",
        //strokeWidth: 4
        //classed: 'dashed'
    }];

    return dataWrapper;
}


$(document).ready(function() {	

	$.getJSON('/data', function(data_json) {
		// CREATE THE TABLE
		//console.log(data_json);
		var items = [];
		$.each(data_json, function(key, row) {
			items.push([ row["station_name"],row["latitude"],row["longitude"],row["date"],
				row["rec_number"],row["temperature"],row["air_humidity"],
				row["pressure"],row["solar_radiation"],row["soil_temperature"],
				row["wind_speed"],row["wind_direction"] ]);
		});
		//console.log(items);

		$('#data_table').DataTable({
			data : items,
			"scrollX": true,
			columns : [ 
				{title : "Station name"}, 
				{title : "Latitude"},
				{title : "Longitude"},
				{title : "Date"},
				{title : "Record number"},
				{title : "Temperature"},
				{title : "Air humidity"},
				{title : "Pressure"},
				{title : "Solar radiation"},
				{title : "Soil temperature"},
				{title : "Wind speed"},
				{title : "Wind direction"}
				]
		});

		var chart;

		// CREATE THE SELECT
		var defaultVariable = "temperature"
		var variables = [];
		$.each( data_json[0], function( key, value ) {
			if ( ['station_name','date','rec_number','longitude','latitude'].indexOf(key) < 0 )
			variables.push(key);
		});
		variables.sort();

		d3.select("#variableSelect")
			.selectAll("option")
			.data(variables)
		  	.enter().append("option")
		    .text(function(d) { return d; });
		$("#variableSelect").val(defaultVariable);

		// CREATE THE PLOT
		var dataWrapper =  createXYWrapper(data_json, defaultVariable);

		nv.addGraph(function() {
	        chart = nv.models.lineWithFocusChart();
		    
		    chart.xAxis
	            .axisLabel("Date")
	            //.tickFormat(d3.time.format("%Y-%m-%d %H:%M:%S"))
	            //.staggerLabels(true)
	        	.tickFormat(function(d) {
		            return dateFormat(new Date(d));
		        })
		        .showMaxMin(false)
		        .ticks(5)
	        ;

	        chart.x2Axis
	            .axisLabel("Date")
	        	.tickFormat(function(d) {
		            return d3.time.format('%Y-%m-%d')(new Date(d));
		        })
		        .showMaxMin(false)
	        ;

	        chart.yAxis
	            .axisLabel(defaultVariable)
	            .tickFormat(function(d) {
	                if (d == null) {
	                    return 'N/A';
	                }
	                return d3.format(',.2f')(d);
	            })
	        ;

	        chart.useInteractiveGuideline(true);

	        d3.select('#chart svg')
	            .datum(dataWrapper)
	            .call(chart);

			nv.utils.windowResize(chart.update);
	        return chart;
	    });


		// CREATE EVENTS
	    $("#variableSelect").on('change', function () {
			var variable = this.value;
			console.log("Selected: " + variable);
			dataWrapper =  createXYWrapper(data_json, variable);
			//console.log(dataWrapper);

			d3.select('#chart svg').datum(dataWrapper);
	        chart.update();
        });


	});
});
