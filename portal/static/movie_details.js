$(document).ready(function () {
    // simulate a click
    document.getElementById("PIVButton").click();
});

(function($) {
    $.fn.plotPIV = function(movieId, serieTitle) {
        const container = this;
        $.getJSON(
            `/api/visualize/get_velocity_vectors/${movieId}`,
            function( response ) {
                Chart = Highcharts.chart(container.attr('id'), {
                    chart: {
                        plotBackgroundImage: `/api/visualize/get_projected_snapshot/${movieId}`,
                        height: 1500 * ((response["ymax"] - response["ymin"]) / (response["xmax"] - response["xmin"])),
                        width: 1500,
                        margin: 0,
//                        scrollbar: {
//                            enabled: true
//                        }

                    },
                    legend: {
                        enabled: false
                    },
                    title: {
                        text: null
                    },
                    xAxis: {
                        min: response["xmin"],
                        max: response["xmax"],
                        gridLineWidth: 0,
                        visible: true
                    },
                    yAxis: {
                        min: response["ymin"],
                        max: response["ymax"],
                        gridLineWidth: 0,
                        visible: false
                    },
                    series: [{
                        type: 'vector',
                        name: serieTitle,
                        color: Highcharts.getOptions().colors[6],
                        vectorLength: 20,
                        data: response["data"],
                        turboThreshold: 0, // Required for datasets covering more than 1k points.
                        tooltip: {
                            useHTML: true,
                            headerFormat: '<b>{series.name}</b><br>',
                            pointFormatter: function() {
                                var string = 'velocity: ' + this.options.length.toFixed(2) + ' m/s <br> angle measured from left-to-right: ' + (this.options.direction + 90).toFixed(2) + ' deg.<br>';
                                return string;
                            }
                        }
                    }],
                    exporting: {
                        buttons: {
                            contextButton: {
                                menuItems: ['downloadPNG']
                            }
                        }
                    }
                });
            }
        );

        return this;
    }
})(jQuery);

function openTab(evt, tabName) {
  // Declare all variables
  var i, tabcontent, tablinks;

  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
  // run ajax call and callback
//  if (tabName === "map_view") {
//    callback = map_bathymetry;
//  } else {
//    callback = cross_section;
//  }
//  plotData(callback);
}
