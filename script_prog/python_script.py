import requests
import numpy as np
import math
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from tkinter import Tk, messagebox
import sys
import webbrowser
import folium
from geopy.distance import distance
import os
import easygui

# Function to ask the user if they want to continue
def ask_cont(question_string):
    root = Tk()
    root.withdraw()  # Hide the root window
    root.attributes("-topmost", True)

    # Display a yes/no messagebox
    result = messagebox.askyesno("Continue?", question_string)

    root.destroy()  # Destroy the root window

    return result

# Function to display an info message
def show_info_message(info_string):
    root = Tk()
    root.withdraw()  # Hide the root window

    # Display info message in the foreground
    root.lift()
    root.attributes("-topmost", True)
    root.focus_force()  # Ensure the root window gets focus

    messagebox.showinfo("Instructions", info_string)

    root.destroy()  # Destroy the root window

# Function to download and display the image
def download_and_display_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))

    fig, ax = plt.subplots()
    ax.imshow(img)
    points = []

    def onclick(event):
        nonlocal points
        if len(points) < 4 and event.button == 1 and event.key == 'control':
            x = int(event.xdata)
            y = int(event.ydata)
            points.append(x)
            points.append (y)
            #print (f"Point {round(len(points)/2)}: ({x}, {y})")
            ax.plot(x, y, 'ro')
            fig.canvas.draw()

        if len(points) == 4:
            fig.canvas.mpl_disconnect(cid)
            plt.close(fig)
            
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
    return img, points

# This function displays an image with points for better orientation when geolocating the point pair
def display_image_with_points(img, points):
    fig, ax = plt.subplots()
    ax.imshow(img)
    for i in range(0, len(points), 2):
        x, y = points[i], points[i + 1]
        ax.plot(x, y, 'ro')
    plt.title (label="Auxilliary image with your points")
    plt.show(block=False)

# This function returns the sorted coordinates (upper and lower point) from points array
def sort_point_coordinates (points):
    x_first = points [0]
    y_first = points [1]
    x_second = points [2]
    y_second = points [3]
    if y_first < y_second:
        x_up = x_first
        y_up = y_first
        x_down = x_second
        y_down = y_second
    else:
        x_up = x_second
        y_up = y_second
        x_down = x_first
        y_down = y_first
    return x_up, y_up, x_down, y_down

# This function calculates deastination points for compass angles lines
def calculate_destination_point(origin, angle_rad, distance):

    origin_x = origin [0]
    origin_y = origin [1]
    # Calculate the destination point in the projected coordinate system
    dx = distance * math.cos(angle_rad)
    dy = distance * math.sin(angle_rad)
    dest_x = origin_x + dx
    dest_y = origin_y + dy

    # Create the destination point
    dest_point = [dest_x, dest_y]

    return dest_point

# This function creates a map with a circle and compass angle lines
def base_map (camera_lat, camera_lon, angle_rad, new_point_lat = None, new_point_lon = None):
    camera_position = [camera_lat, camera_lon]
    # Create a folium map centered on computed_lon, computed_lat with zoom level 16
    m = folium.Map(location=camera_position, zoom_start=18)
    folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
       ).add_to(m)
    folium.CircleMarker(location=camera_position, 
                        radius=5, weight=10, color = 'blue').add_to(m)
    destination_center = calculate_destination_point (camera_position, angle_rad, 0.001)
    destination_right = calculate_destination_point (camera_position, angle_rad+math.radians (45), 0.001)
    destination_left = calculate_destination_point (camera_position, angle_rad-math.radians (45), 0.001)

    folium.PolyLine (locations=[camera_position, destination_center], 
                    weight = 3, color = 'blue').add_to(m)
    folium.PolyLine (locations=[camera_position, destination_left], 
                    weight = 2, color = 'blue').add_to(m)
    folium.PolyLine (locations=[camera_position, destination_right], 
                    weight = 2, color = 'blue').add_to(m)
    
    if new_point_lat is not None and new_point_lon is not None:
        folium.CircleMarker (location=[new_point_lat, new_point_lon], 
                                radius=3, weight=6, color = 'red').add_to (m)

    m.add_child(
        folium.ClickForLatLng(format_str='"[" + lat + "," + lng + "]"', alert=True)
    )
    m.add_child(folium.LayerControl())
    return m

