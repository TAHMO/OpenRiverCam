$(document).ready(function () {
    // simulate a click
    document.getElementById("mapButton").click();
});

function plotData(callback){
    const id = $('input#bathymetry_id').val();
    $.ajax({
        type: 'GET',
        url: `/api/bathymetry_details/${id}`,
        contentType: "application/json",
        dataType: 'json',
        success: function(data) {
            console.log(data);
            callback(data);
        },

        error: function() {console.log("Something went wrong")}
    });
}

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
  if (tabName === "map_view") {
    callback = map_bathymetry;
  } else {
    callback = cross_section;
  }
  plotData(callback);
}

cross_section = function(data) {
    // add a highchart of the bathymetry profile
    Highcharts.chart('cross_section', {
        chart: {
        },
        title: {
            text: `Bathymetry at site ${data.site_id} - ${data.site_name}`
        },
        subtitle: {
            text: 'YZ profile (left bank is zero)'
        },
        xAxis: {
            reversed: false,
            title: {
                enabled: true,
                text: 'Distance from left-bank'
            },
            labels: {
                format: '{value} m'
            },
            maxPadding: 0.05,
            showLastLabel: true
        },
        yAxis: {
            title: {
                text: 'Elevation above reference level'
            },
            labels: {
                format: '{value} m'
            },
            lineWidth: 2
        },
        legend: {
            enabled: false
        },
        tooltip: {
            headerFormat: '<b>{series.name}</b><br/>',
            pointFormat: 'Distance: {point.x} m, Elevation: {point.y} m'
        },
        plotOptions: {
            spline: {
                marker: {
                    enable: false
                }
            }
        },
        series: [{
            name: 'Bathymetry',
            data: data.bathym_yz,
        }]
    });
}
map_bathymetry = function(data) {
   // make a nice geospatial map
    var maxAutoZoom = 19;
    var map = L.map('map').setView({lon: 0, lat: 0}, 2);
    var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 20,
        attribution: '&copy; <a href="https://openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors' +
            '</a> ',
        tileSize: 256,
    });
    var googleSat = L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        subdomains:['mt0','mt1','mt2','mt3']
    });
    var googleTer = L.tileLayer('http://{s}.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        subdomains:['mt0','mt1','mt2','mt3']
    });
    var baseMaps = {
        "OpenStreetMap": osmLayer,
        "Google Satellite": googleSat,
        "Google Terrain": googleTer

    }
    L.control.layers(baseMaps).addTo(map);
    osmLayer.addTo(map);
    // add a scale at at your map.
    var scale = L.control.scale().addTo(map);
    // add site position to map
    marker = new L.marker(data.site_position);
    toolTip = "<dl>" +
        "<dt>ID: " + data.site_id + "</dt>" +
        "<dt>Name: " + data.site_name + "</dt>" +
        "</dl>"
    marker.bindTooltip(toolTip);
    // update the marker so that it sets everything in the same way
    marker.addTo(map);
    // zoom to marker
    pos = marker.getLatLng();
    map.setView([pos.lat, pos.lng], maxAutoZoom);

    // add bathymetry to map
    L.geoJson(data.bathym_geojson, {
        style: function(feature) {
            return {
            stroke: true,
            color: "red",
            weight: 5
            }
        }
    }).addTo(map);
}
