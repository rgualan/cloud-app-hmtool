var width = 960,
    height = 960,
    active = d3.select(null);


var projection = d3.geo.mercator()
    .scale((width + 1) / 2 / Math.PI)
    .translate([width / 2, height / 2])
    .precision(.1);

var path = d3.geo.path()
    .projection(projection);

var graticule = d3.geo.graticule();

var svg = d3.select("#canvas-svg").append("svg")
    .attr("width", width)
    .attr("height", height);

svg.append("path")
    .datum(graticule)
    .attr("class", "graticule")
    .attr("d", path);


d3.json("../data/world-topo-min.json", function (error, world) {
    var countries = topojson.feature(world, world.objects.countries).features;

    svg.append("path")
        .datum(graticule)
        .attr("class", "choropleth")
        .attr("d", path);

    var g = svg.append("g");

    g.append("path")
        .datum({type: "LineString", coordinates: [[-180, 0], [-90, 0], [0, 0], [90, 0], [180, 0]]})
        .attr("class", "equator")
        .attr("d", path);


    var country = g.selectAll(".country").data(countries);

    country.enter().insert("path")
        .attr("class", "land")
        .attr("d", path)
        .attr("id", function (d, i) {
            return d.id;
        })
        .attr("title", function (d) {
            return d.properties.name;
        })


        /*.on('mouseover', function (d) {
            d3.select(this)
                     .enter().append("text")
      .attr("class", function(d) { return "subunit-label " + d.id; })
      .attr("transform", function(d) { return "translate(" + path.centroid(d) + ")"; })
      .attr("dy", ".35em")
      .text(function(d) { return d.properties.name; });

                })
                .on("mouseout", function (d) {

                    d3.select("#tooltip_country").style("opacity", 0);
                });
*/
/*
    function clicked(d) {

        if (active.node() === this) return reset();
        active.classed("active", false);
        active = d3.select(this).classed("active", true);


        var bounds = path.bounds(d),
            dx = bounds[1][0] - bounds[0][0],
            dy = bounds[1][1] - bounds[0][1],
            x = (bounds[0][0] + bounds[1][0]) / 2,
            y = (bounds[0][1] + bounds[1][1]) / 2,
            scale = .7 / Math.max(dx / width, dy / height),
            translate = [width / 2 - scale * x, height / 2 - scale * y-150];

        g.transition()
            .duration(750)
            .style("stroke-width", 1.5 / scale + "px")
            .attr("transform", "translate(" + translate + ")scale(" + scale + ")");

    }

    function reset() {
        active.classed("active", false);
        active = d3.select(null);

        g.transition()
            .duration(750)
            .style("stroke-width", "1.5px")
            .attr("transform", "");

    }
*/


    g.append("path")
        .datum(topojson.mesh(world, world.objects.countries, function (a, b) {
            return a !== b;
        }))
        .attr("class", "boundary")
        .attr("d", path);

    svg.attr("height", height * 2.2 / 3);



    d3.json("../data/test_mapdata.json", function (error, data) {
        var sen = getseperate(data);
        var word = ["bad", "happy"];
        var col = ["red", "blue"];

        for (var i = 0; i < word.length; i++) {
            console.log(sen[word[i]]);
            g.selectAll(".circle_" + word[i])
                .data(sen[word[i]])
                .enter()
                .append("circle")
                .attr("id", "circle_" + word[i])
                .attr("cx", function (d) {
                    return projection([d.geometry.coordinates[0], d.geometry.coordinates[1]])[0];
                })
                .attr("cy", function (d) {
                    return projection([d.geometry.coordinates[0], d.geometry.coordinates[1]])[1];
                })
                .style("fill", col[i])
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
                        fill: col[i],
                        r: 2
                    });
                    d3.select("#tooltip").style("opacity", 0);
                });
        }
        // zoom and pan
var zoom = d3.behavior.zoom()
    .on("zoom",function() {
        g.attr("transform","translate("+
            d3.event.translate.join(",")+")scale("+d3.event.scale+")");
          for (var i = 0; i < word.length; i++) {
              var a=g.selectAll("#circle_" + word[i]) .attr("d", path.projection(projection));
          }

        g.selectAll("path")
            .attr("d", path.projection(projection));

  });

svg.call(zoom);


    });
});
function getseperate(data) {
    sen = {bad: [], happy: []};
    var feature = data.features;
    for (d in feature) {
        if (Number(feature[d].point) < 0) {
            sen.bad.push(feature[d]);
        }
        else {
            sen.happy.push(feature[d]);
        }
    }
    return sen;

}


