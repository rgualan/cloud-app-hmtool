// world map
var width = 800,
    height = 700,
    active = d3.select(null);
var projection = d3.geo.mercator()
    .scale((width + 1) / 2 / Math.PI)
    .translate([width / 2, height / 2])
    .precision(0.1);
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

// import world json
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

    // read tweets data
    d3.json("/tweets-api", function (error, data) {
        data=[{"location": [36.840000000000003, -2.46], "sentiment": -1, "tweetid": "817781285863071745"}, {"location": [31.149999999999999, -81.489999999999995], "sentiment": -1, "tweetid": "817786175687565312"}];
        var lat_lng = [];
        lat_lng[0] = [];
        lat_lng[1] = [];
        lat_lng[2] = [];
        for (var i = 0; i < data.length; i++) {
            if (data[i].sentiment < 0)
                lat_lng[0].push([data[i].location[0], data[i].location[1]]);
            else if (data[i].sentiment == 0)
                lat_lng[1].push([data[i].location[0], data[i].location[1]]);
            else
                lat_lng[2].push([data[i].location[0], data[i].location[1]]);

        }
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

        var sen = getseperate(data);

        var word = ["bad", "zero","happy"];
        var col = ["#D3352E","#A2A116","#167EA2"];
        for (i = 0; i < word.length; i++) {
            g.selectAll(".circle_" + word[i])
                .data(sen[word[i]])
                .enter()
                .append("circle")
                .attr("id", "circle_" + word[i])
                .attr("cx", function (d) {
                    return projection([d.location[1], d.location[0]])[0];
                })
                .attr("cy", function (d) {
                    return projection([d.location[1], d.location[0]])[1];
                })
                .style("fill", col[i])
                .attr("r", 1.5) // sets the radius
                .on('mouseover', function (d) {
                    d3.select(this).attr({
                        fill: col[i],
                        r: 1.5 * 2
                    });
                    d3.select("#tooltip").transition().duration(200).style("opacity", 0.9);
                    d3.select("#tooltip").html("tweetid:" + d.tweetid + "<br>weight:" + d.sentiment)
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
                    g.selectAll("#circle_" + word[i]).attr("d", path.projection(projection));
                }

                g.selectAll("path")
                    .attr("d", path.projection(projection));

            });

        d3.select("#back").on("click", function () {
            map_to_bar([sen.bad.length, sen.zero.length, sen.happy.length]);
            d3.select("#bar_country_name").html("World");
        });
        svg.call(zoom);
        map_to_bar([sen.bad.length, sen.zero.length, sen.happy.length]);


    });
});
//seperate data into two part
function getseperate(data) {
    var sen = {bad: [], zero: [], happy: []};
    for (var d in data) {
        if (Number(data[d].sentiment) < 0) {
            sen.bad.push(data[d]);
        }
        else if (Number(data[d].sentiment) === 0) {
            sen.zero.push(data[d]);
        }
        else
            sen.happy.push(data[d]);
    }
    return sen;

}

//caculate bad and happy amount of one country

function draw(lat_lng, country) {
    d3.csv('js/codegrid/country_code.csv', function (data) {
        var code_select;
        for (var i = 0; i < data.length; i++) {
            if (data[i].Name === country) {
                code_select = data[i].Code.toLowerCase();
                break;
            }
        }
        var grid = codegrid.CodeGrid();
        var count_bad = 0;
        var count_happy = 0;
        var count_zero = 0;
        grid.getCode(lat_lng[0], function (err, code0) {
            grid.getCode(lat_lng[1], function (err, code1) {
                grid.getCode(lat_lng[2], function (err, code2) {
                    for (var i = 0; i < code0.length; i++) {
                        if (code0[i] === code_select) {
                            count_bad++;
                        }
                    }
                    for (i = 0; i < code1.length; i++) {
                        if (code1[i] === code_select) {
                            count_zero++;
                        }
                    }
                    for (var i = 0; i < code2.length; i++) {
                        if (code2[i] === code_select) {
                            count_happy++;
                        }
                    }
                    map_to_bar([count_bad, count_zero,count_happy]);
                });
            });
        });
    });
}



