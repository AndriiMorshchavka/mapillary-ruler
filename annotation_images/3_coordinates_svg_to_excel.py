# This program extracts coordinates of circles in .svg-files and saves them into an Excel file

import xml.etree.ElementTree as ET
import os
from openpyxl import Workbook, load_workbook

def parse_svg(file_path):
    # Parse the SVG file to extract circle coordinates and IDs.
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Define the SVG namespace
    namespaces = {'svg': 'http://www.w3.org/2000/svg'}
    
    # Extract all circle elements using the namespace
    circles = root.findall('.//svg:circle', namespaces)
    
    # Print found circles
    print(f"Found {len(circles)} circles")
    
    data = []

    for circle in circles:
        cx = circle.get('cx')
        cy = circle.get('cy')
        identifier = circle.get('id', 'N/A')  # Use 'N/A' if no ID is present
        identifier = "0"+identifier[5:]
        print (f"{identifier}, {cx}, {cy}")
        
        if cx is not None and cy is not None:
            data.append({
                'id': identifier,
                'image_x_px': float(cx),
                'image_y_px': float(cy)
            })

    return data

def save_to_xlsx(data, output_file):
    # Save the extracted data to an Excel file.
    # Load an existing workbook and select the desired worksheet
    workbook = load_workbook(output_file)
    sheet = workbook["new_coordinates"]    
    # Write each row of data to the worksheet
    for row in data:
        sheet.append([row['id'], row['image_x_px'], row['image_y_px']])

    # Save the workbook to the specified file
    workbook.save(output_file)

# Specify the input SVG file and output Excel file
print ("Type the pKey")
pKey = input()
print (f"You have typed pKey: {pKey}")
directory = os.path.abspath(__file__)
svg_file = os.path.join (directory, fr"..//processed_images//.svg//{pKey}.svg")
output_xlsx = os.path.join(directory, r"..//3_ref_points.xlsx")

# Parse the SVG file and save the coordinates to an Excel file
data = parse_svg(svg_file)
save_to_xlsx(data, output_xlsx)

print(f"Coordinates have been saved to {output_xlsx}")
