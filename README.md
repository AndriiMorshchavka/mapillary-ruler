# Building Height Estimation using Mapillary API

This guide explains how to annotate new images for training a network to estimate building heights using Mapillary API data, and how to use trained networks for estimation.

## Image Annotation (`annotation_images`)

1. **Directory Setup**

   Create the following folders in `annotation_images`:
	
 	annotation_images/

		├── new_images/

		└── processed_images/

    			├── .original/
   
    			├── .ai/
   
    			└── .svg/


3. **Image Search and Data Collection**

- Run `1_image_data_request.py` to search for images and save them to `new_images/` and their data to `1_new_images.xlsx`.
- Assign project IDs in `1_new_images.xlsx`.

3. **Data Preparation**

- Move data from `1_new_images.xlsx` to `2_all_images.xlsx`.
- Use `2_excel_to_geojson.py` to convert data to GeoJSON, saved as `2_all_images_3857.geojson`.

4. **Image Processing**

- Move images from `new_images/` to `processed_images/.original`.
- Open each image in Adobe Illustrator (or similar) to add circles and export them as SVGs.
- Name circles according to project ID, point pair position, and point type (e.g., `048062`).

5. **Geolocation**

- Geolocate point pairs in QGIS using `3_annotation_qgis.qgz` and save them to `3_ref_points_3857.geojson`.
- Extract coordinates from SVGs with `3_coordinates_svg_to_excel.py` and save to `3_ref_points.xlsx`.

6. **Line Creation**

- Use QGIS's "Join by Lines" tool to create lines as shown in `4_how_to_create_lines.png`.
- Calculate line lengths and angles, referencing `5_lines_attributes_example` in QGIS, and export to `5_lines_data.xlsx`.

7. **Data Compilation**

- Merge all data into `matlab_table.xlsx` in the `script_prog` folder:
  - `2_all_images.xlsx` to `image_data_all`
  - `3_ref_points.xlsx` to `ref_coordinates`
  - `5_lines_data.xlsx` to `lines`
- Prepare data for MATLAB Neural Network in `matlab_input_all` and filter images as needed.

