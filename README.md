This explanation describes how to annotate new images to train a net for building height estimation from Mapillary API (Directory annotation_images) or how to use the trained nets to estimate building heights (script_prog).

Process of images Annotation (annotation_images):
0. Create in annotation_images the following empty folders in annotation_images:
	/
 
	├── new_images/
 
	├── processed_images/
 
    		├── .original/
      
    		├── .ai/
      
    		└── .svg/
1. Search for images fitting your criteria and save them and their data using 1_image_data_request.py. The images are saved to new_images folder, data - to 1_new_images.xlsx. Assign project IDs to the images in the first column that correspond to your Needs.
2. Cut data from 1_new_images.xlsx to 2_all_images.xlsx and save the data with camera Position coordinates to geojson using script 2_excel_to_geojson.py. The geojson reprojected into EPSG:3857 is saved into 2_all_images_3857.geojson.
3. Cut each new image from new_images to proccessed_images/original and open them with Adobe Illustrator or any similar vector image processing tool that allows creating importing jpg, adding circles, and exporting to SVG. Examples of images in original format and as SVG can be found in branch examples-building-height. For Adobe Illustrator:
	3.1. Open original .jpg and adjust artboard.
	3.2. Add circles and name them correctly. In my work, the first three numbers stood for the project id of the Image, next two symbols - for the position of points pair in the image from left to right, and the last one was either 1 for the top point or 2 for bottom point - e.g., 048062.
	3.3. Then, geolocate the projections of points pair on the ground in QGIS. In the project 3_annotation_qgis.qgz, the 2_all_images_3857.geojson is open, as well as 3_ref_points_	3857.geojson with points from my project geolocated. Add your points to the 3_ref_points_3857.geojson and name them correctly - e.g., the first five numbers of points names that correspond to the points pair.
	3.4. Save points coordinates from .svg to an Excel file using 3_coordinates_svg_to_excel.py. The coordinates are saved to the worksheet new_coordinates in 3_ref_points.xlsx.
	3.5. Assign to each point pair in the worksheet new_coordinates in 3_ref_points.xlsx the Building height for ground truth data.
4. Create lines in your QGIS project using the tool "Join by Lines (Hub Lines)" from processing toolbox. Refer to 4_how_to_create_lines.png. 
5. Calculate the length and angles of the lines from the lines layer by copying fields from the layer 5_lines_attributes_example in the QGIS project 3_annotation_qgis.qgz or create new virtual fields as in 5_how_to_calculate_lines.png. Export the layer as Excel to 5_lines_data.xlsx.
6. Combine all data to matlab_table.xlsx in the folder script_prog: 2_all_images.xlsx to worksheet image_data_all, 3_ref_points.xlsx to worksheet ref_coordinates, and 5_lines_data to worksheet lines. Then, combine all layers into an input for MATLAB Feedforward Neural Network on worksheet matlab_input_all. You can then filter the images by user as I did with the images of stefanhrt or filter them by the outlying values of building height or distance.

Process of using or training neural networks (script_prog):
1. Train neural network from the required worksheet of matlab_table.xlsx using sgript_neural.m. You can adjust the worksheet used, data range, columns used as input, data split (training-validation-testing), and the way to handle the optimization algorthms and hidden layers number.
2. Use matlab_main_script.m to use neural network. In the current code, you can compare two neural networks. 
3. The MATLAB program accesses compiled Python program in __py_cache__/python_script.cpython-311.pyc. You can change the code in python_script.py and then recompile using compile.py.
