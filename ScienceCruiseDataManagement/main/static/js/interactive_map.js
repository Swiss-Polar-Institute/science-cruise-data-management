function post_marker(marker) {
    updating_marker = marker;
    $.post
    ({
        url: "/api/pois.json",
        dataType: "json",
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        },
        data: JSON.stringify ({
            latitude: marker.getLatLng().lat,
            longitude: marker.getLatLng().lng,
        }),
        success: function(data) {
            updating_marker.id = data.id;
            alert(updating_marker.id);
        }
    });
}

function put_marker(event) {
    updating_marker = event.target;
    $.ajax
    ({
        url: "/api/pois.json",
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
        dataType: "application/json",
        success: function(data) {
            updating_marker.id = data.id;
        }
    });
}

function main() {
    antarctic_map_main();

    // To add a marker (in Ushuaia)
    L.marker([-54.8, -68.3], {icon: offLineIcon("yellow")}).addTo(map);

    map.on('contextmenu',function(mouseEvent){
        // popup.openOn(map);
        var marker = L.marker(mouseEvent.latlng, {icon: offLineIcon("red"), draggable: true});
        marker.addTo(map);
        post_marker(marker);
        marker.on('dragend', put_marker);
    });

    map.on('drag')
    loadAndPlotGeojsonMarkers(STATIC_URL + "api/events.geojson");
}