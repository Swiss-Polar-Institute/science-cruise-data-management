function main() {
    antarctic_map_main();

    loadAndPlotGeojsonMarkers("/api/positions.geojson");
    loadAndPlotGeojsonLineString("/api/track.geojson");

}