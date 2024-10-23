from helpers.file_write_helper import FileWriteHelper
from helpers.file_write_helper import FileWriteHelper

from map_generator.layout_generator import LayoutGenerator
from map_generator.structure_organiser import StructureOrganiser

from map_renderer.map_renderer import MapRenderer
from textures_generator.texture_tile_set_generator import TileSetGenerator
import time
import datetime
# Save Folder

class MainIsh:
    def __init__(self):
        #helper class
        self.fwh = FileWriteHelper()

        #file paths into absolutes
        self.file_paths = self.fwh.json_to_dict("assets\\json_files\\file_paths.json")

        self.battle_map_save_file = "C:\\Users\\user\\OneDrive\\Desktop\\Battle_Map_Creator_Python\\save\\file_1"
        
        #Set and extract properties
        self.map_properties = self.fwh.json_to_dict(self.battle_map_save_file+"\\json_lists\\map_properties.json")
        
        self.chunk_x=int(self.map_properties["chunk_x"])
        self.chunk_y=int(self.map_properties["chunk_y"])
        self.chunk_size=int(self.map_properties["chunk_size"])
        self.cell_resolution=int(self.map_properties["cell_resolution"])

        # Non int properties
        self.texture_pack=self.map_properties["texture_pack"]

        self.sizex = self.chunk_size*self.chunk_x #size of grid
        self.sizey = self.chunk_size*self.chunk_y #size of grid


        # Create generator and rendering class
        self.sg = StructureOrganiser(self.map_properties, self.battle_map_save_file, self.file_paths)
        self.mr = MapRenderer(self.map_properties, self.battle_map_save_file, self.file_paths)
        
    def start(self):
        start = time.time()
        self.sg.start_test_3()

        end = time.time()
        print(f"Time taken for generation: {end - start} seconds")

        test_layout = self.sg.mp.grid
        #test_layout = self.fwh.csv_to_array(self.battle_map_save_file+"\\Layout.csv",0)

        documentation_file_path = "C:\\Users\\user\\OneDrive\\Desktop\\Battle_Map_Creator_Python\\A-Documentation-PNG"

        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H%M%S")
        filename = "Documentation "+formatted_datetime

        structure_list = self.sg.structure_list

        # proper rendering

        start = time.time()

        #self.mr.layout_to_render_format(test_layout)
        #self.mr.render_rendered_layout_image()   
        self.mr.pil_render_layout(test_layout)
        self.mr.cache_layout_image.save(documentation_file_path+"\\"+filename+"_rendered.png", "PNG") 

        end = time.time()
        print(f"Time taken for rendering: {end - start} seconds")

    def start_2(self):
        self.fwh.clear_folder("C:\\Users\\user\\OneDrive\\Desktop\\Battle_Map_Creator_Python\\src\\assets\\textures\\sample_tile_set")
        tile_generator = TileSetGenerator(self.file_paths)
        tile_generator.start_test()