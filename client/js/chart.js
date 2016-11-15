/**
 * Created by junewang on 14/11/2016.
 */
var colour = ['red', 'blue', 'green', 'black', 'pink'];
function line(data, time) {
    var a=[];
    for(var i=0;i<time.length;i++)
        a[i]={date:time[i],data:data[i]}
   // var a = data;

    /*    var xdomain = 500;
     var ydomain = 50;
     var bandPos = [-1, -1];
     var pos;*/
var margin = {top: 20, right: 20, bottom: 30, left: 50};
    var w = 1500;
    var h = 300;
    var padding = 20;
    var xScale = d3.time.scale()
            .domain([d3.min(time), d3.max(time)])
            .range([padding + 30, w - padding * 2])
        ;
    var yScale = d3.scale.linear()
        .domain([d3.min(data), d3.max(data)])
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
    //.style(colour,'blue')
    //.selectAll("text")
    //.text(function (d) {
    //    return time[d];
    // })
    ;

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + (padding + 30) + ",0)")
        .call(yAxis)
        .append("text")
        .text("aa")
    ;

    var line = d3.svg.line()
        .interpolate("monotone")
        .x(function (d, i) {
            return xScale(time[i]);
        })
        .y(function (d) {
            return yScale(d);
        })


    //for (var i = 0; i < data.length; i++) {
    var path = svg.append("path")
        .attr("d", line(data))
        .style("fill", "#0000")
        .style("fill", "none")
        .style("stroke-width", 1)
        .style("stroke", colour[0])
        .style("stroke-opacity", 0.9);


    svg.selectAll("circle" + i)
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", function (d, i) {
            return xScale(time[i]);
        })
        .attr("cy", function (d) {
            return yScale(d);
        })
        .attr("r", 3.5)
        .attr("fill", function (d) {
            return colour[0];
        })
        .on('mouseover', function () {

            d3.select(this).transition().duration(500).attr('r', 5);

        })

        .on('mouseout', function () {

            d3.select(this).transition().duration(500).attr('r', 3.5);

        });

    //inner_line

    var xInner = d3.svg.axis()
        .scale(xScale)
        .tickSize(-(h-padding-padding),0,0)
        .orient("bottom")
        .ticks(time.length);

    svg.append("g")
        .attr("class","inner_line")
        .attr("transform", "translate(0," + (h - padding) + ")")
        .call(xInner)
        .selectAll("text")
        .text("");

    var yInner = d3.svg.axis()
        .scale(yScale)
        .tickSize(-(w-padding*2),0,0)
        .tickFormat("") 
        .orient("left")
        .ticks(10);
    var yBar=svg.append("g")
        .attr("class", "inner_line")
        .attr("transform", "translate("+padding+",0)")
        .call(yInner);

    //tips

 /*   var tips = svg.append('g').attr('class', 'tips');

    tips.append('rect')

        .attr('class', 'tips-border')

        .attr('width', 200)

        .attr('height', 50)

        .attr('rx', 10)

        .attr('ry', 10);

    var wording1 = tips.append('text')

        .attr('class', 'tips-text')

        .attr('x', 10)

        .attr('y', 20)

        .text('');

    var wording2 = tips.append('text')

        .attr('class', 'tips-text')

        .attr('x', 10)

        .attr('y', 40)

        .text('');


    container

        .on('mousemove', function () {

            var m = d3.mouse(this),

                cx = m[0] - margin.left;

            var x0 = xScale.invert(cx);

            var i = (d3.bisector(function (d, i) {
            return xScale(time[i]);
        }).left)(time, x0, 1);

            var d0 = time[i - 1],

                d1 = time[i] || {},

                d = x0 - d0.date > d1.date - x0 ? d1 : d0;

            function formatWording(d,i) {

                return '日期：' + time[i];

            }

            wording1.text(formatWording(d,i));

            wording2.text('PV：' + d);

            var x1 = xScale(d),

                y1 = yScale(time[i]);

// 处理超出边界的情况

            //var dx = x1 > width ? x1 - width + 200 : x1 + 200 > width ? 200 : 0;

            //var dy = y1 > height ? y1 - height + 50 : y1 + 50 > height ? 50 : 0;

           // x1 -= dx;

            //y1 -= dy;

            d3.select('.tips')

                .attr('transform', 'translate(' + x1 + ',' + y1 + ')');

            d3.select('.tips').style('display', 'block');

        })

        .on('mouseout', function () {

            d3.select('.tips').style('display', 'none');

        });*/
    //zoom
    /*    var band = svg.append("rect")
     .attr("width", 0)
     .attr("height", 0)
     .attr("x", 0)
     .attr("y", 0)
     .attr("class", "band");
     svg.append("clipPath")
     .attr("id", "clip")
     .append("rect")
     .attr("width", w)
     .attr("height", h);

     var drag = d3.behavior.drag();
     var zoomOverlay = svg.append("rect")
     .attr("width", w - 10)
     .attr("height", h)
     .attr("class", "zoomOverlay")
     .call(drag);

     var zoomout = svg.append("g");

     zoomout.append("rect")
     .attr("class", "zoomOut")
     .attr("width", 75)
     .attr("height", 40)
     .attr("x", -12)
     .attr("y", h - 20)
     .on("click", function () {
     zoomOut();
     });

     zoomout.append("text")
     .attr("class", "zoomOutText")
     .attr("width", 75)
     .attr("height", 30)
     .attr("x", -10)
     .attr("y", h - 5)
     .text("Zoom Out");

     zoom();

     drag.on("dragend", function () {
     var pos = d3.mouse(this);
     var x1 = xScale.invert(bandPos[0]);
     var x2 = xScale.invert(pos[0]);

     if (x1 < x2) {
     zoomArea.x1 = x1;
     zoomArea.x2 = x2;
     } else {
     zoomArea.x1 = x2;
     zoomArea.x2 = x1;
     }

     var y1 = yScale.invert(pos[1]);
     var y2 = yScale.invert(bandPos[1]);

     if (x1 < x2) {
     zoomArea.y1 = y1;
     zoomArea.y2 = y2;
     } else {
     zoomArea.y1 = y2;
     zoomArea.y2 = y1;
     }

     bandPos = [-1, -1];

     d3.select(".band").transition()
     .attr("width", 0)
     .attr("height", 0)
     .attr("x", bandPos[0])
     .attr("y", bandPos[1]);

     zoom();
     });

     drag.on("drag", function () {

     var pos = d3.mouse(this);

     if (pos[0] < bandPos[0]) {
     d3.select(".band").attr("transform", "translate(" + (pos[0]) + "," + bandPos[1] + ")");
     }
     if (pos[1] < bandPos[1]) {
     d3.select(".band").attr("transform", "translate(" + (pos[0]) + "," + pos[1] + ")");
     }
     if (pos[1] < bandPos[1] && pos[0] > bandPos[0]) {
     d3.select(".band").attr("transform", "translate(" + (bandPos[0]) + "," + pos[1] + ")");
     }

     //set new position of band when user initializes drag
     if (bandPos[0] == -1) {
     bandPos = pos;
     d3.select(".band").attr("transform", "translate(" + bandPos[0] + "," + bandPos[1] + ")");
     }

     d3.select(".band").transition().duration(1)
     .attr("width", Math.abs(bandPos[0] - pos[0]))
     .attr("height", Math.abs(bandPos[1] - pos[1]));
     });

     function zoom() {
     //recalculate domains
     if (zoomArea.x1 > zoomArea.x2) {
     xScale.domain([zoomArea.x2, zoomArea.x1]);
     } else {
     xScale.domain([zoomArea.x1, zoomArea.x2]);
     }

     if (zoomArea.y1 > zoomArea.y2) {
     yScale.domain([zoomArea.y2, zoomArea.y1]);
     } else {
     yScale.domain([zoomArea.y1, zoomArea.y2]);
     }

     //update axis and redraw lines
     var t = svg.transition().duration(750);
     t.select(".x.axis").call(xAxis);
     t.select(".y.axis").call(yAxis);

     t.selectAll(".line").attr("d", line);
     }

     var zoomOut = function () {
     xScale.domain([0, xdomain]);
     yScale.domain([0, ydomain]);

     var t = svg.transition().duration(750);
     t.select(".x.axis").call(xAxis);
     t.select(".y.axis").call(yAxis);

     t.selectAll(".line").attr("d", line);
     }*/
    // }


}
$(document).ready(function () {
    var dataset = [];
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

        console.log(dataset);


        /*items = [['a', 'd', 'd', '2014-05-13 06:15:00', 1, 10.63, 100, 743.1774, 2.156174, 17.98, 0.845, 295.3276],
         ['a', 'd', 'd', '2014-05-13 06:20:00', 2, 10.69, 100, 743.2004, 3.409225, 17.97, 0.916, 285.5955],
         ['a', 'd', 'd', '2014-05-13 06:25:00', 3, 10.69, 100, 743.2656, 4.402618, 17.97, 0.871, 307.3093],
         ['a', 'd', 'd', '2014-05-13 06:30:00', 4, 10.71, 100, 743.2841, 5.700919, 17.96, 0.649, 268.4106],
         ['a', 'd', 'd', '2014-05-13 06:35:00', 5, 10.67, 100, 743.3101, 6.400824, 17.96, 0.962, 288.0786],
         ['a', 'd', 'd', '2014-05-13 06:40:00', 6, 10.61, 100, 743.3107, 12.81273, 17.95, 0.669, 212.0179],
         ['a', 'd', 'd', '2014-05-13 06:45:00', 7, 10.62, 100, 743.3678, 16.95503, 17.94, 0.59, 193.0039],
         ['a', 'd', 'd', '2014-05-13 06:50:00', 8, 10.74, 100, 743.429, 31.62904, 17.94, 0.532, 259.6522],
         ]*/
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
        $("#select").change(function () {
            var a = $("#select").find("option:selected").val();
            document.querySelector('svg').innerHTML = '';
            var data = new Array();
            var time = new Array();
            n = 0;
            for (i = 1; i < 100; i++) {

                data[n] = parseFloat(items[i][parseInt(a)]);
                date = new Date(items[i][3].replace(/-/g, "/"));
                time[n] = date;
                //date.getHours()+":"+date.getMinutes()+":"+date.getSeconds();
                n++;
            }
            //       end_str = (time[0]).replace(/-/g,"/");
            //     var end_date = new Date(end_str);
            //     alert(end_date.getDay());
            line(data, time);


        });
    });
})


