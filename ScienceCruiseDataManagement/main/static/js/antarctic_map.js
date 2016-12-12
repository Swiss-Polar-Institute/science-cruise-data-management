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

    loadAndPlotGeojsonPolygon(STATIC_URL + "maps/Coastline_high_res_polygon.geojson", antarctic_style);
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

function m_to_formatted_nautical_miles(distance_m) {
    var nautical_miles = (distance_m/1000) * 0.539957;

    return nautical_miles.toFixed(2);
}

function show_distance(line) {
    var line_distance = line._latlngs[0].distanceTo(line._latlngs[1]);
    var line_nautical_miles = m_to_formatted_nautical_miles(line_distance);

    var total_distance = 0;
    for (var i = 0; i < lines.length; i++) {
        var lat_longs = lines[i].getLatLngs();

        total_distance += lat_longs[0].distanceTo(lat_longs[1]);
    }

    var total_nautical_miles = m_to_formatted_nautical_miles(total_distance);

    // $(message).html("<b>Line:</b> " + line_nautical_miles + " Nautical miles | <b>Total:</b> " + total_nautical_miles + " Nautical miles");
}

var lines = [];
last_added_marker = null;

function loadAndPlotGeojsonMarkers(url) {
    $.getJSON(url,
        function(geojson) {
            var pointToLayer = function(feature, latlng) {
                var marker = L.marker(latlng, {icon: offLineIcon(feature.properties.marker_color), draggable: false});
                return marker;
            };

            var onEachFeature = function(feature, layer) {
                    layer.text = layer.feature.properties.text;
                    layer.id = layer.feature.properties.id;

                    make_marker_clickable(layer);
            };

            L.geoJSON(geojson, {pointToLayer: pointToLayer, onEachFeature: onEachFeature}).addTo(map);
        }
    );
}
/*
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
    if (typeof(this.movingLine) !== 'undefined') {
        var line_latlng = lines[this.movingLine]._latlngs;
        line_latlng[this.movingLineIndex] = e.latlng;
        lines[this.movingLine].setLatLngs(line_latlng);
        show_distance(lines[this.movingLine]);
    }
}

function dragEndHandler (e) {
    delete this.movingLineIndex;
    delete this.movingLine;
}
*/

function make_marker_clickable(marker) {
    marker.bindPopup(popupContent(marker.id, marker.text));

    marker.on('click', function(e) {
        updating_marker = e.target;
    });

    //marker.on('dragstart', dragStartHandler);
    //marker.on('drag', dragHandler);
    //marker.on('dragend', dragEndHandler);
    //marker.on('dragend', put_marker);

/*
    if (last_added_marker != null) {
        var line = new L.Polyline([last_added_marker.getLatLng(), marker.getLatLng()]);
        line.on('mouseover', function(e) {
            show_distance(e.target);
            e.target.setStyle({color: '#ff0000'});
        });
        line.on('mouseout', function(e) {
            e.target.setStyle({color: '#3388ff'});
        });
        line.addTo(map);
        lines.push(line);
    }
*/
    last_added_marker = marker;
}

function loadAndPlotGeojsonPolygon(url, style) {
    $.getJSON(url,
        function(geojson)
        {
            addGeojsonLayer(geojson, style);
        }
    );
}

function adjustTextAreaUpdateChange(textArea) {
    marker_text = $(textArea).val();
}

function popupContent(id, text) {
    return 'Id: ' + id + '<br>' + text;
    /* With a text box: return 'Internal id:' + id +
        '<br><textarea class="custom_marker_text" ' +
        'onchange="adjustTextAreaUpdateChange(this)" ' +
        'name="'+id+'">' + text+
        '</textarea>';
    */
}
/*
function put_marker(event) {
    updating_marker = event.target;
    $.ajax
    ({
        url: endpoint,
        dataType: "json",
        type: "PUT",
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        },
        data: JSON.stringify ({
            latitude: updating_marker.getLatLng().lat,
            longitude: updating_marker.getLatLng().lng,
            id: updating_marker.id
        }),
        success: function(data) {
            updating_marker.id = data.id;
            updating_marker.bindPopup(popupContent(data.id, data.text));
        }
    });
}
*/