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

function average(data){
  var sum = data.reduce(function(sum, value){
    return sum + value;
  }, 0);

  var avg = sum / data.length;
  return avg;
}

function standardDeviation(values){
  var avg = average(values);
  
  var squareDiffs = values.map(function(value){
    var diff = value - avg;
    var sqrDiff = diff * diff;
    return sqrDiff;
  });
  
  var avgSquareDiff = average(squareDiffs);

  var stdDev = Math.sqrt(avgSquareDiff);
  return stdDev;
}

function getStatistics(array, variable){
	var sorted = array;
	sorted.sort();
	//console.log(sorted);

	var q1 = sorted[Math.ceil(0.25*sorted.length)];
	var q2 = sorted[Math.ceil(0.50*sorted.length)];
	var q3 = sorted[Math.ceil(0.75*sorted.length)];
	var minv = Math.min.apply(null, sorted);
	var maxv = Math.max.apply(null, sorted); 

	var mean = average(array);
	var stDev = standardDeviation(array);

	return [{
          label: variable,
          values: {
          	mean: mean,
          	stDev: stDev,
            Q1: q1,
            Q2: q2,
            Q3: q3,
            min: minv,
            max: maxv,
            whisker_low: minv,
            whisker_high: maxv
          },
    	}]
}

$(document).ready(function() {
	var spinner = new Spinner();
	spinner.spin(document.getElementById('chart'));

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
			spinner.stop();
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

        $("#btnAggregate").on('click', function () {
			var variable = $("#variableSelect").val();
			var level = $("#levelAggregationSelect").val();
			var how = $("#howSelect").val();
			
			//console.log(variable);console.log(level);console.log(how);

			$.getJSON('/aggregate?variable='+variable+"&level="+level+"&how="+how, function(data) {
				dataWrapper2 = createXYWrapper(data, variable);
				dataWrapper2[0].key = "Aggregated-"+level+"-"+how;
				//console.log(dataWrapper2[0].values.slice(0,10));

				dataWrapperTemp  = d3.select('#chart svg').datum();
				dataWrapper = [];
				dataWrapperTemp.forEach(function(d){
					if (d.key !== dataWrapper2[0].key){
						dataWrapper.push(d);						
					}
				});
				dataWrapper.push(dataWrapper2[0]);

				d3.select('#chart svg').datum(dataWrapper);
				chart.update();					
			});		
			
        });

        $("#statsLink").on('click', function () {
        	console.log("Calc statistics");
        	var variable = $("#variableSelect").val();
			
			/*$.getJSON('/statistics?variable='+variable, function(data) {
				var format = d3.format(",.2f");	
				$('#txt_mean').val( format( data.mean ) );
				$('#txt_median').val( format( data.median ) );
				$('#txt_min').val( format( data.min ) );
				$('#txt_max').val( format( data.max ) );
			});*/

			var datum = d3.select('#chart svg').datum();
			var xyData = datum[0].values;
        	var data = []
        	xyData.forEach(function(d){
        		data.push(d.y);
        	})
        	var stats = getStatistics(data, variable)[0]["values"];
			var format = d3.format(",.2f");	
			$('#txt_mean').val( format( stats.mean ) );
			$('#txt_stdev').val( format( stats.stDev ) );
			$('#txt_min').val( format( stats.min ) );
			$('#txt_max').val( format( stats.max ) );
			$('#txt_median').val( format( stats.Q2 ) );
			$('#txt_iqr').val( format( stats.Q3-stats.Q1 ) );

        });
        
        $("#btnRunningMean").on('click', function () {
        	console.log("Calc running mean");
        	var variable = $("#variableSelect").val();
        	var steps = $("#txt_steps").val();
			
			$.getJSON('/runningmean?variable='+variable+"&steps="+steps, function(data) {
				var format = d3.format(",.2f");	
				
				dataWrapper2 = createXYWrapper(data, variable);
				dataWrapper2[0].key = "Running-mean-"+steps;

				dataWrapperTemp  = d3.select('#chart svg').datum();
				dataWrapper = [];
				dataWrapperTemp.forEach(function(d){
					if (d.key !== dataWrapper2[0].key){
						dataWrapper.push(d);						
					}
				});
				dataWrapper.push(dataWrapper2[0]);

				d3.select('#chart svg').datum(dataWrapper);
				chart.update();		
			});
        });

        $("#btnReset").on('click', function () {
        	console.log("Reseting plot");

			dataWrapperTemp  = d3.select('#chart svg').datum();
			dataWrapper = [dataWrapperTemp[0]];

			d3.select('#chart svg').datum(dataWrapper);
			chart.update();
        });


		$("#boxPlotLink").on('click', function () {
			var variable = $("#variableSelect").val();
        	var datum = d3.select('#chart svg').datum(); 

        	var xyData = datum[0].values;
        	var data = []
        	xyData.forEach(function(d){
        		data.push(d.y);
        	})

			var boxplotChart; 
			nv.addGraph(function() {
			  var width = 250;
			  var height = 400;
		      boxplotChart = nv.models.boxPlotChart()
		          .x(function(d) { return d.label })
		          .staggerLabels(true)
		          .maxBoxWidth(75) // prevent boxes from being incredibly wide
		          .yDomain(d3.extent(data))
		          .width(width).height(height)
		          ;

		      d3.select('#boxPlotChart svg')
		          .datum(getStatistics(data, variable))
		          .call(boxplotChart)
		          .style({ 'width': width, 'height': height });;
		      nv.utils.windowResize(boxplotChart.update);
		      return boxplotChart;
		    });
		});

        $("#histogramLink").on('click', function () {
        	var variable = $("#variableSelect").val();
        	var datum = d3.select('#chart svg').datum(); 

        	var xyData = datum[0].values;
        	var data = []
        	xyData.forEach(function(d){
        		data.push(d.y);
        	})
        	//console.log(data);

			var dataWrapper = [
			  {
			    x: data,
			    type: 'histogram',
				marker: {
			    color: 'steelblue',
				},
			  }
			];

			var layout = {
			  title: "Histogram", 
			  xaxis: {title: variable}, 
			  yaxis: {title: "Frequency"}
			};

			Plotly.newPlot('histogramChart', dataWrapper, layout);
			
        });


	});
});
