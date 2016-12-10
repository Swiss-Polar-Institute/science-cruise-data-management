function antarctic_map_main() {
    var initialZoom = 0;
    var projection_name = 'EPSG:3031';
    var projection_definition = '+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs';
    var crs = new L.Proj.CRS(projection_name, projection_definition, {
                                origin: [-90, 0],
                                resolutions: [ 40000.0, 20000.0, 10000.0, 5000.0, 2500.0, 1250.0]
                            }
              );

    map = L.map('map', {
        maxZoom: crs.options.resolutions.length,
        minZoom: 0,
        continuousWorld: true,
        zoomControl: true,
        initialZoom: 2,
        center: [-90, 0],
        crs: crs
    }).setView([-90, 0], initialZoom);

    var antarctic_style = { color: 'black',
                            weight: 1,
                            fillColor: 'white',
                            fillOpacity: 1
                          };

    var continents_style = { color: 'black',
                        weight: 1,
                        fillColor: 'green',
                        fillOpacity: 1
                        };

    // loadAndPlotGeojsonPolygon(STATIC_URL + "maps/Coastline_high_res_polygon.geojson", antarctic_style);
    loadAndPlotGeojsonPolygon(STATIC_URL + "maps/Sub-antarctic_coastline_high_res_polygon_to30S.geojson", continents_style);

    // Adds circle for up to 30 degrees.
    L.circle([-90, 0], 7150000).addTo(map);
}

function offLineIcon(color = "blue") {
    // This icon has everything off-line. Could it be generated from L.Icon.Default?

    // Possible colors: black, blue, green, grey, orange, red, violet, yellow.
    // Default color: blue

    var icon = L.icon({
            iconUrl: STATIC_URL + "images/external/leaflet-color-markers/marker-icon-" + color + ".png",
            shadowUrl: STATIC_URL + "images/external/marker-shadow.png",
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
    });
    return icon;
}

function addGeojsonLayer(data, style) {
    var newLayer = L.Proj.geoJson(data, {
            style: style
            }
        );
    newLayer.addTo(map);
}

function show_distance(line) {
    var distance = line._latlngs[0].distanceTo(line._latlngs[1]);
    $(message).text("Distance: " + distance/1000 + " Km");
}

ordered_markers = [];
var lines = [];

function loadAndPlotGeojsonMarkers(url) {
    $.getJSON(url,
        function(geojson)
        {
            var pointToLayer = function(feature, latlng) {
                var marker = L.marker(latlng, {icon: offLineIcon(), draggable: true});
                return marker;
            };

            var onEachFeature = function(feature, layer) {
                    layer.text = layer.feature.properties.text;
                    layer.id = layer.feature.properties.id;

                    make_marker_clickable(layer);

                    ordered_markers.push(layer.getLatLng());

            };

            L.geoJSON(geojson, {pointToLayer: pointToLayer, onEachFeature: onEachFeature}).addTo(map);

            var previous;
            for (var i=0; i < ordered_markers.length; i++) {
                if (i != 0) {
                    var line = new L.Polyline([previous, ordered_markers[i]]);
                    line.on('mouseover', function(e) { show_distance(e.target); });
                    line.addTo(map);
                    lines.push(line);
                }
                previous = ordered_markers[i];
            }
        }
    );
}

function dragStartHandler (e) {
    var latlng = this.getLatLng();

    for (var i = 0; i < lines.length; i++) {
        if (latlng.equals(lines[i]._latlngs[0])) {
            this.movingLine = i;
            this.movingLineIndex = 0;
        }
        else if (latlng.equals(lines[i]._latlngs[1])) {
            this.movingLine = i;
            this.movingLineIndex = 1;
        }
    }
}

function dragHandler (e) {
    var line_latlng = lines[this.movingLine]._latlngs;
    line_latlng[this.movingLineIndex] = e.latlng;
    lines[this.movingLine].setLatLngs(line_latlng);
    show_distance(lines[this.movingLine]);;
}

function dragEndHandler (e) {
    delete this.movingLineIndex;
    delete this.movingLine;
}

function make_marker_clickable(marker) {
    marker.bindPopup(popupContent(marker.id, marker.text));

    marker.on('click', function(e) {
        updating_marker = e.target;
    });

    marker.on('dragstart', dragStartHandler);
    marker.on('drag', dragHandler);
    marker.on('dragend', dragEndHandler);
    marker.on('dragend', put_marker);
}

function loadAndPlotGeojsonPolygon(url, style) {
    $.getJSON(url,
        function(geojson)
        {
            addGeojsonLayer(geojson, style);
        }
    );
}
