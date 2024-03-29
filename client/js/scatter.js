var margin = { top: 20, right: 10, bottom: 40, left: 50 },
    outerWidth = 600,
    outerHeight = 400,
    width = outerWidth - margin.left - margin.right,
    height = outerHeight - margin.top - margin.bottom;

var x = d3.time.scale().range([0, width]).nice();
var y = d3.scale.linear().range([height, 0]).nice();

function queryTweetData(cb){    //reads the tweets from the datastore
    $.getJSON("/tweets", function(dataJson){
        if (dataJson.length === 0){
            console.log("No data returned!");
        }
        cb(dataJson);
    });
}

var parseDate = d3.time.format("%Y-%m-%d %H:%M:%S").parse;

$(document).ready(function() {

    function createTweetData(data) {
        data.forEach(function(d) {
            d.date = parseDate(d.date);
        });

        var xMax = d3.max(data, function (d) {return d.date;}),
            xMin = d3.min(data, function (d) {return d.date;}),
            // xMin = xMin > 0 ? 0 : xMin,
            yMax = d3.max(data, function (d) {return d.weight;}) * 1.05,
            yMin = d3.min(data, function (d) {return d.weight;});
            //yMin = yMin > 0 ? 0 : yMin;

        x.domain([xMin, xMax]);
        y.domain([yMin, yMax]);

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom")
            .tickSize(-height);

        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left")
            .tickSize(-width);

        var color = d3.scale.category10();

        var tip = d3.tip()
            .attr("class", "d3-tip")
            .offset([-10, 0])
            .html(function (d) {
                return "Date: " + d.date + "<br>" + "Tweet: " + d.words + "<br>" + "Weight: " + d.weight;
            });

        var zoomBeh = d3.behavior.zoom()
            .x(x)
            .y(y)
            .scaleExtent([0, 500])
            .on("zoom", zoom);

        var svg = d3.select("#scatter")
            .append("svg")
            .attr("width", outerWidth)
            .attr("height", outerHeight)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
            .call(zoomBeh);

        svg.call(tip);

        svg.append("rect")
            .attr("width", width)
            .attr("height", height);

        svg.append("g")
            .attr("class", "axis x")
            //.classed("x axis", true)
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis)
            .append("text")
            .classed("label", true)
            .attr("x", width)
            .attr("y", margin.bottom - 20)
            .style("text-anchor", "end")
            .text("Date");

        svg.append("g")
            .attr("class", "axis y")
            //.classed("y axis", true)
            .call(yAxis)
            .append("text")
            //.classed("label", true)
            .attr("transform", "rotate(-90)")
            .attr("y", -margin.left+20)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("Polarity");

        var objects = svg.append("svg")
            .classed("objects", true)
            .attr("width", width)
            .attr("height", height);

        objects.append("svg:line")
            .classed("axisLine hAxisLine", true)
            .attr("x1", 0)
            .attr("y1", 0)
            .attr("x2", width)
            .attr("y2", 0)
            .attr("transform", "translate(0," + height + ")");

        objects.append("svg:line")
            .classed("axisLine vAxisLine", true)
            .attr("x1", 0)
            .attr("y1", 0)
            .attr("x2", 0)
            .attr("y2", height);

        objects.selectAll(".dot")
            .data(data)
            .enter().append("circle")
            .classed("dot", true)
            .attr("r", 5)//function (d) { return 6 * Math.sqrt(Math.abs(d.weight) / Math.PI); })
            .attr("transform", transform)
            .style("fill", function(d){return color(Math.abs(d.weight));})
            .on("mouseover", tip.show)
            .on("mouseout", tip.hide);
      /*
       var legend = svg.selectAll(".legend")
       .data(color.domain())
       .enter().append("g")
       .classed("legend", true)
       .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

       legend.append("circle")
       .attr("r", 3.5)
       .attr("cx", width + 20)
       .attr("fill", color);

       legend.append("text")
       .attr("x", width + 26)
       .attr("dy", ".35em")
       .text(function(d) { return d; });*/

        d3.select("input").on("click", change);

        function change() {
            xMax = d3.max(data, function (d){return d.date;});
            xMin = d3.min(data, function (d){return d.date;});

            zoomBeh.x(x.domain([xMin, xMax])).y(y.domain([yMin, yMax]));
            var svg = d3.select("#scatter").transition();
            svg.select(".x.axis").duration(750).call(xAxis).select(".label").text("Date");
            objects.selectAll(".dot").transition().duration(1000).attr("transform", transform);
        }

        function zoom() {
            svg.select(".x.axis").call(xAxis);
            svg.select(".y.axis").call(yAxis);
            svg.selectAll(".dot").attr("transform", transform);
        }

        function transform(d) {
            return "translate(" + x(d.date) + "," + y(d.weight) + ")";
        }
    }
    queryTweetData(createTweetData);
});