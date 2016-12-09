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

            // Text for the marker
            updating_marker.bindPopup(popupContent(data.id, data.text));
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
        success: function(data) {
            updating_marker.id = data.id;
            updating_marker.bindPopup(popupContent(data.id, data.text));
        }
    });
}

function update_text(id, text) {
    $.ajax
    ({
        url: "/api/pois.json",
        dataType: "json",
        type: "PUT",
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        },
        data: JSON.stringify ({
            id: updating_marker.id,
            text: text
        }),
        success: function(data) {
            updating_marker.bindPopup(popupContent(data.id, data.text));
        },
        error: function(xhr, status, error) {
          var err = eval("(" + xhr.responseText + ")");
          alert(err.Message);
        }
    });
}


function send_form() {
    alert("test");
}

var markerText = '';

function adjustTextAreaUpdateChange(textArea) {
    markerText = $(textArea).val();
}

function popupContent(marker_id, text) {
    return '<textarea class="custom_marker_text" onchange="adjustTextAreaUpdateChange(this)" name="'+marker_id+'" placeholder="Press to write a note...">'+text+'</textarea>';
}

function main() {
    antarctic_map_main();

    // To add a marker (in Ushuaia)
    L.marker([-54.8, -68.3], {icon: offLineIcon("yellow")}).addTo(map);

    map.on('contextmenu',function(mouseEvent){
        // Creates new marker and sends it to the API
        var marker = L.marker(mouseEvent.latlng, {icon: offLineIcon("red"), draggable: true});
        marker.addTo(map);
        post_marker(marker);

        // Updates the marker
        marker.on('dragend', put_marker);
    });

    map.on('popupclose', function(e) {
        var popup = e.popup;
        var content = $.parseHTML(popup.getContent());

        $.each(content,function( index ) {
            if($(this).is("textarea") && $(this).hasClass( "custom_marker_text" )){
                textArea=$(this);
            }
        });

        var id = textArea.attr('name');

        update_text(id, markerText);
    });

    map.on('drag')
    loadAndPlotGeojsonMarkers(STATIC_URL + "api/events.geojson");
}