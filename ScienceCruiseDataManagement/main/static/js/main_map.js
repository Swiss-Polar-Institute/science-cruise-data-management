function main() {
    antarctic_map_main();

    loadAndPlotGeojsonMarkers("/api/positions.geojson", 'positions');
    //loadAndPlotGeojsonLineString("/api/track.geojson");

}
