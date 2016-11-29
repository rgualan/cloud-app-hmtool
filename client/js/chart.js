/**
 * Created by junewang on 14/11/2016.
 */

function line(data, time,color) {
    var time_all = [];
    var data_all = [];
    for (var i = 0; i < time.length; i++)
    {
        time_all=time_all.concat(time[i]);
        data_all=data_all.concat(data[i]);
    }
        //a[i] = {date: time[i], data: data[i]}
    var margin = {top: 20, right: 20, bottom: 30, left: 50};
    var w = 1000;
    var h = 300;
    var padding = 20;
    var xScale = d3.time.scale()
            .domain([d3.min(time_all), d3.max(time_all)])
            .range([padding + 30, w - padding * 2])
        ;
    var yScale = d3.scale.linear()
        .domain([d3.min(data_all), d3.max(data_all)])
        .range([h - padding, padding]);


    /*    var zoomArea = {
     x1: 0,
     y1: 0,
     x2: xdomain,
     y2: ydomain
     };*/

    var svg = d3.select("svg")
        .attr("width", w)
        .attr("height", h);


    var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient("bottom");
    var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient("left");


    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(0," + (h - padding) + ")")
        .call(xAxis)
    ;

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + (padding + 30) + ",0)")
        .call(yAxis)

    ;
for(var j=0;j<data.length;j++)
    {
        var line;
        line = d3.svg.line()
        .x(function (d, i) {
            return xScale(time[j][i]);
        })
        .y(function (d,i) {
            return yScale(d);
        })


    //for (var i = 0; i < data.length; i++) {
    var path = svg.append("path")
        .attr("d", line(data[j]))
        .style("fill", "#0000")
        .style("fill", "none")
        .style("stroke-width", 1)
        .style("stroke", color[j])
        .style("stroke-opacity", 0.9);


    svg.selectAll("circle" + j)
        .data(data[j])
        .enter()
        .append("circle")
        .attr("cx", function (d, i) {
            return xScale(time[j][i]);
        })
        .attr("cy", function (d) {
            return yScale(d);
        })
        .attr("r", 3.5)
        .attr("fill", function (d) {
            return color[j];
        })
        .on('mouseover', function () {

            d3.select(this).transition().duration(500).attr('r', 5);

        })

        .on('mouseout', function () {

            d3.select(this).transition().duration(500).attr('r', 3.5);

        });

    }


}

function jqchk() {
    var colour = ['red', 'blue', 'green', 'black', 'pink'];
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

    //document.getElementById("station").innerHTML("ssss");
    d3.csv("../data/Station1_min5.csv", function (error, csv) {
        //var dataset = [];
        var xMark = [];
        csv.forEach(function (d) {
            dataset.push([d["#station_name"], d["latitude"], d["longitude"], d["timestamp"],
                d["record"], d["temperature"], d["air_humidity"],
                d["pressure"], d["solar_radiation"], d["soil_temperature"],
                d["wind_velocity"], d["wind_direction"]]);
        })
        items = dataset;

        var station_name = [];
        for (var i = 1; i < items.length; i++) {
            var m = 1;
            for (var j = 0; j < station_name.length; j++) {
                if (station_name[j] == items[i][0])
                    m = 0;
            }
            if (m == 1) {
                station_name.push(items[i][0]);
            }
        }
        var str = "";
        for (var i = 0; i < station_name.length; i++) {
            str += "<div class='checkbox'><label><input type='checkbox' id='"+i+"'class='check_box' value='" + station_name[i] + "'>" + station_name[i] + "</label></div>";
        }


        document.getElementById("station").innerHTML = str;
        console.log(dataset);
        $('#data_table').DataTable({
            data: items,
            columns: [
                {title: "Station name"},
                {title: "Latitude"},
                {title: "Longitude"},
                {title: "Date"},
                {title: "Record number"},
                {title: "Temperature"},
                {title: "Air humidity"},
                {title: "Pressure"},
                {title: "Solar radiation"},
                {title: "Soil temperature"},
                {title: "Wind speed"},
                {title: "Wind direction"}
            ]
        });
        function line_chart(a,chk_station,color) {
            document.querySelector('svg').innerHTML = '';
            var data = new Array();
            var time = new Array();

                for(j=0;j<chk_station.length;j++)
                {

                    data[j]=new Array();
                    time[j]=new Array();
                     for (i = 1; i < items.length; i++) {
                        if(items[i][0]==chk_station[j])
                        {
                          data[j].push( parseFloat(items[i][parseInt(a)]));
                          date = new Date(items[i][3].replace(/-/g, "/"));
                          time[j].push(date);

                     }
                }
            }
            line(data, time,color);

        }
        $("#select").change(function () {
            var a = $("#select").find("option:selected").val();
            var chk_station=jqchk();
            line_chart(a,chk_station[0],chk_station[1]);

        });
            $("input[type='checkbox']").click(function(){
                 var a = $("#select").find("option:selected").val();
            var chk_station=jqchk();
            line_chart(a,chk_station[0],chk_station[1]);
             })

    });
})


