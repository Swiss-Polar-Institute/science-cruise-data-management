function main(static_url) {
		// proj4.defs("EPSG:3031","+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs");
		// proj4.defs("urn:ogc:def:crs:EPSG::3031","+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs");
		var initialZoom = 0;
        var projection_name = 'EPSG:3031';
        var projection_definition = '+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs';
		var crs = new L.Proj.CRS(projection_name, projection_definition, {
                                    origin: [-90, 0],
                                    resolutions: [ 40000.0, 20000.0, 10000.0, 5000.0, 2500.0, 1250.0]
					            }
				  );

		var map = L.map('map', {
			maxZoom: crs.options.resolutions.length,
			minZoom: 0,
			continuousWorld: true,
			zoomControl: true,
			initialZoom: 2,
			center: [-90, 0],
			crs: crs
		}).setView([-90, 0], initialZoom);

        function offLineIcon(color = "blue") {
            // This icon has everything off-line. Could it be generated from L.Icon.Default?

            // Possible colors: black, blue, green, grey, orange, red, violet, yellow.
            // Default color: blue

            var icon = L.icon({
                    iconUrl: static_url + "images/external/leaflet-color-markers/marker-icon-" + color + ".png",
                    shadowUrl: static_url + "images/external/marker-shadow.png",
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

        function loadAndPlotGeojsonPolygon(url, style) {
            $.getJSON(url,
                function(geojson)
                {
                    addGeojsonLayer(geojson, style);
                }
            );
        }

        function loadAndPlotGeojsonMarkers(url, icon) {
            $.getJSON("/api/events.geojson",
    			function(geojson)
			    {
				    var pointToLayer = function(feature, latlng) {
                        return L.marker(latlng, {icon: offLineIcon()});
				    };

    				var onEachFeature = function(feature, layer) {
	    				layer.bindPopup(feature.properties.id + " - " + feature.properties.text);
		    		};

				    L.geoJSON(geojson, {pointToLayer: pointToLayer, onEachFeature: onEachFeature}).addTo(map);
			    }
			);
        }

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

        loadAndPlotGeojsonPolygon(static_url + "maps/Coastline_high_res_polygon.geojson", antarctic_style);
        loadAndPlotGeojsonPolygon(static_url + "maps/Sub-antarctic_coastline_high_res_polygon_to30S.geojson", continents_style);


        loadAndPlotGeojsonMarkers(static_url + "api/events.geojson");

    // To add a marker (in Ushuaia)
    L.marker([-54.8, -68.3], {icon: offLineIcon("yellow")}).addTo(map);

    // Adds circle for up to 30 degrees.
    L.circle([-90, 0], 7150000).addTo(map);
}