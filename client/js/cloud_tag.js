function queryWordsData(cb){
    $.getJSON("/words", function(dataJson) { 
        //console.log(dataJson);
        if (dataJson.length === 0){
            console.log("No data returned!");
        }

        cb(dataJson);
    });
}


$(document).ready(function() {

    function createCloudTag(data){
        data.forEach(function(d){
            //console.log(d);
            d.word_sum_weight = +d.word_sum_weight*20;            
        });


        var fill = d3.scale.category20();
        var color = d3.scale.linear()
                //.domain([0,1,2,3,4,5,6,10,15,20,100])
                //.domain(d3.extent(data, function(d){ return d.word_sum_weight }))
                .range(["#ddd", "#ccc", "#bbb", "#aaa", "#999", "#888", "#777", "#666", "#555", "#444", "#333", "#222"]);

        var width = 600;
        var height = 350;

        d3.layout.cloud().size([width, height])
                .words(data)
                .rotate(0)
                .fontSize(function(d) { return d.word_sum_weight; })
                .on("end", draw)
                .start();

        function draw(words) {
            d3.select("#cloudTag").append("svg")
                    .attr("width", width)
                    .attr("height", height)
                    .attr("class", "wordcloud")
                    .append("g")
                    // without the transform, words words would get cutoff to the left and top, they would
                    // appear outside of the SVG area
                    .attr("transform", "translate("+(width/2)+","+(height/2)+")") //320,200
                    .selectAll("text")
                    .data(words)
                    .enter().append("text")
                    .style("font-size", function(d) { return d.word_sum_weight + "px"; })
                    //.style("fill", function(d, i) { return color(i); })
                    .style("fill", function(d, i) { return fill(i%20); })
                    .attr("transform", function(d) {
                        return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                    })
                    .text(function(d) { return d.word_text; });
        }
    }

    queryWordsData(createCloudTag);

});
