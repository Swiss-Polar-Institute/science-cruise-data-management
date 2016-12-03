Original files (*.shp* downloaded from "SCAR Antarctic Digital Database". See license.txt for the license.

Then to convert them to GeoJSON (so Leaflet can read them) we executed:

ogr2ogr -f GeoJSON -simplify 1000 -t_srs EPSG:3031 Coastline_high_res_polygon.geojson Coastline_high_res_polygon.shp
ogr2ogr -f GeoJSON -simplify 1000 -t_srs EPSG:3031 Sub-antarctic_coastline_high_res_polygon_to30S.geojson Sub-antarctic_coastline_high_res_polygon_to30S.shp

