/**
 * Created by junewang on 14/11/2016.
 */
var color = d3.scale.ordinal().range(["#48A36D", "#7FB1CF", "#C280B7",
 "#E26962", "#E29D58", "#E0B15B", "#DFB95C", "#DDC05E", "#F2DE8A"]);  
var maxSelect = 3;

var margin = {top: 20, right: 20, bottom: 30, left: 50};
var margin2 = {top: 5, right: 100, bottom: 30, left: 50};
var padding = 20;
var w = 800;
var h = 300 - margin.top - margin.bottom, height2 = 50 - margin2.top - margin2.bottom;

// Parse the date / time
var parseDate = d3.time.format("%Y-%m-%d %H:%M:%S").parse;
    bisectDate = d3.bisector(function(d) { return d.date; }).left;
var xScale = d3.time.scale()
            // .domain([d3.min(time_all), d3.max(time_all)])//d3.min(time_all)
            .range([padding + 30, w - padding * 2]),
    xScale2 = d3.time.scale()
        .range([padding + 30, w - padding * 2]); 

var yScale = d3.scale.linear()
    .range([h - padding, padding]);

var xAxis2 = d3.svg.axis() // xAxis for brush slider
    .scale(xScale2)
    .orient("bottom"); 

var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient("bottom").ticks(5);
var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient("left")
        .ticks(5);

var context = d3.select("body")
    .append("g") // Brushing context box container
    .attr("transform", "translate(" + 0 + "," + 410 + ")")
    .attr("class", "context");

// var brush = d3.svg.brush()//for slider bar at the bottom
//     .x(xScale2) 
//     .on("brush", brushed);

//     context.append("g") // Create brushing xAxis
//       .attr("class", "x axis1")
//       .attr("transform", "translate(0," + height2 + ")")
//       .call(xAxis2);

// function line(data, time,color) {
//     var time_all = [];
//     var data_all = [];
//     for (var i = 0; i < time.length; i++)
//     {
//         time_all=time_all.concat(time[i]);
//         data_all=data_all.concat(data[i]);
//     }
//         //a[i] = {date: time[i], data: data[i]}
//     var margin = {top: 20, right: 20, bottom: 30, left: 50};
    
//     var padding = 20;
//     var xScale = d3.time.scale()
//             .domain([d3.min(time_all), d3.max(time_all)])
//             .range([padding + 30, w - padding * 2])
//         ;
//     var yScale = d3.scale.linear()
//         .domain([d3.min(data_all), d3.max(data_all)])
//         .range([h - padding, padding]);

    
//     /*    var zoomArea = {
//      x1: 0,
//      y1: 0,
//      x2: xdomain,
//      y2: ydomain
//      };*/

//     var svg = d3.select("svg")
//         .attr("width", w)
//         .attr("height", h)
//         .append("g")

//     var xAxis = d3.svg.axis()
//         .scale(xScale)
//         .orient("bottom");
//     var yAxis = d3.svg.axis()
//         .scale(yScale)
//         .orient("left");
//     svg.append("rect")
//             .attr("width", w)
//             .attr("height", h)                                    
//             .attr("x", 0) 
//             .attr("y", 0)
//             .attr("id", "mouse-tracker")
//             .style("fill", "white"); 

//     svg.append("g")
//         .attr("class", "x-axis")
//         .attr("transform", "translate(0," + (h - padding) + ")")
//         .call(xAxis)
//     ;

//     svg.append("g")
//         .attr("class", "y-axis")
//         .attr("transform", "translate(" + (padding + 30) + ",0)")
//         .call(yAxis);

//     var focus = svg.append("g")                               
//         .style("display", "none"); 

//     for(var j=0;j<data.length;j++){
//         var line;
//         line = d3.svg.line()
//         // .interpolate("basis")
//         .x(function (d, i) {
//             return xScale(time[j][i]);
//         })
//         .y(function (d,i) {
//             return yScale(d);
//         });
        