# This is a basic function that is called inside main to collect the required data y pKey
def collect_input (pKey):
    # Define Mapillary API base URL
    base_url = "https://graph.mapillary.com"

    # Specify request parameters
    access_token = "MLY|7001510073286829|ea90511ea191e05c31eddbbf6247bf93"
    fields = "exif_orientation,thumb_original_url,computed_geometry,computed_compass_angle,computed_rotation,camera_parameters,camera_type,height,width,exif_orientation, computed_altitude"

    response = requests.get(f"{base_url}/{pKey}?access_token={access_token}&fields={fields}")
    if response.status_code == 200:
        show_info_message("Mapillary request successful")
        # Parse and process the response JSON
        data = response.json()
        # Camera type: e.g., perspective
        camera_type = data.get("camera_type")
        exif = data.get ("exif_orientation")
        # The net is trained only for perspective cameras
        if camera_type == "perspective" and exif == 1:        
            """
            Access the image data directly from the data dictionary
            """
            # Image URL for points in images
            image_url = data.get('thumb_original_url')

            # Computed geometry coordinates for the point on a map
            computed_geometry = data.get("computed_geometry", {})
            computed_coordinates = computed_geometry.get("coordinates", [None, None])
            computed_lat = computed_coordinates[1]
            computed_lon = computed_coordinates[0]

            # Retrieve image size
            image_height = data.get("height")
            image_width = data.get("width")
            # Retrieve compass angle
            compass_angle_deg = data.get("computed_compass_angle")
            compass_angle_rad = math.radians(compass_angle_deg)
            # Retrieve altitude [from sea level?]
            altitude = data.get("computed_altitude")
            # Retrieve rotation data
            computed_rotation = data.get("computed_rotation", [None, None, None])
            rotation_x = computed_rotation[0]
            rotation_y = computed_rotation[1]
            rotation_z = computed_rotation[2]
            # Camera parameters include focal length and distortion
            camera_parameters = data.get("camera_parameters", [None, None, None])
            focal_length = camera_parameters[0]
            k1 = camera_parameters[1]
            k2 = camera_parameters[2]

            """
            Get the points from user
            """
            cont = False
            while cont is False:
                show_info_message("Left Click + Ctrl (Strg) on the image to select two points, that lay above each other")
                # Display the image and get user input
                image, points = download_and_display_image(image_url)

                # Ask if the user wants to continue
                cont = ask_cont("Do you want to continue the program? No means repeat. \nIf you did not put two points before and press No, \nthe program will end")

            # Determine the upper and bottom points
            if len(points) == 4:
                x_up, y_up, x_down, y_down = sort_point_coordinates (points)
            else:
                show_info_message("No points selected. Program is interrupted.")
                sys.exit()

            """
            Georeference the selected point
            """
            show_info_message ("Now you are shown a map with camera position and field of view 90°")
            cont = False
            iteration = 1
            # Create a map with a camera position and compass angle demonstration
            lat_click = None
            lon_click = None        
            map_directory = os.path.join(os.path.abspath (__file__), '../../map.html')
            while cont is False:
                map_base = base_map (computed_lat, computed_lon, compass_angle_rad, lat_click, lon_click)
                map_base.save (map_directory)
                webbrowser.open(map_directory)
                if iteration == 1:
                    show_info_message ("Now, click on a one point on map that represents geoposition of the two points on the image you have selected earlier and press OK to copy coordinates into your clipboard. Then paste them into the terminal. \n\nLater, you will be able to see the point with your coordinates and adjust if needed")
                else:
                    cont = ask_cont("Do you want to continue the program? No means repeat.")
                    if cont is True:
                        continue
                    
                # Show info message for the first iteration
                display_image_with_points (image, points)
                lat_click = None
                lon_click = None
                while lat_click is None and lon_click is None:
                    try: 
                        coordinates_str = easygui.enterbox (f'Paste your coordinates from clipboard here (iteration {iteration}):')
                        # Remove brackets and split by comma
                        coordinates_str = coordinates_str.strip('[]')  # strip off the brackets
                        lat_str, lon_str = coordinates_str.split(',')  # split by comma

                        # Convert strings to float
                        lat_click = float(lat_str)
                        lon_click = float(lon_str)
                    except ValueError:
                        show_info_message ('Invalid coordinates. Try again')
                iteration +=1
                plt.close ()
            camera_position = (computed_lat, computed_lon)
            point_position = (lat_click, lon_click)
            dist = distance(camera_position, point_position).meters
            # Calculate projection on x-axis (longitude axis)
            x_projection = distance((computed_lat, computed_lon), (computed_lat, lon_click)).meters

            # Calculate projection on y-axis (latitude axis)
            y_projection = distance((computed_lat, computed_lon), (lat_click, computed_lon)).meters
            angle_rad = math.atan (y_projection/x_projection)
            
            """
            Assign data to input array
            """


            input_2 = np.zeros (13)
            input_2 [0] = image_width;
            input_2 [1] = image_height;
            input_2[2] = x_down - x_up
            input_2[3] = y_down - y_up
            input_2[4] = dist
            #input_2[5] = compass_angle_rad
            #input_2 [6] = angle_rad
            input_2[5] =  angle_rad - compass_angle_rad
            input_2[6] = altitude
            input_2[7] = focal_length
            input_2[8] = k1
            input_2[9] = k2
            input_2[10] = rotation_x
            input_2[11] = rotation_y
            input_2[12] = rotation_z

            print (f'pKey: {pKey},')
            print (f'Camera coordinates: ({computed_lat}; {computed_lon}),')
            print (f'Click coordinates: ({lat_click}; {lon_click}),')
            return input_2

        else:
            if camera_type != "perspective":
                show_info_message(f"This is camera type {camera_type}, try another image")
            if exif != 1:
                show_info_message(f"This is not exif-orientation 1, but {exif}, try another image")
    else:
        show_info_message(f'Request failed with status code {response.status_code}: {response.text}')

def main_function ():
    # Get id from user
    pKey  = easygui.enterbox("Type the Mapillary id")
    show_info_message(f"You have typed pKey: {pKey}")

    input_2 = collect_input(pKey)

    for i in range (0, 13):
        print (f'{input_2[i]}, ')

if __name__ == '__main__':
    main_function()