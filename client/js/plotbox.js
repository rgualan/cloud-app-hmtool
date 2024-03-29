/**
 * Created by junewang on 03/12/2016.
 */


 function boxplot(item, type, station) {
      var labels = true; // show the text labels beside individual boxplots?

    var margin = {top: 30, right: 50, bottom: 80, left: 50};
    var width = 800 - margin.left - margin.right;
    var height = 400 - margin.top - margin.bottom;

console.log(item);

    var sta_result = statistic(item, type,station);
    var sta_value = sta_result[0];

    var div = d3.select(".tooltip")
    .style("opacity", 0).style("width", 120).style("height", 60);

        var min = sta_result[2],
            max = sta_result[1];
        document.querySelector('#svg').innerHTML = '';
        var chart = d3.box()
                .whiskers(iqr(1.5))
                .height(height)
                .domain([min, max])
                .showLabels(labels);

        var svg = d3.select("#svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .attr("class", "box")
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
                ;
   /*     var svg1 = d3.select("#svg1")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .attr("class", "box")
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
                ;*/
    function mouseover(d) {
        mstat=d[0];
        mstat_data=d[1];
        alert(mstat_data);
        d3.select(this).transition().duration(2000).attr("fill", "red")

    }
        // the x-axis
        var x = d3.scale.ordinal()
                .domain(sta_value.map(function (d) {
                    return d[0]
                }))
                .rangeRoundBands([0, width], 0.7, 0.3);
        var xAxis = d3.svg.axis()
                .scale(x)
                .orient("bottom");

        // the y-axis
        var y = d3.scale.linear()
                .domain([min, max])
                .range([height + margin.top, 0 + margin.top]);

        var yAxis = d3.svg.axis()
                .scale(y)
                .orient("left")
       /* // line
        var xLine = d3.time.scale().range([0, width]);
        var yLine = d3.scale.linear().range([height, 0]);
        var xLineAxis = d3.svg.axis().scale(x)
            .orient("bottom")
        var yLineAxis = d3.svg.axis().scale(yLine)
            .orient("left").ticks(5);
        var valueline = d3.svg.line()
            .x(function(d) { return x(d.date); })
            .y(function(d) { return y0(d.rating); })
            .defined(function(d) { return d.rating; });
*/
        // draw the boxplots
        svg.selectAll(".box")
                .data(sta_value)
                .enter().append("g")
                .attr("transform", function (d) {
                    return "translate(" + x(d[0]) + "," + margin.top + ")";
                })
                .call(chart.width(x.rangeBand()))
                .on("mouseover", function(d) {
                    div.html(d[0] + ":<br/> average value:"  + d[2][0]+"<br/> highest value:"+ d[2][1]+"<br/> lowest value:"+d[2][2])
                        .style("left", x(d[0])+x.rangeBand()+70 + "px")
                        .style("top", (d3.event.pageY - 28) + "px")
                        .transition()
                        .duration(200)
                        .style("opacity", .9);


                 })
                .on("mouseout", function(d) {
                    div.transition()
                        .duration(500)
                        .style("opacity", 0);
                })
                /*.on("click", function(d){

                })*/;

        // add a title
        svg.append("text")
                .attr("x", (width / 2))
                .attr("y", 0 + (margin.top / 2))
                .attr("text-anchor", "middle")
                .style("font-size", "18px")
                //.style("text-decoration", "underline")
                .text("Box plot");

        // draw y axis
        svg.append("g")
                .attr("class", "y axis")
                .call(yAxis)
                .append("text") // and text1
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .style("font-size", "16px")
                .text(type);

        // draw x axis
        svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + (height + margin.top + 10) + ")")
                .call(xAxis)
                .append("text")             // text label for the x axis
                .attr("x", (width / 2))
                .attr("y", 20)
                .attr("dy", ".71em")
                .style("text-anchor", "middle")
                .style("font-size", "16px")
                .text("Station");
    }
    ;

    // Returns a function to compute the interquartile range.
    function iqr(k) {
        return function (d, i) {
            var q1 = d.quartiles[0],
                    q3 = d.quartiles[2],
                    iqr = (q3 - q1) * k,
                    i = -1,
                    j = d.length;
            while (d[++i] < q1 - iqr);
            while (d[--j] > q3 + iqr);
            return [i, j];
        };
    }



function statistic(item, type,station_name) {
    var sta_value=[];
    var  min_all = Infinity,
         max_all = -Infinity;
    for(var i=0;i<station_name.length;i++)
    {
        var min = Infinity, max = -Infinity;
        sta_value[i] = [];
        sta_value[i][0] = station_name[i];
        sta_value[i][2] = [];
        sta_value[i][1] = [];
        var sum = 0, n = 0.0;
        for (var j = 0; j < item.length; j++) {
                if (item[j].station_name === station_name[i]) {
                                sta_value[i][1].push(parseFloat(item[j][type]));
                    var rowMax = parseFloat(item[j][type]);
                    var rowMin = parseFloat(item[j][type]);
                    sum +=parseFloat(item[j][type]);
                    if (rowMax > max) max = rowMax;
                    if (rowMin < min) min = rowMin;
                    n++;

                }
            }
            if (max > max_all) max_all = max;
            if (min < min_all) min_all = min;
            sta_value[i][2][0]=(sum/n).toFixed(2);
            sta_value[i][2][1]=max.toFixed(2);
            sta_value[i][2][2]=min.toFixed(2);
    }
    return [sta_value,max_all,min_all];

}