//         //for (var i = 0; i < data.length; i++) {
//         var path = svg.append("g")
//             .append("path")
//             .attr("class","graph")
//             .attr("d", line(data[j]))
//             .style("fill", "#0000")
//             .style("fill", "none")
//             .style("stroke-width", 2)
//             .style("stroke", color[j])
//             .style("stroke-opacity", 0.9);
//     }
// }
function line2(d, type_data,color) {
     var div = d3.select("#tooltip_line")
    .style("opacity", 0).style("width", 120).style("height", 60);
    var data_all = [];
    for (var i = d.length - 1; i >= 0; i--) {
        data_all=data_all.concat(d[i][type_data]);
        
    };

    // xScale.domain(d3.extent(d, function(d) { return parseDate(d.date); }));
    // yScale.domain([0, d3.max(data_all)])
    // xScale2.domain(xScale.domain());

    
    var svg = d3.select("svg")

    svg.select(".x-axis")
        .attr("class", "x-axis")
        .attr("transform", "translate(0," + (h - padding) + ")")
        .call(xAxis)
        .style("stroke-width", "0.5px");

    svg.select(".y-axis")
        .attr("class", "y-axis")
        .attr("transform", "translate(" + (padding + 30) + ",0)")
        .call(yAxis)
        .style("stroke-width", 1);


    //append clip path for lines plotted, hiding those part out of bounds
    svg.append("defs")
      .append("clipPath") 
        .attr("id", "clip")
        .append("rect")
        .attr("width", w)
        .attr("height", h); 

    var focus = svg.append("g")                               
        .style("display", "none"); 

    
    var valueline = d3.svg.line()
    .x(function(d) { return xScale(parseDate(d.date)); })
    .y(function(d) { return yScale(d[type_data]); })
    .defined(function(d) { return d[type_data]; });
    var path = svg.append("g")
        .append("path")
        .attr("class","graph")
        .attr("d", valueline(d))
        .style("stroke-width", 1.5)
        .style("stroke", color)
        .style("stroke-opacity", 0.9)
        .style("fill", "#0000")
        .style("fill", "none");

       // Add the scatterplot
   var circle = svg.selectAll("dot")
        .data(d)
        .enter()
        .append("circle")
        .attr("r", 1.5)
        .attr("cx", function(d) { return xScale(parseDate(d.date)); })
        .attr("cy", function(d) { return yScale(d[type_data]); })
        .attr("fill", color)
        .on("mouseover",function (d) {
           d3.select(this).transition().duration(100).attr("r",2.5);
            div.html(d.station_name + ":<br/>value:"  + d[type_data])
             .style("x", xScale(parseDate(d.date)))
                .style("y", (yScale(d[type_data]))).attr("opacity",1);

        })
        .on("mouseout",function () {
            d3.select(this).transition().duration(100).attr("r",1.5);

        });

}
function jqchk() {
    var colour = ['red', 'blue', 'green', 'black', 'pink','orange'];
    var chk_value = [];
    var color=[];

        $('input[class="check_box"]:checked').each(function () {

        chk_value.push($(this).val());
        color.push(colour[$(this).attr('id')]);
    });
    
    return [chk_value,color]
}

