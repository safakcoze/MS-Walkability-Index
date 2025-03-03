import geopandas as gpd

# MS_DISTRICTS ---------------------------
# Read the MS_Districts file using GeoPandas
gdf_districts = gpd.read_file("Data/ms_districts.geojson")

# Reproject to EPSG:4326 (WGS 84)
gdf_districts = gdf_districts.to_crs(epsg=4326)

# Save the reprojected GeoJSON
gdf_districts.to_file("Data/ms_districts_prj.geojson", driver="GeoJSON")

# MS_STREETS ---------------------------
# Read the MS_Strets file using GeoPandas
gdf_streets = gpd.read_file("Data/ms_streets.geojson")

# Reproject to EPSG:4326 (WGS 84)
gdf_streets = gdf_streets.to_crs(epsg=4326)

# Save the reprojected GeoJSON
gdf_streets.to_file("Data/ms_streets_prj.geojson", driver="GeoJSON")
