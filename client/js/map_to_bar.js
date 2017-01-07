function map_to_bar(data) {
    document.getElementById("svg_bar").innerHTML = "";
    var margin = {top: 20, right: 20, bottom: 50, left: 40},
        width = 350 - margin.left - margin.right,
        height = 450 - margin.top - margin.bottom;
    var type = ["negative", "neutral","positive"];
    var color = ["#D3352E","#A2A116","#167EA2"];
    var num = [data[0], data[1],data[2]];
    var x = d3.scale.ordinal().rangeRoundBands([0, width], 0.05);
    var y = d3.scale.linear().range([height, 0]);
    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");
    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .ticks(10);
    var tip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([-10, 0])
        .html(function (d) {
            return "<strong>value:</strong> <span style='color:lightgoldenrodyellow'>" + d + "</span>";
        });
    var svg = d3.select("#svg_bar")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");
    x.domain(type);
    y.domain([0, d3.max(num)]);
    svg.call(tip);
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", "-.55em")
        .attr("transform", "rotate(-90)");

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("count");

    svg.selectAll("bar")
        .data(num)
        .enter().append("rect")
        .style("fill", function (d, i) {
            return color[i];
        })
        .attr("x", function (d, i) {
            return x(type[i]) + 20;
        })
        .attr("width", x.rangeBand() - 40)
        .attr("y", function (d) {
            return y(d);
        })
        .attr("height", function (d) {
            return height - y(d);
        })
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);


}

