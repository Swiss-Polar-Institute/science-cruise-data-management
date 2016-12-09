var endpoint = "/api/positions";

function post_marker(marker) {
    updating_marker = marker;
    $.post
    ({
        url: endpoint,
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
            updating_marker.bindPopup(popupContent(data.id, data.text));
        }
    });
}

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

function update_text(id, text) {
    $.ajax
    ({
        url: endpoint,
        dataType: "json",
        type: "PUT",
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        },
        data: JSON.stringify ({
            id: id,
            text: marker_text
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


var marker_text = '';
var marker_id = 0;
var updating_marker = null;

function adjustTextAreaUpdateChange(textArea) {
    marker_text = $(textArea).val();
}
function popupContent(id, text) {
    return 'Internal id:' + id +
        '<br><textarea class="custom_marker_text" ' +
        'onchange="adjustTextAreaUpdateChange(this)" ' +
        'name="'+id+'">' + text+
        '</textarea>';
}

function main() {
    antarctic_map_main();

    // To add a marker (in Ushuaia)
    // L.marker([-54.8, -68.3], {icon: offLineIcon("yellow")}).addTo(map);

    map.on('contextmenu',function(mouseEvent){
        // Creates new marker and sends it to the API
        var marker = L.marker(mouseEvent.latlng, {icon: offLineIcon("blue"), draggable: true});
        marker.addTo(map);

        marker.id = 0;
        marker.text = "";

        make_marker_clickable(marker);

        post_marker(marker);
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

        update_text(id, marker_text);
    });

    loadAndPlotGeojsonMarkers(endpoint);
}