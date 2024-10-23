from helpers.file_write_helper import FileWriteHelper
from helpers.color_helper import ColorHelper

from front_end.map_class import Map
from map_generator.structures import *

import PySimpleGUI as sg
import numpy
import math
import secrets
import threading

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import PIL.Image
import io
import os
import time

class MainFrontEnd:
    def __init__(self, file_paths):
        # helper functions
        self.fwh = FileWriteHelper()
        self.color_helper = ColorHelper()
    # - - - source Path - - - #

        self.file_paths = file_paths

        self.cell_types_file_path = self.file_paths['application_path'] + self.file_paths['cell_types.csv']
        self.structure_types_file_path = self.file_paths['application_path']+self.file_paths['structure_types.csv']
        self.cell_types_texture_hiearchy_file_path = self.file_paths['application_path']+self.file_paths['cell_type_texture_hiearchy.csv']

        self.save_file_path = self.file_paths['application_path'] + self.file_paths['save']

        self.settings_file_path = self.file_paths['application_path'] + "\\src\\assets\\json_files\\settings.json"
        self.windows_settings_file_path = self.file_paths['application_path']+self.file_paths['windows_settings.json']

        self.textures_file_path = self.file_paths['application_path']+self.file_paths['textures']

        self.cell_types_csv = []
        self.structure_types_csv = []
        self.cell_types_texture_hiearchy = []

        self.window_settings = {}
        self.settings = {}

        self.extract_all_files()

    # Apearances
    
        sg.change_look_and_feel(self.settings["default_appearance"])

    # - - - PyGUI Layouts - - - #

            # Windows Settings

        self.windows_settings_file_path = self.file_paths['application_path'] + "\\src\\assets\\json_files\\windows_settings.json"
        self.windows_settings = self.fwh.json_to_dict(self.windows_settings_file_path)
        
        self.fonts = self.windows_settings["AllScreens"]["fonts"]
        self.initialization_parameters = self.windows_settings["AllScreens"]["initialization_parameters"]
        self.window_icons_file_path = self.file_paths['application_path']+self.file_paths['window_icons']

    # - - - Window Opening Specific - - - #

        self.window_home = None
        self.window_new_map = None
        self.window_open_existing_file = None
        self.window_settings = None

        self.window_map_editor = {
            "SelectLayer": None,
            "Panel1": None,
            "Panel2": None,
            "Panel3": None,
            "Display": None
        }

        self.window_pop_up_input = None
        self.window_pop_up_loading = None
        self.window_pop_up_export_map = None


    # - - - Cache - - - #
        self.cache_map = None
        self.cache_exported_map = None # full file path
        try:
            self.open_existing_file_screen_selected_map = self.fwh.return_items_in_folder(self.file_paths["application_path"]+self.file_paths["save"])[0]
        except Exception:
            self.open_existing_file_screen_selected_map = ""
    # - - - Micellaneoous - - - #
        self.missing_texture_icon = self.window_icons_file_path+"\\no_preview_avaible_icon.png"

# basic file extraction
        
    def extract_all_files(self):
        def csv_to_array(file_path, skipline):
            data = numpy.genfromtxt(file_path, delimiter=',', skip_header=skipline, dtype=str, encoding='utf-8')
            return data
        self.cell_type_texture_hiearchy = self.fwh.csv_to_array(self.cell_types_texture_hiearchy_file_path,0)

        temp = csv_to_array(self.cell_types_file_path, 1)
        for i in temp:
            i[2] = "#"+str(i[2])
        self.cell_types_csv = temp

        temp = self.fwh.csv_to_array(self.structure_types_file_path, 1) #skips 1 line of header
        self.structure_types_csv = temp
        return_a = []
        for i in temp:
            if i[1] == "None":
                i[1] = None
            return_a.append(i[1])
        self.structure_types = return_a

        self.settings = self.fwh.json_to_dict(self.settings_file_path)
        self.windows_settings = self.fwh.json_to_dict(self.windows_settings_file_path)

