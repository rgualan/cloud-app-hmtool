var width = 700,
    height = 700,
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


d3.json("/json/world-topo-min.json", function (error, world) {
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


    d3.json("json/test_mapdata.json", function (error, data) {
        var data_get = data.features;
        var lat_lng = [];
        lat_lng[0] = [];
        lat_lng[1] = [];
        for (var i = 0; i < data_get.length; i++) {
            if (data_get[i].point < 0)
                lat_lng[0].push([data_get[i].geometry.coordinates[1], data_get[i].geometry.coordinates[0]]);
            else
                lat_lng[1].push([data_get[i].geometry.coordinates[1], data_get[i].geometry.coordinates[0]]);
        }
        console.log(lat_lng);
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


            .on('mouseover', function (d) {
                d3.select("#country").html("<h4>" + d.properties.name + "</h4>");

            })
            .on('click', function (d) {

                d3.select("#bar_country_name").html(d.properties.name);
                draw(lat_lng, d.properties.name);

            })

            .on("mouseout", function (d) {
                d3.select("#country").html("<h4>World</h4>");
            });

        g.append("path")
            .datum(topojson.mesh(world, world.objects.countries, function (a, b) {
                //console.log(a);
                //console.log(b);

                return a !== b;
            }))
            .attr("class", "boundary")
            .attr("d", path);

        svg.attr("height", height * 2.2 / 3);


        var sen = getseperate(data.features);
        console.log(sen);
        var word = ["bad", "happy"];
        var col = ["#F084B3", "#91E4D5"];


        for (var i = 0; i < word.length; i++) {
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
                .attr("r", 1.5) // sets the radius
                .on('mouseover', function (d) {
                    d3.select(this).attr({
                        fill: col[i],
                        r: 1.5 * 2
                    });
                    d3.select("#tooltip").transition().duration(200).style("opacity", .9);
                    d3.select("#tooltip").html("user_id:" + d.user_id + "<br>point:" + d.point)
                        .style("left", (d3.event.pageX) + "px")
                        .style("top", (d3.event.pageY - 28) + "px");
                })
                .on("mouseout", function (d) {
                    d3.select(this).attr({
                        fill: col[i],
                        r: 1.5
                    });
                    d3.select("#tooltip").style("opacity", 0);
                });
        }
        // zoom and pan
        var zoom = d3.behavior.zoom()
            .on("zoom", function () {
                g.attr("transform", "translate(" +
                    d3.event.translate.join(",") + ")scale(" + d3.event.scale + ")");
                for (var i = 0; i < word.length; i++) {
                    var a = g.selectAll("#circle_" + word[i]).attr("d", path.projection(projection));
                }

                g.selectAll("path")
                    .attr("d", path.projection(projection));

            });

        function button1() {

        }

        d3.select("#back").on("click", function () {
            map_to_bar([sen.bad.length, sen.happy.length]);
            d3.select("#bar_country_name").html("World");
        })
        svg.call(zoom);
        map_to_bar([sen.bad.length, sen.happy.length]);


    });
});
function getseperate(data) {
    sen = {bad: [], happy: []};
    for (d in data) {
        if (Number(data[d].point) < 0) {
            sen.bad.push(data[d]);
        }
        else {
            sen.happy.push(data[d]);
        }
    }
    return sen;

}

//caculate bad and happy amount of one country

function draw(lat_lng, country) {
    d3.csv('js/codegrid/country_code.csv', function (data) {
        var country_name_code = [];
        var code_select;
        var n = 0;
        for (var i = 0; i < data.length; i++) {
            if (data[i].Name === country) {
                code_select = data[i].Code.toLowerCase();
                break;
            }
        }
        var grid = codegrid.CodeGrid();
        var count_bad = 0;
        var count_happy = 0;
        grid.getCode(lat_lng[0], function (err, code0) {
            grid.getCode(lat_lng[1], function (err, code1) {
                for (var i = 0; i < code0.length; i++) {
                    if (code0[i] === code_select) {
                        count_bad++;
                    }
                }
                for (var i = 0; i < code1.length; i++) {
                    if (code1[i] === code_select) {
                        count_happy++;
                    }
                }
                map_to_bar([count_bad, count_happy]);
            });
        })
    })
}



