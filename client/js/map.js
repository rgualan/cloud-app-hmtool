var width = 960,
    height = 480;

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

var projection = d3.geo.equirectangular()
    .scale(153)
    .translate([width / 2, height / 2])


var path = d3.geo.path()
    .projection(projection);

var graticule = d3.geo.graticule();

d3.json("../data/world.json", function (error, world) {

    d3.json("../data/test_mapdata.json", function (error, data) {
        console.log(data.features);
        svg.selectAll("circle")
            .data(data.features)
            .enter()
            .append("a")
            .append("circle")
            .attr("cx", function (d) {
                return projection([d.geometry.coordinates[0], d.geometry.coordinates[1]])[0];
            })
            .attr("cy", function (d) {
                return projection([d.geometry.coordinates[0], d.geometry.coordinates[1]])[1];
            })
            .style("fill", "red")
            .attr("r", 2) // sets the radius
            .on('mouseover', function (d) {
                d3.select(this).attr({
                    fill: "orange",
                    r: 2 * 2
                });
                d3.select("#tooltip").transition().duration(200).style("opacity", .9);
                d3.select("#tooltip").html("user_id:" + d.user_id + "<br>point:" + d.point)
                    .style("left", (d3.event.pageX) + "px")
                    .style("top", (d3.event.pageY - 28) + "px");
            })
            .on("mouseout", function (d) {
                d3.select(this).attr({
                    fill: "red",
                    r: 2
                });
                d3.select("#tooltip").style("opacity", 0);
            });
    });


    svg.append("g")
        .attr("class", "land")
        .selectAll("path")
        .data([topojson.object(world, world.objects.land)])
        .enter().append("path")
        .attr("d", path);
    svg.append("g")
        .attr("class", "boundary")
        .selectAll("boundary")
        .data([topojson.object(world, world.objects.countries)])
        .enter().append("path")
        .attr("d", path);
    svg.append("g")
        .attr("class", "graticule")
        .selectAll("path")
        .data(graticule.lines)
        .enter().append("path")
        .attr("d", path);


});
