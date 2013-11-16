function make_pie_chart(data, element) {
    nv.addGraph(function() {
        var chart = nv.models.pieChart()
          .x(function(d) { return d[0] })
          .y(function(d) { return d[1] })
          .showLabels(true);
          
        chart.valueFormat(d3.format(',f'));

        d3.select(element)
          .datum(data)
          .transition().duration(1200)
          .call(chart);

        return chart;
    });
}