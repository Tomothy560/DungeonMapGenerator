from helpers.file_write_helper import FileWriteHelper
from map_generator.layout_generator import LayoutGenerator
from map_generator.structure_organiser import StructureOrganiser
from helpers.file_write_helper import FileWriteHelper
from helpers.color_helper import ColorHelper
from map_renderer.map_renderer import MapRenderer
import time

class Map:
    def __init__(self, map_properties, battle_map_save_file, file_paths):
        # get map name
        temp = battle_map_save_file.split("\\")
        self.map_name = temp[-1]

        # helper function
        self.fwh = FileWriteHelper()
        self.color_helper = ColorHelper()

        # extract current map save file information
        self.battle_map_save_file = battle_map_save_file
        self.file_paths = file_paths
        self.map_properties = map_properties

        # program classes
        self.structure_organiser = StructureOrganiser(map_properties, battle_map_save_file, file_paths)
        self.map_renderer = MapRenderer(map_properties, battle_map_save_file, file_paths)

    # - - - - - initialize empty data - - - - - #
        
        self.extract_map_save_files_data()
        

    
    def update_size_change(self): # not finished
        # fetch information from application
            # not done
        
        # change size information in map renderer

        # change size information in structure organiser
        self.structure_organiser.change_size()

# File Related Funtions

    def extract_map_save_files_data(self):
        # extract current file map information - update as we go on - These act as temporary cache while the application is running
        self.map_properties = self.fwh.json_to_dict(self.battle_map_save_file+"\\json_lists\\map_properties.json")
        
        # structure organiser items
        self.structure_organiser.path_list = self.fwh.csv_to_array(self.battle_map_save_file+"\\cell_type_list_layout\\path_list.csv",0).tolist()
        self.structure_organiser.hazard_list = self.fwh.csv_to_array(self.battle_map_save_file+"\\cell_type_list_layout\\hazard_list.csv",0).tolist()   
        self.structure_organiser.water_list = self.fwh.csv_to_array(self.battle_map_save_file+"\\cell_type_list_layout\\water_list.csv",0).tolist()   
        self.structure_organiser.mp.grid = self.fwh.csv_to_array(self.battle_map_save_file+"\\Layout.csv",0).tolist()
        
        self.structure_organiser.structure_list = self.fwh.save_file_to_structure_list(self.battle_map_save_file)
        self.map_renderer.object_list = []
            # object list
        
        # re-initialize structure organiser ####

        # organize data further
        self.chunk_x=int(self.map_properties["chunk_x"])
        self.chunk_y=int(self.map_properties["chunk_y"])
        self.chunk_size=int(self.map_properties["chunk_size"])
        self.cell_resolution=int(self.map_properties["cell_resolution"])

        self.sizex = self.chunk_x * self.chunk_size
        self.sizey = self.chunk_y * self.chunk_size
        self.pixel_x = self.sizex * self.cell_resolution
        self.pixel_y = self.sizey * self.cell_resolution

    def clear_battle_map_save_file(self): #truncate all the files excerpt properties file - update as we go on
        #truncate the jsons
        self.fwh.clear_json_file(self.battle_map_save_file+"\\json_lists\\structure_list.json")
        self.fwh.clear_json_file(self.battle_map_save_file+"\\json_lists\\object_list.json")

        self.fwh.clear_folder(self.battle_map_save_file+"\\structure_list_layout")
        
        self.fwh.clear_csv(self.battle_map_save_file+"\\cell_type_list_layout\\path_list.csv")
        self.fwh.clear_csv(self.battle_map_save_file+"\\cell_type_list_layout\\hazard_list.csv")
        self.fwh.clear_csv(self.battle_map_save_file+"\\Layout.csv")

    def save_to_file(self): #save all current information to file
        self.structure_organiser.write_structure_list_into_file()
        self.structure_organiser.write_cell_type_list_into_file()
        self.map_renderer.save_object_list_to_file()
        self.map_renderer.save_cache_images_to_file()
        self.fwh.clear_csv(self.battle_map_save_file+"\\Layout.csv")
        self.fwh.write_array_to_csv(self.battle_map_save_file+"\\Layout.csv", self.structure_organiser.mp.grid)

    def clear_cach(self): #clear grid cache and lists, anything that can be empty becomes empty
        self.structure_organiser.clear_cache()
        self.map_renderer.clear_cache()

