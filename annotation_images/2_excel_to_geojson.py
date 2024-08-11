# This program converts Excel-file with Mapillary data to geojson to enable image annotation in GIS program

import os
import openpyxl
import json
import geopandas as gpd

# Specify output directory
directory = os.path.abspath(__file__)
excel_path = os.path.join(directory, r"..//2_all_images.xlsx")
geojson_path = os.path.join(directory, "..//2_all_images.geojson")

# Load Excel file
wb = openpyxl.load_workbook(excel_path)
# Select the appropriate worksheet (assuming it's the first one)
ws = wb.active

# Create an empty dataframe
features = []

for image_index in range (2, 100):
    # Construct a feature
    column_counter = 1
    id_proj = ws.cell (row=image_index, column = column_counter).value
    if id_proj is None:
            continue
    column_counter+=1
    pKey = ws.cell (row = image_index, column=column_counter).value
    column_counter+=1
    thumb_url = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    lat = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    lon = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    altitude = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    compass_angle = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    camera_type = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    rot_x = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    rot_y = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    rot_z = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    focal_length = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    k1 = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    k2 = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    height = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    width = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    exif = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    atomic_scale = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    username = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    make = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1
    model = ws.cell (row=image_index, column = column_counter).value
    column_counter+=1

    map_url = f"https://www.mapillary.com/app/?lat={lat}&lng={lon}&z=17&pKey={pKey}&focus=photo"

    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat]
        },
        "properties": {
            "id_project": id_proj,
            "pKey" : pKey,
            "lat" : lat,
            "lon" : lon,
            "altitude" : altitude,
            "thumb URL": thumb_url ,
            "map URL" : map_url,
            "compass angle" : compass_angle,
            "rotation x" : rot_x,
            "rotation y" : rot_y,
            "rotation z" : rot_z,
            "focal length" : focal_length,
            "k1" : k1,
            "k2" : k2,
            "height" : height,
            "width" : width,
            "exif" : exif,
            "atomic_scale" : atomic_scale,
            "username" : username,
            "make" : make,
            "model" : model
        }
    }
    
    # Append feature to dataframe
    features.append(feature)

    # Return all values back to None in case by the next feature some value is missing
    id_proj = None
    pKey = None
    lat = None
    lon = None
    compass_angle = None
    camera_type = None
    rot_x = None
    rot_y = None
    rot_z = None
    focal_length = None
    k1 = None
    k2 = None
    height = None
    width = None
    map_url = None
    thumb_url = None

# Declare a geojson
geojson = {
"type": "FeatureCollection",
"features": features
}

# Append all data to geojson (to avoid deleting, otherwise write - "w")
with open(geojson_path, "a") as f:
                json.dump(geojson, f, indent=2)

# Convert the whole geojson to GeoDataFrame and reproject
gdf = gpd.GeoDataFrame.from_features(geojson["features"])
gdf = gdf.set_crs("EPSG:4326")  # Original
gdf = gdf.to_crs("EPSG:3857")

# Save the reprojected GeoJSON
geojson_reprojected_path = os.path.join(directory, r"..//2_all_images_3857.geojson")
gdf.to_file(geojson_reprojected_path, driver="GeoJSON")