function main(static_url) {
		proj4.defs("EPSG:3031","+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs");
		proj4.defs("urn:ogc:def:crs:EPSG::3031","+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs");
		var initialZoom = 0;

		var crs = new L.Proj.CRS('EPSG:3031', '+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs',
		                        {
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

		function makeMap(data, style) {
			var darkMap = L.tileLayer('').addTo(map);

			boroughLayer = L.Proj.geoJson(data, {
				style: style
				}
				).addTo(map);
		}
		$.getJSON(static_url + "maps/Coastline_high_res_polygon.geojson",
			function(data)
			{
				var style = function(feature)
						{
							return { color: 'black',
								weight: 1,
								fillColor: 'white',
								fillOpacity: 1
					      			}
						};

				makeMap(data, style);
			}
		);
		$.getJSON(static_url + "maps/Sub-antarctic_coastline_high_res_polygon_to30S.geojson",
			function(data)
			{
				var style = function(feature)
					{
						return { color: 'black',
							weight: 1,
							fillColor: 'green',
							fillOpacity: 1
							}
					};

				makeMap(data, style);
			}
		);


		$.getJSON("/api/events.geojson",
			function(data)
			{
				var pointToLayer = function(feature, latlng) {

					    // This icon has everything off-line. Could it be generated from L.Icon.Default?
					    var icon2 = L.icon({
						iconUrl: static_url + "images/marker-icon.png",
						shadowUrl: static_url + "images/marker-shadow.png",
						iconSize: [25, 41],
						iconAnchor: [12, 41],
						popupAnchor: [1, -34],
						shadowSize: [41, 41]
					    });




					return L.marker(latlng, {icon: icon2});

				};

				var onEachFeature = function(feature, layer) {
					layer.bindPopup(feature.properties.id + " - " + feature.properties.text);

				};

				L.geoJSON(data, {pointToLayer: pointToLayer, onEachFeature: onEachFeature}).addTo(map);

			}
		);

    // This icon has everything off-line. Could it be generated from L.Icon.Default?
    var icon = L.icon({
        iconUrl: static_url + "images/marker-icon.png",
        shadowUrl: static_url + "images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });


    L.marker([-54.8, -68.3], {icon: icon}).addTo(map);

    // Adds circle for up to 30 degrees.
    L.circle([-90, 0], 7150000).addTo(map);
}