# add to structure organiser and update final layout - fast quick shortcut
    
    def place_cells_in_list(self, x1, y1, x2, y2, cell_type):
        def iterate_and_add(x1, y1, x2, y2, list):
            for cood in list:
                if cood[0] >= x1 and cood[0] <= x2 and cood[1] >= y1 and cood[1] <= y2:
                    list.remove(cood)
            for i in range(x1, x2):
                for j in range(y1, y2):
                    list.append([i,j])
            return list
        x1, y1, x2, y2 = self.structure_organiser.mp.xy_order_helper(x1, y1, x2, y2)
        if self.structure_organiser.mp.check_x1y1x2y2_in_range(x1, y1, x2, y2) and self.structure_organiser.mp.check_cell_grid_area_is_all_void(x1, y1, x2, y2):
            if cell_type == "path":
                self.structure_organiser.path_list = iterate_and_add(x1, y1, x2, y2, self.structure_organiser.path_list)
            elif cell_type == "hazard":
                self.structure_organiser.hazard_list = iterate_and_add(x1, y1, x2, y2, self.structure_organiser.hazard_list)
            elif cell_type == "water":
                self.structure_organiser.water_list = iterate_and_add(x1, y1, x2, y2, self.structure_organiser.water_list)
            else:
                return False
            return True
        else:
            return False 
    def delete_cells_in_list(self, x1, y1, x2, y2, cell_type):
        
        def iterate_and_delete(x1, y1, x2, y2, list):
            for _ in range(0, 5):
                for cood in list:
                    if cood[0] >= x1 and cood[0] <= x2 and cood[1] >= y1 and cood[1] <= y2:
                        list.remove(cood)
            return list

        x1, y1, x2, y2 = self.structure_organiser.mp.xy_order_helper(x1, y1, x2, y2)
        if self.structure_organiser.mp.check_x1y1x2y2_in_range(x1, y1, x2, y2):
            for _ in range(0,5):
                if cell_type == "path":
                    self.structure_organiser.path_list = iterate_and_delete(x1, y1, x2, y2, self.structure_organiser.path_list)
                elif cell_type == "hazard":
                    self.structure_organiser.hazard_list = iterate_and_delete(x1, y1, x2, y2, self.structure_organiser.hazard_list)
                elif cell_type == "water":
                    self.structure_organiser.water_list = iterate_and_delete(x1, y1, x2, y2, self.structure_organiser.water_list)
                else:
                    return False
            return True
        else:
            return False

# layout specific function
        
    def reload_layout(self):
        self.structure_organiser.mp.grid = [["void" for _ in range(self.sizey)] for _ in range(self.sizex)]
        self.structure_organiser.write_structure_list_into_layout_grid()
        self.structure_organiser.write_path_list_into_layout_grid()
        self.structure_organiser.write_hazard_list_into_layout_grid()
        self.structure_organiser.write_water_list_into_layout_grid()
    
# map renderer - can return images
        
    def render_structure_layer(self):
        structure_list = self.structure_organiser.structure_list
        return self.map_renderer.pil_render_structures(structure_list)
    def render_layout_layer(self):
        grid = self.structure_organiser.mp.grid
        print(grid)
        return self.map_renderer.pil_render_layout(grid)
    def render_object_layer(self):
        return self.map_renderer.pil_render_object_layer_image()

    def render_export_image(self):
        active = {
            "structure": True,
            "layout": True,
            "rendered": True,
            "object": True
        }
        self.map_renderer.render_all_layers(self.structure_organiser.structure_list, self.structure_organiser.mp.grid)
        self.map_renderer.render_display_image(active, "#ffffff")
        return self.map_renderer.cache_display_image

        
