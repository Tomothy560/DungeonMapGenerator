import numpy
import csv
import os
import shutil
import json
import re
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from map_generator.structures import*


class FileWriteHelper:

    def __init__(self):
        a = 1

# file name
        
    def is_valid_file_name(self, name):
        # Define the regular expression pattern for a valid file name
        pattern = r'^[a-zA-Z0-9_-]+$'

        # Check if the name matches the pattern
        match = re.match(pattern, name)
        
        return bool(match)
    
# general
    
    def delete(self, folder_path):
        shutil.rmtree(folder_path)

# csv function
    def csv_to_array(self, file_path, skip_line):
        data = numpy.genfromtxt(file_path, delimiter=',', skip_header=skip_line, dtype=None, encoding='utf-8')
        return data
    def write_array_to_csv(self, file_path, data):
        with open(file_path, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(data)
    def clear_csv(self, file_path):
        with open(file_path, 'w', newline='') as file:
            file.truncate()
    def create_empty_csv(self, file_path):
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

# properties file function

    def load_properties(self, file_path):
        properties = {}
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    properties[key.strip()] = value.strip()
        return properties #as a dictionary

    def save_properties(self, file_path, properties):
        with open(file_path, 'w') as file:
            for key, value in properties.items():
                file.write(f'{key}={value}\n')

# txt file functions
    def load_txt_as_string(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")
            return None
        except IOError:
            print(f"Error reading file '{file_path}'.")
            return None
        
    def append_to_txt(self, file_path, content):
        try:
            with open(file_path, 'a') as file:
                file.write(content)
            print(f"Content appended to file '{file_path}' successfully.")
        except IOError:
            print(f"Error appending content to file '{file_path}'.")

    def clear_txt_file(self,file_path):
        try:
            with open(file_path, 'w') as file:
                file.truncate(0)
            print(f"File '{file_path}' cleared successfully.")
        except IOError:
            print(f"Error clearing file '{file_path}'.")

#folder
    def clear_folder(self,folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                # Remove files
                os.remove(file_path)
            elif os.path.isdir(file_path):
                # Remove subdirectories
                shutil.rmtree(file_path)

    def create_folder(self,folder_path):
        os.makedirs(folder_path)

    def return_items_in_folder(self,folder_path):
        # Get a list of all files and folders in the directory
        file_list = os.listdir(folder_path)
        return file_list
    
    def path_exist(self, folder_path):
        return os.path.exists(folder_path)
#jsons
    def write_array_of_dicts_to_json(self, data, file_path):
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    def clear_json_file(self, file_path):
        with open(file_path, 'w') as json_file:
            json_file.truncate(0)
    def json_to_dict(self, file_path):
        with open(file_path, 'r') as f:
            data_dict = json.load(f)
        return data_dict
    def json_to_array(self, file_path):
        with open(file_path, 'r') as f:
            array = json.load(f)
        return array
    def dict_to_json(self, file_path, my_dict):
        with open(file_path, "w") as json_file:
            json.dump(my_dict, json_file)

# structure extraction
            
    def save_file_to_structure_list(self,battle_map_save_file):
        with open(battle_map_save_file+"\\json_lists\\structure_list.json") as file:
            structure_array = json.load(file)

        structure_list = []

        for structure_dict in structure_array:
            #extract structure layout
            structure_layout = self.csv_to_array(battle_map_save_file+"\\structure_list_layout\\"+structure_dict["id_value"]+".csv",0) 
            x1 = structure_dict['x1']
            y1 = structure_dict['y1']
            x2 = structure_dict['x2']
            y2 = structure_dict['y2']
            structure_type = structure_dict['structure_type']
            id = structure_dict['id_value']            
            
            if structure_dict["structure_type"] == []: #structure 0 
                new_structure = Structure(x1, y1, x2, y2,structure_type, id)
            elif structure_dict["structure_type"] == "rectangular_room": #rectangular_room
                new_structure = StructureRectangularRoom(x1, y1, x2, y2, id, structure_dict['NESW'])
            elif structure_dict["structure_type"] == "maze": #"maze"
                new_structure = StructureMaze(x1, y1, x2, y2, id)
            elif structure_dict["structure_type"] == "circular_room": #"circular_room"
                new_structure = StructureCircularRoom(x1, y1, x2, y2, id, structure_dict['perfect_circle'])
            elif structure_dict["structure_type"] == "corridor": #"corridor"
                new_structure = StructureCorridor(x1, y1, x2, y2, id, structure_dict['orientation'])
            elif structure_dict["structure_type"] == "L_room": #"L_room"
                new_structure = StructureLRoom(x1, y1, x2, y2, id, structure_dict['midx'],structure_dict['midy'],structure_dict['missing_q'])
            
            new_structure.grid = structure_layout
            structure_list.append(new_structure)
        return structure_list

# png
    def convert_png_to_pdf(self, png_path, pdf_path):
        # Open the PNG image
        image = Image.open(png_path)

        # Create a new PDF file
        c = canvas.Canvas(pdf_path, pagesize=letter)

        # Set the size of the PDF page based on the image size
        c.setPageSize((image.width, image.height))

        # Draw the PNG image on the PDF canvas
        c.drawImage(png_path, 0, 0)

        # Save the PDF file
        c.save()
    
    def convert_png_to_jpeg(png_path, jpeg_path):
        # Open the PNG image
        image = Image.open(png_path)

        # Convert the image to JPEG
        image.convert('RGB').save(jpeg_path, 'JPEG')