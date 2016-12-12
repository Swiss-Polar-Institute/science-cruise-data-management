// Code once used and that it might be handy for the cruise.

var lines = [];
last_added_marker = null;


function m_to_formatted_nautical_miles(distance_m) {
    var nautical_miles = (distance_m/1000) * 0.539957;

    return nautical_miles.toFixed(2);
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