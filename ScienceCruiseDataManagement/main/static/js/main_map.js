function main() {
    antarctic_map_main();

    // To add a marker (in Ushuaia)
    // L.marker([-54.8, -68.3], {icon: offLineIcon("yellow")}).addTo(map);

    loadAndPlotGeojsonMarkers("/api/positions.geojson");
}