# return layouts to bypass reuse layout rule
        
    def layout_home_screen(self):
        menu_def = [['File', ['New', 'Open', 'Exit', ]],  ['Help', 'About...'], ]

        layout = [
            [sg.Menu(menu_def)],    
            [sg.Text(""), sg.Text('Battle Map Generator',font=self.fonts["font_heading_1"]), sg.Text("")],
            [sg.Text("                     "), sg.Button('New Map',font=self.fonts["font_button"], size=(10, 1)), sg.Text("    ")],
            [sg.Text("                     "), sg.Button('Open File',font=self.fonts["font_button"], size=(10, 1)), sg.Text("    ")],
            [sg.Text("                     "), sg.Button('Settings',font=self.fonts["font_button"], size=(10, 1)), sg.Text("    ")]
        ]
        return layout
    def layout_new_map_screen(self): # not finished

        input_size = (10,1)
        label_size = (20,1)
        button_size = (8,1)

        combo_size = (15,1)
        combo_label_size = (14,1)

        chunk_x = ""
        chunk_y = ""
        cell_resolution = str(self.settings['default_cell_resolution'])
        chunk_size = str(self.settings['default_chunksize'])
        texture = str(self.settings['default_texture'])

        texture_combo = self.fwh.return_items_in_folder(self.textures_file_path)

        layout = [
            [sg.Text(""), sg.Text('Create a New Map',font=self.fonts["font_heading_2"]), sg.Text("")],
            [sg.Text("")],
            [sg.Text("Name:", size=label_size, font=self.fonts["font_text"]),                       sg.Input(key="-NAME-", size=input_size, font=self.fonts["font_input"])],
            [sg.Text("Number of Chunks in X:", size=label_size, font=self.fonts["font_text"]),      sg.Input(key="-CHUNK_X-", size=input_size, font=self.fonts["font_input"], default_text=chunk_x),        sg.Text("Number of Chunks in Y:", size=label_size, font=self.fonts["font_text"]),    sg.Input(key="-CHUNK_Y-", size=input_size, font=self.fonts["font_input"], default_text=chunk_y)],
            [sg.Text("Chunk Size:", size=label_size, font=self.fonts["font_text"]),                 sg.Input(key="-CHUNK_SIZE-", size=input_size, font=self.fonts["font_input"],default_text=chunk_size),   sg.Text("Cell Resolution:", size=label_size, font=self.fonts["font_text"]),          sg.Input(key="-CELL_RESOLUTION-", size=input_size, font=self.fonts["font_input"], default_text=cell_resolution)],
            [sg.Text("Texture Pack:", size=combo_label_size, font=self.fonts["font_text"]),         sg.Combo(texture_combo, key="-TEXTURE-",size=combo_size, font=self.fonts["font_input"], default_value=texture, readonly=True)],
            [sg.Button("Cancel",font=self.fonts["font_button"], size=button_size), sg.Button("Reset",font=self.fonts["font_button"], size=button_size), sg.Text("",font=self.fonts["font_button"], size=(22 ,1)), sg.Button("Save and Proceed",font=self.fonts["font_button"], size=(15,1))]
        ]
        return layout
    def layout_open_existing_file_screen(self): # not finished
        # Actual code
        def convert_to_bytes(file_or_bytes, sizex, sizey, selection=False):
            img = PIL.Image.open(file_or_bytes)
            resized_img = img.resize((sizex, sizey))
            if selection: # add a border
                white_glowing_border = PIL.Image.open(self.window_icons_file_path+"\\white_glowing_border.png").resize((sizex, sizey))
                resized_img.paste(white_glowing_border, (0, 0), mask=white_glowing_border)
            with io.BytesIO() as bio:
                resized_img.save(bio, format="PNG")
                del resized_img
                return bio.getvalue()     
        def get_resized_size(screen_sizex, screen_sizey, ratio):
            if screen_sizex > screen_sizey:
                if ratio >= 1:
                    sizey = screen_sizey
                    sizex = math.floor(screen_sizey / ratio)
                else:
                    sizex = screen_sizex
                    sizey = math.floor(screen_sizey * ratio)
            else:
                if ratio <= 1:
                    sizey = screen_sizey
                    sizex = math.floor(screen_sizey / ratio)
                else:
                    sizex = screen_sizex
                    sizey = math.floor(screen_sizey * ratio)
            return sizex, sizey
        def is_not_png_blank(image_path):
            start_time = time.time()
            if os.path.exists(image_path) == False:
                return False
            image = Image.open(image_path)
            image = image.convert('RGBA')
            width, height = image.size

            sample_points = 1000
            step_size = max(width * height // sample_points, 1)
            pixels = image.getdata()

            return_val = False
            for i in range(0, width * height, step_size):
                pixel = pixels[i]
                if pixel[3] != 0:
                    return_val = True

            end_time = time.time()
            print("Elapsed time:", end_time - start_time, "seconds")
            return return_val
        
        start_time = time.time()

        label_size = (20,1)
        button_size = (10,1)

        combo_size = (17,1)

        combo = self.fwh.return_items_in_folder(self.file_paths["application_path"]+self.file_paths["save"])
        map_image_size = (200, 150)

        map_image_list = []
        map_image_name = []

        end_time = time.time()
        print("Pre-Processing: ", end_time - start_time)

        for file_name in combo:
            start_time = time.time()
            map_file_path = self.file_paths["application_path"]+self.file_paths["save"]+"\\"+file_name
            ratio = self.fwh.json_to_dict(map_file_path+"\\json_lists\\map_properties.json")["chunk_y"] / self.fwh.json_to_dict(map_file_path+"\\json_lists\\map_properties.json")["chunk_x"]     
            if is_not_png_blank(map_file_path+"\\images\\cache_rendered_image.png"):
                image_file_path = map_file_path+"\\images\\cache_rendered_image.png"
            elif is_not_png_blank(map_file_path+"\\images\\cache_layout_image.png"):
                image_file_path = map_file_path+"\\images\\cache_layout_image.png"
            elif is_not_png_blank(map_file_path+"\\images\\cache_structure_layer_image.png"):
                image_file_path = map_file_path+"\\images\\cache_structure_layer_image.png"
            else: # place holder missing texture file
                image_file_path = self.missing_texture_icon
                ratio = 1
            sizex, sizey = get_resized_size(map_image_size[0], map_image_size[1], ratio)

            if self.open_existing_file_screen_selected_map == file_name:
                map_image_list.append(convert_to_bytes(image_file_path ,sizex, sizey))
                # Disable white border
                # map_image_list.append(convert_to_bytes(image_file_path ,sizex, sizey, selection=True))
            else:
                map_image_list.append(convert_to_bytes(image_file_path ,sizex, sizey))
            map_image_name.append(file_name)
            end_time = time.time()
            print("- - - ", file_name, ": ", end_time - start_time)
        start_time = time.time()
        ratio = 1
        sizex, sizey = get_resized_size(map_image_size[0], map_image_size[1], ratio)
        map_image_name.append("New Map")
        map_image_list.append(convert_to_bytes(self.window_icons_file_path+"\\pencil_icon.png",sizex, sizey))

        max_map_per_row = 5-1
        row_needed = math.ceil(len(map_image_name)/max_map_per_row)
        layout_maps_grid = []
        index = 0

        while len(map_image_name) < row_needed*max_map_per_row +1:
            map_image_list.append(False)
            map_image_name.append(None)

        def return_sg_image(asdasdasd):
            if asdasdasd == False:
                return sg.Image(size=map_image_size, key='-CANVAS-')
            else:
                return sg.Image(size=map_image_size, key='-CANVAS-', data=asdasdasd)
        def return_sg_text(awdawdawd):
            if awdawdawd == None:
                return sg.Text("", size=(math.floor(2+map_image_size[0]/10),1))
            else:
                return sg.Text(awdawdawd, font=self.fonts["font_text"], size=(math.floor(map_image_size[0]/10),1))
        
        for _ in range(0, row_needed):
            print("Length of List: "+str(len(map_image_name)))
            print(_)
            new_row_image = []
            new_row_text = []
            for a in range(0, max_map_per_row):
                new_row_image.append(return_sg_image(map_image_list[index+a]))
                new_row_text.append(return_sg_text(map_image_name[index+a]))
            index += max_map_per_row
            layout_maps_grid.append(new_row_text)
            layout_maps_grid.append(new_row_image)

        # residual maps
        combo.append("New Map")

        layout_1st = [
            [sg.Text(""), sg.Text('Open an Existing Map File',font=self.fonts["font_heading_3"]), sg.Text("", size=label_size), sg.Text("", size=label_size), sg.Button("Delete",font=self.fonts["font_button"], size=button_size), sg.Button("Export",font=self.fonts["font_button"], size=button_size)],
        ]
        layout_2nd = [
            [sg.Button("Select Map",font=self.fonts["font_button"], size=button_size),         sg.Combo(combo, key="-COMBO-",size=combo_size, font=self.fonts["font_input"], default_value=self.open_existing_file_screen_selected_map, readonly=True)],
            [sg.Button("Back",font=self.fonts["font_button"], size=button_size), sg.Button("Proceed",font=self.fonts["font_button"], size=button_size)]
        ]
        layout = layout_1st + layout_maps_grid + layout_2nd

        self.close_window("LoadingPopUp")
        end_time = time.time()
        print("Post-Processing: ", end_time - start_time)
        return layout
    def layout_settings_screen(self):
        cell_resolution = str(self.settings['default_cell_resolution'])
        chunk_size = str(self.settings['default_chunksize'])
        texture = str(self.settings['default_texture'])
        default_appearance = str(self.settings['default_appearance'])

        texture_options = self.fwh.return_items_in_folder(self.textures_file_path)
        appearance_options = [
            'Black', 'BlueMono', 'BluePurple', 'BrightColors', 'BrownBlue', 'Dark', 'Dark2', 'DarkAmber', 'DarkBlack', 'DarkBlack1', 'DarkBlue', 'DarkBlue1', 'DarkBlue10', 'DarkBlue11', 'DarkBlue12', 'DarkBlue13', 'DarkBlue14', 'DarkBlue15', 'DarkBlue16', 'DarkBlue17', 'DarkBlue2', 'DarkBlue3', 'DarkBlue4', 'DarkBlue5', 'DarkBlue6', 'DarkBlue7', 'DarkBlue8', 'DarkBlue9', 'DarkBrown', 'DarkBrown1', 'DarkBrown2', 'DarkBrown3', 'DarkBrown4', 'DarkBrown5', 'DarkBrown6', 'DarkBrown7', 'DarkGreen', 'DarkGreen1', 'DarkGreen2', 'DarkGreen3', 'DarkGreen4', 'DarkGreen5', 'DarkGreen6', 'DarkGreen7', 'DarkGrey', 'DarkGrey1', 'DarkGrey10', 'DarkGrey11', 'DarkGrey12', 'DarkGrey13', 'DarkGrey14', 'DarkGrey15', 'DarkGrey2', 'DarkGrey3', 'DarkGrey4', 'DarkGrey5', 'DarkGrey6', 'DarkGrey7', 'DarkGrey8', 'DarkGrey9', 'DarkPurple', 'DarkPurple1', 'DarkPurple2', 'DarkPurple3', 'DarkPurple4', 'DarkPurple5', 'DarkPurple6', 'DarkPurple7', 'DarkRed', 'DarkRed1', 'DarkRed2', 'DarkTanBlue', 'DarkTeal', 'DarkTeal1', 'DarkTeal10', 'DarkTeal11', 'DarkTeal12', 'DarkTeal2', 'DarkTeal3', 'DarkTeal4', 'DarkTeal5', 'DarkTeal6', 'DarkTeal7', 'DarkTeal8', 'DarkTeal9', 'Default', 'Default1', 'DefaultNoMoreNagging', 'GrayGrayGray', 'Green', 'GreenMono', 'GreenTan', 'HotDogStand', 'Kayak', 'LightBlue', 'LightBlue1', 'LightBlue2', 'LightBlue3', 'LightBlue4', 'LightBlue5', 'LightBlue6', 'LightBlue7', 'LightBrown', 'LightBrown1', 'LightBrown10', 'LightBrown11', 'LightBrown12', 'LightBrown13', 'LightBrown2', 'LightBrown3', 'LightBrown4', 'LightBrown5', 'LightBrown6', 'LightBrown7', 'LightBrown8', 'LightBrown9', 'LightGray1', 'LightGreen', 'LightGreen1', 'LightGreen10', 'LightGreen2', 'LightGreen3', 'LightGreen4', 'LightGreen5', 'LightGreen6', 'LightGreen7', 'LightGreen8', 'LightGreen9', 'LightGrey', 'LightGrey1', 'LightGrey2', 'LightGrey3', 'LightGrey4', 'LightGrey5', 'LightGrey6', 'LightPurple', 'LightTeal', 'LightYellow', 'Material1', 'Material2', 'NeutralBlue', 'Purple', 'Python', 'PythonPlus', 'Reddit', 'Reds', 'SandyBeach', 'SystemDefault', 'SystemDefault1', 'SystemDefaultForReal', 'Tan', 'TanBlue', 'TealMono', 'Topanga'
            ]
        
        layout = [
            [sg.Text("   Default Chunk Size", font=self.fonts["font_text"], size=(30, 1)),          sg.Input(key='-DEFAULT_CHUNK_SIZE-',font=self.fonts["font_input"], default_text=chunk_size, size=(50, 1))],
            [sg.Text("   Default Cell Resolution", font=self.fonts["font_text"], size=(30, 1)),     sg.Input(key='-DEFAULT_CELL_RESOLUTION-',font=self.fonts["font_input"], default_text=cell_resolution, size=(50, 1))],
            [sg.Text("   Default Texture", font=self.fonts["font_text"], size=(30, 1)),             sg.Combo(texture_options, key='-DEFAULT_TEXTURE-',font=self.fonts["font_input"], default_value=texture, size=(48, 1), readonly=True)],
            [],
            [sg.Text("   Appearances", font=self.fonts["font_text"], size=(30, 1)),                 sg.Combo(appearance_options,key='-APPEARANCE-',font=self.fonts["font_input"], default_value=default_appearance, size=(48, 1), readonly=True)],
            [],
            [sg.Button('Back',font=self.fonts["font_button"], size=(10, 1)),                       sg.Text("", size=(46,1)),sg.Button('Reset',font=self.fonts["font_button"], size=(10, 1)), sg.Button('Save',font=self.fonts["font_button"], size=(10, 1))]
        ]

        # magin cannot be 3 or less

        return layout

    # popups

    def layout_export_map_pop_up(self):
        layout = [ 
            [sg.Text(""), sg.Text('Export Map',font=self.fonts["font_heading_3"]), sg.Text("")],
            [sg.Text(""), sg.Radio('PDF', "file_format", font=self.fonts["font_text"], size=(10, 1), default=False, key="-PDF-")],
            [sg.Text(""), sg.Radio('PNG', "file_format", font=self.fonts["font_text"], size=(10, 1), default=True, key="-PNG-")],
            [sg.Text(""), sg.Radio('JPEG', "file_format", font=self.fonts["font_text"], size=(10, 1), default=False, key="-JPEG-")],
            [sg.Text(" - - - ", font=self.fonts["font_text"], size=(10, 1))],
            [sg.Text(""), sg.Radio('RGB', "color_format", font=self.fonts["font_text"], size=(10, 1), default=True, key="-RGB-")],
            [sg.Text(""), sg.Radio('CMYK', "color_format", font=self.fonts["font_text"], size=(10, 1), default=False, key="-CMYK-")],
            [sg.Text(" - - - ", font=self.fonts["font_text"], size=(10, 1))],
            [sg.Button('Confirm Export',font=self.fonts["font_button"], size=(13, 1))],
            [sg.Text("", font=self.fonts["font_text"], size=(30, 1), key="-LOADING_TEXT-")]         
        ]
        return layout
    def layout_loading_pop_up(self, loading_text="Wait for Completion: "):
        layout = [ 
            [sg.Text(""), sg.Text(loading_text,font=self.fonts["font_text"]), sg.Text("0%",font=self.fonts["font_text"], key="-PERCENTAGE-"), sg.Text("")],
            [sg.Image(size=(120,20), key='-LOADING_BAR-')]
        ]
        return layout
    
    # canvas + select layer

    def layout_map_editor_canvas(self, sizex, sizey, imgdata=False): # not finished
        if imgdata == False:
            layout = [
                [sg.Image(size=(math.floor(25*sizex/36),math.floor(24*sizey/24)), key='-CANVAS-')]
            ]   
        else:
            layout = [
                [sg.Image(size=(math.floor(25*sizex/36),math.floor(24*sizey/24)), key='-CANVAS-', data=imgdata)]
            ]
        return layout
    def layout_map_editor_select_layer(self, sizex, sizey):
        def convert_to_bytes(file_or_bytes, sizex, sizey):
            img = PIL.Image.open(file_or_bytes)
            resized_img = img.resize((sizex, sizey))
            with io.BytesIO() as bio:
                resized_img.save(bio, format="PNG")
                del resized_img
                return bio.getvalue()
      
        # layout structure objects
        icon_1 = convert_to_bytes(self.window_icons_file_path+"\\blueprint_icon.png", math.floor(2*sizex/36), math.floor(2*sizex/36))
        icon_2 = convert_to_bytes(self.window_icons_file_path+"\\pencil_icon.png", math.floor(2*sizex/36), math.floor(2*sizex/36))
        icon_3 = convert_to_bytes(self.window_icons_file_path+"\\painter_icon.png", math.floor(2*sizex/36), math.floor(2*sizex/36))
        layout = [
            [
                sg.Button(image_data=icon_1, key="-SELECT_LAYER_STRUCTURE-", image_size=(math.floor(2*sizex/36),math.floor(3*sizey/24))),
                sg.Button(image_data=icon_2, key="-SELECT_LAYER_LAYOUT-", image_size=(math.floor(2*sizex/36),math.floor(3*sizey/24))),
                sg.Button(image_data=icon_3, key="-SELECT_LAYER_OBJECT-", image_size=(math.floor(2*sizex/36),math.floor(3*sizey/24)))

            ]
        ]
        return layout
    def layout_map_editor_panel_2(self, sizex, sizey):        
        input_size = (5,1)
        label_size = (10,1)
        button_size = (15,1)
        smaller_label_size = (5,1)

        combo_size = (15,1)
        combo_label_size = (14,1)

        layout = [
            [sg.Button('Place Visualizer',font=self.fonts["font_text"], size=button_size)], # sg.Checkbox("Generation Visuals:", key="-DEBUG_VISUALS-")
            [],
            [sg.Text('x1: ',font=self.fonts["font_text"]),sg.Input(key="-X1-", size=input_size, font=self.fonts["font_input"], default_text=""), sg.Text('y1: ',font=self.fonts["font_text"]),sg.Input(key="-Y1-", size=input_size, font=self.fonts["font_input"], default_text="")],
            [sg.Text('x2: ',font=self.fonts["font_text"]),sg.Input(key="-X2-", size=input_size, font=self.fonts["font_input"], default_text=""), sg.Text('y2: ',font=self.fonts["font_text"]),sg.Input(key="-Y2-", size=input_size, font=self.fonts["font_input"], default_text="")],
            [],
            [sg.Radio('Dots',font=self.fonts["font_text"], group_id="-SHAPE-"), sg.Radio('Rectangle',font=self.fonts["font_text"], group_id="-SHAPE-")]
        ]
        return layout
    def layout_map_editor_panel_3(self, sizex, sizey):
        def convert_to_bytes(file_or_bytes, sizex, sizey):
            img = PIL.Image.open(file_or_bytes)
            resized_img = img.resize((sizex, sizey))
            with io.BytesIO() as bio:
                resized_img.save(bio, format="PNG")
                del resized_img
                return bio.getvalue()
        
        icon_1 = convert_to_bytes(self.window_icons_file_path+"\\settings_icon.png", math.floor(2*sizex/36), math.floor(2*sizex/36))
        icon_2 = convert_to_bytes(self.window_icons_file_path+"\\save_icon.png", math.floor(2*sizex/36), math.floor(2*sizex/36))
        icon_3 = convert_to_bytes(self.window_icons_file_path+"\\generate_all_icon.png", math.floor(2*sizex/36), math.floor(2*sizex/36))
        icon_4 = convert_to_bytes(self.window_icons_file_path+"\\export_icon.png", math.floor(2*sizex/36), math.floor(2*sizex/36))
        
        layout = [
            [sg.Button(image_data=icon_1, key="-PANEL_3_MAP_PROPERTIES-", image_size=(math.floor(2*sizex/36),math.floor(2*sizex/36)))],
            [sg.Button(image_data=icon_2, key="-PANEL_3_SAVE-", image_size=(math.floor(2*sizex/36),math.floor(2*sizex/36)))],
            # [sg.Button(image_data=icon_3, key="-PANEL_3_GENERATE_ALL-", image_size=(math.floor(2*sizex/36),math.floor(2*sizex/36)))],
            [sg.Button(image_data=icon_4, key="-PANEL_3_EXPORT-", image_size=(math.floor(2*sizex/36),math.floor(2*sizex/36)))]
        ]
        return layout 

    # panel 1, the one situated on the left

    def layout_map_editor_panel_1_structure(self, sizex, sizey): # panel 1 - Structure Layer
        def get_structure_types():
            structure_types_file_path = self.file_paths['application_path']+self.file_paths['structure_types.csv']
            temp = self.fwh.csv_to_array(structure_types_file_path, 2) #skips 1 line of header
            returnA = []
            for i in temp:
                if i[1] == "None":
                    i[1] = None
                returnA.append(i[1])
            return returnA
        def get_structure_list():
            structure_list_names = []
            for structure in self.cache_map.structure_organiser.structure_list:
                structure_list_names.append(structure.id_value)
            try:
                structure_list_names.remove("structure_000000")
            except Exception:
                a = 1
            return structure_list_names
        input_size = (5,1)
        label_size = (10,1)
        button_size = (20,1)
        smaller_label_size = (5,1)
        bigger_label_size = (15,1)

        combo_size = (15,1)

        current_room_list = get_structure_list()

        generation_methods = ["Random","Spine", "1PC"]
        room_types = get_structure_types()

        layout = [
            [sg.Text(""), sg.Text('Structures Generation',font=self.fonts["font_heading_3"]), sg.Text("")],
            [sg.Text("Room Placement Method:", size=label_size, font=self.fonts["font_text"]),sg.Combo(generation_methods, key="-GENERATION_METHOD-",size=combo_size, font=self.fonts["font_input"], default_value="Spine")],
            [sg.Text("Min Room Size:", size=bigger_label_size, font=self.fonts["font_text"]),sg.Input(key="-MIN_ROOM_SIZE-", size=input_size, font=self.fonts["font_input"], default_text="8")],
            [sg.Text("Max Room Size:", size=bigger_label_size, font=self.fonts["font_text"]),sg.Input(key="-MAX_ROOM_SIZE-", size=input_size, font=self.fonts["font_input"],default_text="48")],
            [sg.Text("Margin:", size=bigger_label_size, font=self.fonts["font_text"]),sg.Input(key="-STRUCTURE_MARGIN-", size=input_size, font=self.fonts["font_input"],default_text="4")],
            [sg.Button("Generate Structures",font=self.fonts["font_text"], size=button_size)],

            [sg.Text(""), sg.Text('Place Structures',font=self.fonts["font_heading_3"]), sg.Text("")],
            [sg.Text("Room Type:", size=label_size, font=self.fonts["font_text"]),sg.Combo(room_types, key="-ROOM_TYPE-",size=combo_size, font=self.fonts["font_input"], default_value="", readonly=True)],
            [sg.Text("x1:", size=smaller_label_size, font=self.fonts["font_text"]),sg.Input(key="-X1-", size=input_size, font=self.fonts["font_input"],default_text=""), sg.Text("y1:", size=smaller_label_size, font=self.fonts["font_text"]),sg.Input(key="-Y1-", size=input_size, font=self.fonts["font_input"],default_text="")],
            [sg.Text("x2:", size=smaller_label_size, font=self.fonts["font_text"]),sg.Input(key="-X2-", size=input_size, font=self.fonts["font_input"],default_text=""), sg.Text("y2:", size=smaller_label_size, font=self.fonts["font_text"]),sg.Input(key="-Y2-", size=input_size, font=self.fonts["font_input"],default_text="")],
            [sg.Button("Place Structure",font=self.fonts["font_text"], size=button_size)],

            [sg.Button("Delete Structure",font=self.fonts["font_text"], size=button_size), sg.Combo(current_room_list, key="-SELECTED_STRUCTURE-",size=combo_size, font=self.fonts["font_input"], default_value="")],
        ]
        return layout
    def layout_map_editor_panel_1_layout(self, sizex, sizey): # panel 2 - Layout layer
        def get_cell_types():
            cell_types_file_path = self.file_paths['application_path']+self.file_paths['cell_types.csv']
            temp = self.fwh.csv_to_array(cell_types_file_path, 1) #skips 1 line of header
            returnA = []
            for i in temp:
                if i[1] == "None":
                    i[1] = None
                returnA.append(i[1])
            return returnA
        
        input_size = (5,1)
        label_size = (10,1)
        button_size = (30,1)
        smaller_label_size = (5,1)

        combo_size = (15,1)
        combo_label_size = (14,1)

        cell_types = get_cell_types()

        layout = [
            [sg.Text(""), sg.Text('Paths Generation',font=self.fonts["font_heading_3"]), sg.Text("")],
            [sg.Button("Generate Paths",font=self.fonts["font_text"], size=button_size)], # sg.Checkbox("Generation Visuals:", key="-DEBUG_VISUALS-")

            [sg.Text(""), sg.Text('Place Cells',font=self.fonts["font_heading_3"]), sg.Text("")],
            [sg.Text("Cell Type:", size=label_size, font=self.fonts["font_text"]),sg.Combo(cell_types, key="-CELL_TYPE-",size=combo_size, font=self.fonts["font_input"], default_value="path", readonly=True)],
            [sg.Text("x1:", size=smaller_label_size, font=self.fonts["font_text"]),sg.Input(key="-X1-", size=input_size, font=self.fonts["font_input"],default_text=""), sg.Text("y1:", size=smaller_label_size, font=self.fonts["font_text"]),sg.Input(key="-Y1-", size=input_size, font=self.fonts["font_input"],default_text="")],
            [sg.Text("x2:", size=smaller_label_size, font=self.fonts["font_text"]),sg.Input(key="-X2-", size=input_size, font=self.fonts["font_input"],default_text=""), sg.Text("y2:", size=smaller_label_size, font=self.fonts["font_text"]),sg.Input(key="-Y2-", size=input_size, font=self.fonts["font_input"],default_text="")],
            [sg.Button("Place Cells",font=self.fonts["font_text"], size=button_size)],
            [sg.Button("Delete Cells in Region",font=self.fonts["font_text"], size=button_size)],
            [sg.Button("Delete All Cell of Selected Type",font=self.fonts["font_text"], size=button_size)]
        ]
        return layout
    def layout_map_editor_panel_1_object(self, sizex, sizey): # panel 3 - Objet Layer
        def get_structure_types():
            structure_types_file_path = self.file_paths['application_path']+self.file_paths['structure_types.csv']
            temp = self.fwh.csv_to_array(structure_types_file_path, 2) #skips 1 line of header
            returnA = []
            for i in temp:
                if i[1] == "None":
                    i[1] = None
                returnA.append(i[1])
            return returnA
        
        input_size = (5,1)
        label_size = (10,1)
        button_size = (20,1)
        smaller_label_size = (5,1)

        combo_size = (15,1)
        combo_label_size = (14,1)

        chunk_x = ""
        chunk_y = ""
        cell_resolution = str(self.settings['default_cell_resolution'])
        chunk_size = str(self.settings['default_chunksize'])
        texture = str(self.settings['default_texture'])
        

        generation_methods = ["Random","Spine", "1PC"]
        room_types = get_structure_types()

        layout = [
            [sg.Text(""), sg.Text('Structures Generation',font=self.fonts["font_heading_3"]), sg.Text("")],
            [sg.Text("Room Placement Method:", size=label_size, font=self.fonts["font_text"]),sg.Combo(generation_methods, key="-TEXTURE-",size=combo_size, font=self.fonts["font_input"], default_value="")],
            [sg.Text(""), sg.Text('    Room Size',font=self.fonts["font_text"]), sg.Text("")],
            [sg.Text("Min Size:", size=label_size, font=self.fonts["font_text"]),sg.Input(key="-MIN_ROOM_SIZE-", size=input_size, font=self.fonts["font_input"], default_text="")],
            [sg.Text("Max Size:", size=label_size, font=self.fonts["font_text"]),sg.Input(key="-MAX_ROOM_SIZE-", size=input_size, font=self.fonts["font_input"],default_text="")],
            [sg.Text("Margin:", size=label_size, font=self.fonts["font_text"]),sg.Input(key="-STRUCTURE_MARGIN-", size=input_size, font=self.fonts["font_input"],default_text="")],
            [sg.Button("Generate Structures",font=self.fonts["font_text"], size=button_size)],

            [sg.Text(""), sg.Text('Place Structures',font=self.fonts["font_heading_3"]), sg.Text("")],
            [sg.Text("Room Type:", size=label_size, font=self.fonts["font_text"]),sg.Combo(room_types, key="-ROOM_TYPE-",size=combo_size, font=self.fonts["font_input"], default_value="")],
            [sg.Text("x1:", size=smaller_label_size, font=self.fonts["font_text"]),sg.Input(key="-X1-", size=input_size, font=self.fonts["font_input"],default_text=""), sg.Text("y1:", size=smaller_label_size, font=self.fonts["font_text"]),sg.Input(key="-Y1-", size=input_size, font=self.fonts["font_input"],default_text="")],
            [sg.Text("x2:", size=smaller_label_size, font=self.fonts["font_text"]),sg.Input(key="-X2-", size=input_size, font=self.fonts["font_input"],default_text=""), sg.Text("y2:", size=smaller_label_size, font=self.fonts["font_text"]),sg.Input(key="-Y2-", size=input_size, font=self.fonts["font_input"],default_text="")],
            [sg.Button("Place Structure",font=self.fonts["font_text"], size=button_size)]
        ]
        return layout

# start the program
    
    def start(self): # event loop of the entire program
        def check_if_window_is_map_editor(window):
            for map_editor_window in self.window_map_editor:
                if window == self.window_map_editor[map_editor_window]:
                    return True
            return False
        self.open_window("HomeScreen")
        while True: # event handling
            window, event, values = sg.read_all_windows()
            print(window, event, values)
            if self.process_events_all_screens(window, event, values) == False:
                break
            if window == self.window_home:
                self.process_events_home_screen(window, event, values)
            elif check_if_window_is_map_editor(window):
                self.process_events_map_editor_screen(window, event, values)
            elif window == self.window_new_map:
                self.process_events_new_map_screen(window, event, values)
            elif window == self.window_open_existing_file:
                self.process_events_open_existing_file_screen(window, event, values)
            elif window == self.window_settings:
                self.process_events_settings_screen(window, event, values)
            elif window == self.window_pop_up_export_map:
                self.process_events_export_map_pop_up(window, event, values)
    # - - - Windows Events - Non Map Editor - - - #
            
    def process_events_all_screens(self, window, event, values):
        def check_if_window_is_map_editor(window):
            for map_editor_window in self.window_map_editor:
                if window == self.window_map_editor[map_editor_window]:
                    return True
            return False
        # forced close
        if event == "Exit" and window == self.window_home:
            return False
        if event == sg.WIN_CLOSED:
            if window == self.window_home:
                return False
            elif check_if_window_is_map_editor(window):
                self.close_window("MapEditorScreen")
                self.open_window("HomeScreen")
            elif window == self.window_new_map:
                self.open_window("HomeScreen")
                self.close_window("NewMapScreen")
            elif window == self.window_open_existing_file:
                self.close_window("OpenExistingFileScreen")
                self.open_window("HomeScreen")
            elif window == self.window_settings:
                self.close_window("SettingsScreen")
                self.open_window("HomeScreen")
            elif window == self.window_pop_up_export_map:
                self.close_window("ExportMapPopUp")
            elif window == self.window_pop_up_loading:
                sg.popup("Please be Patient.")
    def process_events_home_screen(self, window, event, values):
        print("processing HomeScreen")
        if event == "Settings":
            self.close_window("HomeScreen")
            self.open_window("SettingsScreen")
        elif event == "New Map" or event == "New":
            self.close_window("HomeScreen")
            self.open_window("NewMapScreen")
        elif event == "Open File" or event == "Open":
            self.close_window("HomeScreen")
            self.open_window("OpenExistingFileScreen")
        elif event == "About...":
            sg.popup(self.fwh.load_txt_as_string(self.file_paths['application_path'] + "\\src\\assets\\text_files\\about.txt"))
    def process_events_new_map_screen(self, window, event, values):
        print("processing NewMapScreen")
        if event == "Cancel":
            self.close_window("NewMapScreen")
            self.open_window("HomeScreen")
        elif event == "Reset":

            chunk_x = ""
            chunk_y = ""
            cell_resolution = str(self.settings['default_cell_resolution'])
            chunk_size = str(self.settings['default_chunksize'])
            texture = str(self.settings['default_texture'])
            structure_margin = str(self.settings['structure_margin'])

            self.window_new_map['-CHUNK_X-'].update(chunk_x)
            self.window_new_map['-CHUNK_Y-'].update(chunk_y)
            self.window_new_map['-CELL_RESOLUTION-'].update(cell_resolution)
            self.window_new_map['-CHUNK_SIZE-'].update(chunk_size)
            self.window_new_map['-MARGIN-'].update(structure_margin)
            self.window_new_map['-TEXTURE-'].update(texture)
        elif event == "Save and Proceed":
            try:
                map_properties={
                    "chunk_x": int(values["-CHUNK_X-"]),
                    "chunk_y": int(values["-CHUNK_Y-"]),
                    "chunk_size": int(values["-CHUNK_SIZE-"]),
                    "cell_resolution": int(values["-CELL_RESOLUTION-"]),
                    "texture_pack": str(values["-TEXTURE-"])
                }

                if self.fwh.is_valid_file_name(str(values["-NAME-"])):
                    self.create_new_map(map_properties, values["-NAME-"])
                    self.close_window("NewMapScreen")
                    self.open_window("MapEditorScreen")
                else:
                    sg.popup("INVALID NAME")
                # if no error, proceed
            except Exception as e:
                sg.popup("ERROR: ", e)
    def process_events_open_existing_file_screen(self, window, event, values):  
        print("processing OpenExistingFileScreen")
        if event == "Back":
            self.close_window("OpenExistingFileScreen")
            self.open_window("HomeScreen")
        elif event == "Proceed":
            if values["-COMBO-"] == "New Map":
                self.close_window("OpenExistingFileScreen")
                self.open_window("NewMapScreen")
            else: 
                self.open_map(self.file_paths["application_path"]+self.file_paths["save"]+"\\"+values["-COMBO-"])
                self.close_window("OpenExistingFileScreen")
                self.open_window("MapEditorScreen")
        elif event == "Delete":
            self.fwh.delete(self.file_paths["application_path"]+self.file_paths["save"]+"\\"+values["-COMBO-"])
            try:
                self.open_existing_file_screen_selected_map = self.fwh.return_items_in_folder(self.file_paths["application_path"]+self.file_paths["save"])[0]
            except Exception:
                self.open_existing_file_screen_selected_map = ""
            self.close_window("OpenExistingFileScreen")
            self.open_window("OpenExistingFileScreen")
        elif event == "Select Map":
            combo_choice = values['-COMBO-']
            file_path = None
            if combo_choice == "choose file from directory":
                file_path = self.choose_file()
                valid_folder, file_path = self.check_folder_is_map_folder(file_path)
            else:
                file_path = self.file_paths["application_path"]+self.file_paths["save"]+"\\"+combo_choice
                valid_folder = True

            if valid_folder:
                self.open_existing_file_screen_selected_map = values['-COMBO-']
                if values['-COMBO-'] == "New Map":
                    self.close_window("OpenExistingFileScreen")
                    self.open_window("NewMapScreen")
            else:
                sg.popup("Invalid File Chosen")
        elif event == "Export":
            self.cache_exported_map =self.file_paths["application_path"]+self.file_paths["save"]+"\\"+values['-COMBO-']
            self.open_window("ExportMapPopUp")
    def process_events_settings_screen(self ,window, event, values):
        print("processing SettingsScreen")
        if event == "Reset":

            cell_resolution = str(self.settings['default_cell_resolution'])
            chunk_size = str(self.settings['default_chunksize'])
            texture = str(self.settings['default_texture'])
            default_appearance = str(self.settings['default_appearance'])

            self.window_settings['-DEFAULT_CHUNK_SIZE-'].update(chunk_size)
            self.window_settings['-DEFAULT_CELL_RESOLUTION-'].update(cell_resolution)
            self.window_settings['-DEFAULT_TEXTURE-'].update(texture)
            self.window_settings['-APPEARANCE-'].update(default_appearance)
        elif event == "Save":
            try:
                temp_json_dict = self.fwh.json_to_dict(self.settings_file_path)
                temp_json_dict["default_cell_resolution"] = int(values['-DEFAULT_CELL_RESOLUTION-'])
                temp_json_dict["default_chunksize"] = int(values['-DEFAULT_CHUNK_SIZE-'])
                temp_json_dict["default_texture"] = values['-DEFAULT_TEXTURE-']
                temp_json_dict["default_appearance"] = values['-APPEARANCE-']

                self.fwh.write_array_of_dicts_to_json(temp_json_dict,self.settings_file_path)
                self.extract_all_files()

                # reload appearance
                
                sg.change_look_and_feel(self.settings["default_appearance"])

                self.close_window("SettingsScreen")
                self.open_window("SettingsScreen")
            except Exception:
                sg.popup("VALUE ERROR")
        elif event == "Back":
            self.open_window("HomeScreen")
            self.close_window("SettingsScreen")
    def process_events_map_editor_screen(self ,window, event, values):
        if window == self.window_map_editor["SelectLayer"]:
            #
            print("processing MapEditorScreen.SelectLayer")
            activate = {
                "SelectLayer": False,
                "Panel1": "structure",
                "Panel2": False,
                "Panel3": False,
                "Display": False
            }
            if event == "-SELECT_LAYER_STRUCTURE-":
                self.window_map_editor["Panel1"].close()
                activate["Panel1"] = "structure"
                self.open_map_editor_screen(activate)
            elif event == "-SELECT_LAYER_LAYOUT-":
                self.window_map_editor["Panel1"].close()
                activate["Panel1"] = "layout"
                self.open_map_editor_screen(activate)
            elif event == "-SELECT_LAYER_OBJECT-":
                sg.popup("Feature Not Available")
                # self.window_map_editor["Panel1"].close()
                # activate["Panel1"] = "object"
                # self.open_map_editor_screen(activate)

            self.render_on_display_window(activate["Panel1"])
            #
        elif window == self.window_map_editor["Panel1"]:
            #
            if window.Title == "Panel 1 - Structure.ME":
                activate = {
                        "SelectLayer": False,
                        "Panel1": "structure",
                        "Panel2": False,
                        "Panel3": False,
                        "Display": False
                    }
                #
                print("processing MapEditorScreen.Panel1.Structure")
                if event == "Place Structure":
                    try:
                        self.place_structure(int(values['-X1-']),int(values['-Y1-']),int(values['-X2-']),int(values['-Y2-']),values['-ROOM_TYPE-'])
                        self.cache_map.structure_organiser.write_structure_list_into_layout_grid()
                    except Exception as e:
                        print(e)
                        sg.popup(e)
                    self.render_on_display_window("structure")
                    #self.window_map_editor['Panel1'].close()
                    #self.open_map_editor_screen(activate)
                elif event == "Generate Structures":
                    try:
                        self.generate_structures(int(values['-STRUCTURE_MARGIN-']), int(values['-MIN_ROOM_SIZE-']), int(values['-MAX_ROOM_SIZE-']), str(values['-GENERATION_METHOD-']))
                    except Exception as e:
                        print(e)
                        sg.popup(e)
                    self.render_on_display_window("structure")
                    self.window_map_editor['Panel1'].close()
                    self.open_map_editor_screen(activate)
                elif event == "Delete Structure":
                    self.delete_structure(values["-SELECTED_STRUCTURE-"])
                    self.render_on_display_window("structure")
                    self.window_map_editor['Panel1'].close()
                    self.open_map_editor_screen(activate)
                #
            elif window.Title == "Panel 1 - Layout.ME":
                #
                print("processing MapEditorScreen.Panel1.Layout")
                if event == 'Generate Paths':
                    self.cache_map.structure_organiser.main_generate_connecting_path(debug_visuals = False)
                    self.render_on_display_window("layout")
                elif event == "Place Cells":
                    try:
                        if self.cache_map.place_cells_in_list(int(values['-X1-']),int(values['-Y1-']),int(values['-X2-']),int(values['-Y2-']),values['-CELL_TYPE-']):
                            self.render_on_display_window("layout")
                        else:
                            sg.popup("Invalid Inputs")
                    except Exception as e:
                        print(e)
                        sg.popup(e)
                elif event == "Delete Cells in Region":
                    try:
                        if self.cache_map.delete_cells_in_list(int(values['-X1-']),int(values['-Y1-']),int(values['-X2-']),int(values['-Y2-']),values['-CELL_TYPE-']):
                            self.render_on_display_window("layout")
                        else:
                            sg.popup("Invalid Inputs")
                    except Exception as e:
                        print(e)
                        sg.popup(e)
                elif event == "Delete All Cell of Selected Type":
                    try:
                        if self.cache_map.delete_cells_in_list(0,0,self.cache_map.sizex-1,self.cache_map.sizey-1,values['-CELL_TYPE-']):
                            self.render_on_display_window("layout")
                        else:
                            sg.popup("Invalid Inputs")
                    except Exception as e:
                        print(e)
                        sg.popup(e)
                #   
            elif window.Title == "Panel 1 - Object.ME":
                #
                print("processing MapEditorScreen.Panel1.Object")
                #
            #
        elif window == self.window_map_editor["Panel2"]:
            #
            print("processing MapEditorScreen.Panel2")
            sg.popup("Feature Not Available")
            #         
        elif window == self.window_map_editor["Panel3"]:
            #
            print("processing MapEditorScreen.Panel3")
            if event == "-PANEL_3_SAVE-":
                self.cache_map.save_to_file()
            elif event == "-PANEL_3_MAP_PROPERTIES-":
                output_str = "Map Prop"
                for key in self.cache_map.map_properties:
                    output_str += f"\n{key}:\t\t{self.cache_map.map_properties[key]}"
                sg.popup(output_str)
            elif event == "-PANEL_3_EXPORT-":
                self.cache_exported_map = self.cache_map.battle_map_save_file
                self.open_window("ExportMapPopUp")
            elif event == "-PANEL_3_GENERATE_ALL-":
                sg.popup("Feature Not Available")
                # self.cache_map.clear_cach()

            #
        elif window == self.window_map_editor["Display"]:
            #
            print("processing MapEditorScreen.Display")
            #
    
    def process_events_export_map_pop_up(self ,window, event, values):
        if event == "Confirm Export":
            if values["-PDF-"]:
                file_format = "PDF"
                smol_txt = ('PDF files', '*.pdf')
            elif values["-PNG-"]:
                file_format = "PNG"
                smol_txt = ('PNG files', '*.png')
            elif values["-JPEG-"]:
                file_format = "JPEG"
                smol_txt = ('JPEG files', '*.jpeg')

            if values["-RGB-"]:
                color_format = "RGB"
            elif values["-CMYK-"]:
                color_format = "CMYK"

            options = {
                'initialdir': '/',
                'title': 'Save File',
                'defaultextension': smol_txt[1],
                'filetypes': [
                    smol_txt
                ]
            }
            file_path = filedialog.asksaveasfilename(**options)
            print(file_path)

            # export...

            # progress bar threading
            def thread_render():
                if self.cache_map == None:
                    self.open_map(self.cache_exported_map)
                    image = self.cache_map.render_export_image()
                    if color_format != image.mode:
                        image = image.convert(color_format)
                    image.save(file_path, format=file_format)
                    self.cache_map = None
                else:
                    image = self.cache_map.render_export_image()
                    if color_format != image.mode:
                        image = image.convert(color_format)
                    image.save(file_path, format=file_format)
            def thread_loading():
                self.window_pop_up_export_map["-LOADING_TEXT-"].update("Rendering Progress: 0%")
                for i in range(0, 10):
                    time.sleep(5)
                    self.window_pop_up_export_map["-LOADING_TEXT-"].update(f"Rendering Progress: {i*10}%")
                

            loading = threading.Thread(target=thread_loading)
            render = threading.Thread(target=thread_render)
            thread_render()

            # Start the threads
            #loading.start()
            #render.start()
            #loading.join()
            #render.join()
            self.close_window("ExportMapPopUp")

    # - - - Open / Close Windows - - - #
                    
    def open_window(self, window): # take the window name
        location = (self.initialization_parameters["locationx"], self.initialization_parameters["locationy"])
        finalize = self.initialization_parameters

        if window == "HomeScreen":
            self.window_home = sg.Window('Home Screen', self.layout_home_screen(), location=(100,100), finalize=finalize)
        elif window == "MapEditorScreen":
            activate = {
                "SelectLayer": True,
                "Panel1": "structure",
                "Panel2": True,
                "Panel3": True,
                "Display": True
            }
            self.open_map_editor_screen(activate)
        elif window == "NewMapScreen":
            self.window_new_map = sg.Window('New Map', self.layout_new_map_screen(), location=(500,100), finalize=finalize)
        elif window == "OpenExistingFileScreen":
            self.window_open_existing_file = sg.Window('Open File', self.layout_open_existing_file_screen(), location=location, finalize=finalize)
        elif window == "SettingsScreen":
            self.window_settings = sg.Window('Settings', self.layout_settings_screen(), location=(100,300), finalize=finalize)

        # pop ups
            
        elif window == "ExportMapPopUp":
            self.window_pop_up_export_map = sg.Window('Export Map', self.layout_export_map_pop_up(), location=(500,300), finalize=finalize)
        elif window == "LoadingPopUp":
            self.window_pop_up_loading = sg.Window('Loading', self.layout_loading_pop_up(), location=(500,300), finalize=finalize)
    def close_window(self, window):
        try:
            window_name = "unknown"
            if window == "HomeScreen":
                self.window_home.close()
                self.window_home = None
                window_name = "window_home"
            elif window == "MapEditorScreen":
                self.close_map_editor_screen()
                window_name = "window_map_editor"
            elif window == "NewMapScreen":
                self.window_new_map.close()
                self.window_new_map = None
                window_name = "window_new_map"
            elif window == "OpenExistingFileScreen":
                self.window_open_existing_file.close()
                self.window_open_existing_file = None
                window_name = "window_open_existing_file"
            elif window == "SettingsScreen":
                self.window_settings.close()
                self.window_settings = None
                window_name = "window_settings"

            # pop ups
                
            elif window == "ExportMapPopUp":
                self.window_pop_up_export_map.close()
                self.window_pop_up_export_map = None
                window_name = "window_pop_up_export_map"
            elif window == "LoadingPopUp":
                self.window_pop_up_loading.close()
                self.window_pop_up_loading = None
                window_name = "window_pop_up_loading"
            print(f"closed {window_name}")
        except Exception:
            print(f"{window} is already closed.")
    
    def close_map_editor_screen(self):
        for window in self.window_map_editor:
            try:
                self.window_map_editor[window].close()
                self.window_map_editor[window] = None
            except Exception as e:
                print(e)
        self.cache_map = None
    def open_map_editor_screen(self, activate_window): # activate window is a library of boolean
        # valid cache map
        if self.cache_map == None:
                self.open_map(self.file_paths['application_path'] +"\\save\\file_1")
                #self.create_new_map_without_input()

        # decide each panel's parameters

        finalize = self.initialization_parameters["finalize"]
        sizex = self.initialization_parameters["sizex"]
        sizey = self.initialization_parameters["sizey"]
        left_top_corner = (self.initialization_parameters["locationx"],self.initialization_parameters["locationy"])

        select_layer_panel_parameters = {
            "location": left_top_corner,
            "size": (math.floor(9*sizex/36),math.floor(3*sizey/24))
        }
        panel_1_parameters = {
            "location": (left_top_corner[0],left_top_corner[1]+select_layer_panel_parameters['size'][1]),
            "size": (math.floor(9*sizex/36),math.floor(14*sizey/24))
        }
        panel_2_parameters = {
            "location": (left_top_corner[0],left_top_corner[1]+select_layer_panel_parameters['size'][1]+panel_1_parameters['size'][1]),
            "size": (math.floor(9*sizex/36),math.floor(7*sizey/24))
        }
        display_canvas_panel_parameters = {
            "location": (left_top_corner[0]+select_layer_panel_parameters['size'][0],left_top_corner[1]),
            "size": (math.floor(25*sizex/36),math.floor(24*sizey/24))
        }
        panel_3_parameters = {
            "location": (left_top_corner[0]+select_layer_panel_parameters['size'][0]+display_canvas_panel_parameters['size'][0],left_top_corner[1]),
            "size": (math.floor(2*sizex/36),math.floor(24*sizey/24))
        }
        
        # initialize each layer
        if activate_window["SelectLayer"]:
            self.window_map_editor["SelectLayer"] = sg.Window('Select Layer.ME', self.layout_map_editor_select_layer(sizex, sizey), size=select_layer_panel_parameters['size'], location=select_layer_panel_parameters['location'], finalize=finalize)

        if activate_window["Panel2"]:
            self.window_map_editor["Panel2"] = sg.Window('Panel 2.ME', self.layout_map_editor_panel_2(sizex, sizey), size=panel_2_parameters['size'], location=panel_2_parameters['location'], finalize=finalize)
        if activate_window["Panel3"]:
            self.window_map_editor["Panel3"] = sg.Window('Panel 3.ME', self.layout_map_editor_panel_3(sizex, sizey), size=panel_3_parameters['size'], location=panel_3_parameters['location'], finalize=finalize)
        if activate_window["Display"]:
            self.window_map_editor["Display"] = sg.Window('Display Render.ME', self.layout_map_editor_canvas(sizex, sizey), size=display_canvas_panel_parameters['size'], location=display_canvas_panel_parameters['location'], finalize=finalize)
            self.render_on_display_window(activate_window["Panel1"])

        if activate_window["Panel1"] == "structure":
            self.window_map_editor["Panel1"] = sg.Window('Panel 1 - Structure.ME', self.layout_map_editor_panel_1_structure(sizex, sizey), size=panel_1_parameters['size'], location=panel_1_parameters['location'], finalize=finalize)
        elif activate_window["Panel1"] == "layout":
            self.window_map_editor["Panel1"] = sg.Window('Panel 1 - Layout.ME', self.layout_map_editor_panel_1_layout(sizex, sizey), size=panel_1_parameters['size'], location=panel_1_parameters['location'], finalize=finalize)
        elif activate_window["Panel1"] == "object":
            self.window_map_editor["Panel1"] = sg.Window('Panel 1 - Object.ME', self.layout_map_editor_panel_1_object(sizex, sizey), size=panel_1_parameters['size'], location=panel_1_parameters['location'], finalize=finalize)

# - - - Create / Delete Map Functions - - - #
    def create_new_map_without_input(self):
        map_properties = {
            "chunk_x": 8, # untold settings
            "chunk_y": 8, # untold settings
            "chunk_size": self.settings["default_chunksize"],
            "cell_resolution": self.settings["default_cell_resolution"],
            "structure_margin": 8,
            "texture_pack": self.settings["default_texture"]
        }
        name = "new_map_" + secrets.token_hex(2)
        self.create_new_map(map_properties, name)
    def create_new_map(self, map_properties, name):
        file_path = self.save_file_path+"\\"+name

        # create all the new files

        self.fwh.create_folder(file_path)

        self.fwh.create_folder(file_path+"\\cell_type_list_layout")
        self.fwh.create_folder(file_path+"\\json_lists")
        self.fwh.create_folder(file_path+"\\structure_list_layout")
        self.fwh.create_folder(file_path+"\\images")

        self.fwh.write_array_of_dicts_to_json(map_properties, file_path+"\\json_lists\\map_properties.json")
        self.fwh.write_array_of_dicts_to_json({}, file_path+"\\json_lists\\object_list.json")
        self.fwh.write_array_of_dicts_to_json({}, file_path+"\\json_lists\\structure_list.json")

        self.fwh.create_empty_csv(file_path+"\\cell_type_list_layout\\path_list.csv")
        self.fwh.create_empty_csv(file_path+"\\cell_type_list_layout\\hazard_list.csv")
        self.fwh.create_empty_csv(file_path+"\\cell_type_list_layout\\water_list.csv")

        self.fwh.create_empty_csv(file_path+"\\Layout.csv")

        self.cache_map = Map(map_properties, file_path, self.file_paths)
    def open_map(self, map_folder_path):
        map_properties = self.fwh.json_to_dict(map_folder_path+"\\json_lists\\map_properties.json")
        self.cache_map = Map(map_properties, map_folder_path, self.file_paths)
    
    def check_folder_is_map_folder(self, file_path):
        map_save_file_path = file_path
        hazard_list = self.fwh.path_exist(map_save_file_path+"\\cell_type_list_layout\\hazard_list.csv")
        path_list = self.fwh.path_exist(map_save_file_path+"\\cell_type_list_layout\\path_list.csv")
        water_list = self.fwh.path_exist(map_save_file_path+"\\cell_type_list_layout\\water_list.csv")

        map_properties = self.fwh.path_exist(map_save_file_path+"\\json_lists\\map_properties.json")
        object_list = self.fwh.path_exist(map_save_file_path+"\\json_lists\\object_list.json")
        structure_list = self.fwh.path_exist(map_save_file_path+"\\json_lists\\structure_list.json")

        Layout = self.fwh.path_exist(map_save_file_path+"\\Layout.csv")

        if (hazard_list and path_list and water_list and map_properties and object_list and structure_list and Layout):
            return True, map_save_file_path
        else:
            return False, map_save_file_path





        #try map name, if false, then no
        

# Structure organiser event linking
    def delete_structure(self, structure_id):
        # find index of structure
        for structure in self.cache_map.structure_organiser.structure_list:
            if structure.id_value == structure_id:
                self.cache_map.structure_organiser.structure_list.remove(structure)
                return True
        return False
    def place_structure(self, x1, y1, x2, y2, structure_type):
        id = secrets.token_hex(5)
        if structure_type == "rectangular_room":
            temp_structure = StructureRectangularRoom(x1, y1, x2, y2, id, [1,1,1,1])
        elif structure_type == "maze":
            temp_structure = StructureMaze(x1, y1, x2, y2, id)
        elif structure_type == "circular_room":
            temp_structure = StructureCircularRoom(x1, y1, x2, y2, id, False)
        elif structure_type == "corridor":
            temp_structure = StructureRectangularRoom(x1, y1, x2, y2, id, [1,1,1,1])
        elif structure_type == "L_room":
            q = random.randint(1,4)
            midx = math.floor(x1/2 + x2/2)
            midy = math.floor(y1/2 + y2/2)
            temp_structure = StructureLRoom(x1, y1, x2, y2, id, midx, midy, q)

        self.cache_map.structure_organiser.structure_list.append(temp_structure)
    def generate_structures(self, margin, minrs, maxrs, method):
        if method == "Random":
            max_room_amount = 100
            room_coords = self.cache_map.structure_organiser.gen_any_and_everywhere(self.cache_map.structure_organiser.structure_generation_try_amount, margin, minrs, maxrs, max_room_amount)
            
        elif method == "Spine":
            rooms_per_rib = 5
            spine_margin = 3
            room_coords = self.cache_map.structure_organiser.gen_spine_organisation(rooms_per_rib, spine_margin, self.cache_map.structure_organiser.structure_generation_try_amount, margin, minrs, maxrs)
    
        elif method == "1PC":
            room_coords = self.cache_map.structure_organiser.gen_1_room_per_chunk_organisation(self.cache_map.structure_organiser.structure_generation_try_amount, margin, minrs, maxrs)

        for a in room_coords:
            self.cache_map.structure_organiser.structure_list.append(self.cache_map.structure_organiser.return_random_structure(a[0],a[1],a[2],a[3],secrets.token_hex(5)))


# layout layer event linking
    
# map renderer event linking
        
    def render_on_display_window(self, layer_type): # render on screen directly
        def convert_to_bytes(file_or_bytes, sizex, sizey):
            img = PIL.Image.open(file_or_bytes)
            resized_img = img.resize((sizex, sizey))
            with io.BytesIO() as bio:
                resized_img.save(bio, format="PNG")
                del resized_img
                return bio.getvalue()

        if layer_type == "structure":
            self.cache_map.render_structure_layer()
            self.cache_map.map_renderer.save_cache_images_to_file()
            image_file_path = self.cache_map.battle_map_save_file + "\\images\\cache_structure_layer_image.png"
        elif layer_type == "layout":
            self.cache_map.reload_layout()
            self.cache_map.render_layout_layer()
            self.cache_map.map_renderer.save_cache_images_to_file()
            image_file_path = self.cache_map.battle_map_save_file + "\\images\\cache_layout_image.png"
        elif layer_type == "object":
            self.cache_map.map_renderer.pil_render_object_layer_image()
            self.cache_map.map_renderer.save_cache_images_to_file()
            image_file_path = self.cache_map.battle_map_save_file + "\\images\\cache_object_layer_image.png"

        screen_sizex, screen_sizey = math.floor(22*self.initialization_parameters['sizex']/36), math.floor(22*self.initialization_parameters['sizey']/24)
        ratio = self.cache_map.chunk_y / self.cache_map.chunk_x # rise over run
        if screen_sizex > screen_sizey:
            if ratio >= 1:
                sizey = screen_sizey
                sizex = math.floor(screen_sizey / ratio)
            else:
                sizex = screen_sizex
                sizey = math.floor(screen_sizey * ratio)
        else:
            if ratio <= 1:
                sizey = screen_sizey
                sizex = math.floor(screen_sizey / ratio)
            else:
                sizex = screen_sizex
                sizey = math.floor(screen_sizey * ratio)

        imgdata = convert_to_bytes(image_file_path, sizex, sizey)
        self.window_map_editor["Display"]["-CANVAS-"].update(data=imgdata)
        print(f"updated display panel. Displaying {layer_type}")



# pop ups
    def save_as_file(self):
        # Create the root window
        root = tk.Tk()
        root.withdraw()

        # Open the file dialog
        file_path = filedialog.asksaveasfilename()

        # Check if a file path was selected
        if file_path:
            return file_path
        else:
            return None
    def choose_file(self):
        # Create the root window
        root = tk.Tk()
        root.withdraw()

        # Open the file dialog
        file_path = filedialog.askopenfilename()

        # Check if a file was selected
        if file_path:
            return file_path
        else:
            return None
    def choose_folder(self):
        # Create the root window
        root = tk.Tk()
        root.withdraw()

        # Open the folder dialog
        folder_path = filedialog.askdirectory()

        # Check if a folder was selected
        if folder_path:
            return folder_path
        else:
            return None

    def input_pop_up(self, text):
        a = 1