$(document).ready(function () {
    var dataset = [];
    var dataGroup;
    //document.getElementById("station").innerHTML("ssss");
    $.getJSON('/data', function(data_json) {
        console.log(data_json)
        var items = [];
        dataGroup = d3.nest()
            .key(function(d) {
                return d.station_name;
            }).sortKeys(d3.ascending)
            .entries(data_json);
        console.log(JSON.stringify(dataGroup));
        var strG = ""

        var svg = d3.select("svg")
        .attr("width", w)
        .attr("height", h)
        .append("g")

        dataGroup.forEach(function(d,i) {

            // var issue = svg.selectAll(".issue")
            //     .data(dataGroup) 
            //     .enter().append("g")
            //     .attr("class", "issue");

            // issue.append("path")
            //     .attr("class", "line")
            //     .style("pointer-events", "none") // Stop line interferring with cursor
            //     .attr("id", function(d) {
            //         return "line-" + d.key.replace(" ", "").replace("/", ""); // Give line id of line-(insert issue name, with any spaces replaced with no spaces)
            //     })
            //     .attr("clip-path", "url(#clip)")//use clip path to make irrelevant part invisible
            //     .style("stroke", color);

            strG += "<div class='checkbox'><label class='checkbox-inline'><input type='checkbox' id='"+i+"'class='check_box' value='" + d.key + "'>" + d.key + "</label> </div>";
        });
        document.getElementById("station").innerHTML = strG;
        console.log(strG);

        // $.each(data_json, function(key, row) {
        //     items.push([ row["station_name"],row["latitude"],row["longitude"],row["date"],
        //     row["rec_number"],row["temperature"],row["air_humidity"],
        //     row["pressure"],row["solar_radiation"],row["soil_temperature"],
        //     row["wind_speed"],row["wind_direction"] ]);
        // });

        // $('#data_table').DataTable({
        //     data: items,
        //     columns: [
        //         {title: "Station name"},
        //         {title: "Latitude"},
        //         {title: "Longitude"},
        //         {title: "Date"},
        //         {title: "Record number"},
        //         {title: "Temperature"},
        //         {title: "Air humidity"},
        //         {title: "Pressure"},
        //         {title: "Solar radiation"},
        //         {title: "Soil temperature"},
        //         {title: "Wind speed"},
        //         {title: "Wind direction"}
        //     ]
        // });
        function line_chart(type,chk_station,color) {
            document.querySelector('svg').innerHTML = '<g class="x-axis"></g><g class="y-axis"></g>';
            var data = new Array();
            var time = new Array();
                if (chk_station.length == 0) {
                    
                }else{
                    for(j=0;j<chk_station.length;j++)
                    {
                        // data[j]=new Array();
                        // time[j]=new Array();
                        dataGroup.forEach(function(d,i) {
                            if (d.key === chk_station[j]) {
                                xScale.domain(d3.extent(d.values, function(d) { return parseDate(d.date); }));
                                yScale.domain([0, d3.max(d.values, function(d){ return d[type];})])
                                xScale2.domain(xScale.domain());
                                console.log(d.values);
                                line2(d.values,type,color[i]);
                            };
                        });
                        
                        // for (i = 1; i < items.length; i++) {
                        //     if(items[i][0]==chk_station[j])
                        //     {
                        //       data[j].push( parseFloat(items[i][parseInt(type)]));
                        //       date = new Date(items[i][3].replace(/-/g, "/"));
                        //       time[j].push(date);
                        //     }
                        // }
                    }
                    // line(data, time,color);
                };
        }

        $("#select").change(function () {

            var type = $("#select").find("option:selected").val();
            if (type != "0") {
                var chk_station=jqchk();
                line_chart(type,chk_station[0],chk_station[1]);
            };

        });
        $("input[type='checkbox']").click(function(){
            
            var checkboxes = $('input[type="checkbox"]');
            var current = checkboxes.filter(':checked').length;
            checkboxes.filter(':not(:checked)').prop('disabled', current >= maxSelect);
            if ($("#select").find("option:selected").val() != "0") {
                var type = $("#select").find("option:selected").val();
                var chk_station=jqchk();

                line_chart(type,chk_station[0],chk_station[1]);
                boxplot(data_json,type,chk_station[0])
            };   
        })

        
    });
})

function findMaxY(data){  // Define function "findMaxY"
    var maxYValues = data.map(function(d) { 
      
        return d3.max(d.values, function(value) { // Return max rating value
          return value.rating; })
    });
    return d3.max(maxYValues);
}



