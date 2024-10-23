from helpers.color_helper import ColorHelper
from helpers.file_write_helper import FileWriteHelper

from map_renderer.objects import *
from map_generator.structures import *
from textures_generator.texture_tile_set_generator import TileSetGenerator

from PIL import Image, ImageDraw
import numpy
import time

class MapRenderer:
    def __init__(self, map_properties, battle_map_save_file, file_paths):
        #helpers
        self.color_helper = ColorHelper()
        self.fwh = FileWriteHelper()
        self.texture_tile_set_generator = TileSetGenerator(map_properties, battle_map_save_file, file_paths)
        
        #path to the folder which the map is stored
        self.battle_map_save_file = battle_map_save_file
        self.file_paths = file_paths
        self.map_properties = map_properties

        #base info

        self.chunk_x=int(self.map_properties["chunk_x"])
        self.chunk_y=int(self.map_properties["chunk_y"])
        self.chunk_size=int(self.map_properties["chunk_size"])
        self.cell_resolution=int(self.map_properties["cell_resolution"])

        self.sizex = self.chunk_x * self.chunk_size 
        self.sizey = self.chunk_y * self.chunk_size 
        self.pixel_x = self.sizex * self.cell_resolution
        self.pixel_y = self.sizey * self.cell_resolution

        self.render_cell_resolution = math.ceil(32768/(self.sizex*self.sizey))

        self.texture_pack=self.map_properties["texture_pack"]
        self.background_color = (0,0,0,0)
        
        #Map render Cache
        self.layout_render_format = self.grid = [["void" for _ in range(self.sizey)] for _ in range(self.sizex)] #x -> y -> properties

        self.cache_structure_layer_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))
        self.cache_layout_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))
        self.cache_object_layer_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))
        self.cache_rendered_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))
        
        self.cache_selection_overlay_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))
        self.cache_selection_overlay_applied_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))

        self.cache_display_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))
        
        #objects
        self.object_list = []

        #Source Path
        self.cell_types_file_path = self.file_paths['application_path'] + self.file_paths['cell_types.csv']
        self.structure_types_file_path = self.file_paths['application_path']+self.file_paths['structure_types.csv']
        self.textures_file_path = self.file_paths['application_path']+self.file_paths['textures']
        self.cell_types_texture_hiearchy_file_path = self.file_paths['application_path']+self.file_paths['cell_type_texture_hiearchy.csv']
        self.object_icon_file_path = self.file_paths['application_path']+self.file_paths['object_icons']

        self.cell_types_csv = []
        self.structure_types_csv = []
        self.cell_types_texture_hiearchy = []
        
        self.extract_cell_types()
        self.extract_structure_types()
        self.extract_cell_types_hiearchy()

# - - - basic file extraction - - - #
    def csv_to_array(self, file_path, skipline):
        data = numpy.genfromtxt(file_path, delimiter=',', skip_header=skipline, dtype=str, encoding='utf-8')
        return data
    def extract_cell_types(self):
        temp = self.csv_to_array(self.cell_types_file_path, 1)
        #print(temp)
        # color hex code add the "#"
        for i in temp:
            i[2] = "#"+str(i[2])
        self.cell_types_csv = temp
        return temp
    def extract_structure_types(self):
        temp = self.fwh.csv_to_array(self.structure_types_file_path, 1) #skips 1 line of header
        self.structure_types_csv = temp
        return_a = []
        for i in temp:
            if i[1] == "None":
                i[1] = None
            return_a.append(i[1])
        self.structure_types = return_a
    def extract_cell_types_hiearchy(self):
        self.cell_type_texture_hiearchy = self.fwh.csv_to_array(self.cell_types_texture_hiearchy_file_path,0)

    def clear_cache(self):
        #Map render Cache
        self.layout_render_format = self.grid = [["void" for _ in range(self.sizey)] for _ in range(self.sizex)] #x -> y -> properties

        self.cache_structure_layer_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))
        self.cache_layout_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))
        self.cache_object_layer_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))
        self.cache_rendered_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))

        self.cache_selection_overlay_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))
        self.cache_selection_overlay_applied_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))

        self.cache_display_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))
        
        #objects
        self.object_list = []

# - - - color helper - - - #
    def cell_type_to_color(self,cell_type):
        #match color to cell type
        if cell_type == "void":
            return None
        for i in self.cell_types_csv:
            color = self.color_helper.color_to_hex(i[2])
            if cell_type == i[1]:
                return color
        #no cell types matched, return None as color
        return None
    
# - - - pil Rendering - all requires rgba - - - #
    def pil_create_rectangle(self,image,x1,y1,x2,y2,color): # unused function
        try: 
            # Create a drawing object
            draw = ImageDraw.Draw(image)

            # Draw a rectangle on the image
            color = self.color_helper.hex_to_rgba(color,255)
            draw.rectangle((x1,y1,x2,y2))
            return image
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    def pil_render_structures(self,structure_list):
        sizex = self.sizex
        sizey = self.sizey
        cell_resolution = self.render_cell_resolution
        image = Image.new("RGBA", (sizex*cell_resolution, sizey*cell_resolution), self.background_color)
        draw = ImageDraw.Draw(image)

        for s in structure_list:
            color = "#000000"
            for line in self.structure_types_csv:
                if line[1] == s.structure_type:
                    color = line[3]
            color = self.color_helper.hex_to_rgba(color,255)

            for i in range(len(s.grid)):
               for j in range(len(s.grid[i])):
                    if color != None and s.grid[i][j] != "void":
                        x1 = (s.x1+i)*cell_resolution
                        y1 = (s.y1+j)*cell_resolution
                        x2 = x1+cell_resolution
                        y2 = y1+cell_resolution
                        draw.rectangle((x1,y1,x2,y2), fill=color)

        self.cache_structure_layer_image = image        
        return image       
    def pil_render_layout(self, grid):
        cellsize = self.render_cell_resolution
        image = Image.new("RGBA", (len(grid)*cellsize, len(grid[0])*cellsize), self.background_color)
        draw = ImageDraw.Draw(image)

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if self.cell_type_to_color(grid[i][j]) != None:
                    color = self.color_helper.hex_to_rgba(self.cell_type_to_color(grid[i][j]),255)
                    draw.rectangle((i*cellsize,j*cellsize,i*cellsize+cellsize,j*cellsize+cellsize), fill=color)
        self.cache_layout_image = image
        return image
    
    # - Render Overlay Layer

    def pil_render_selection_overlay_image(self, x, y, x1, y1, x2, y2):
        a = 1

    # - render and write object methods
    
    def write_objects_array_to_file(self):
        object_list_file_path = self.battle_map_save_file+"\\json_lists\\object_list.json"
        self.fwh.clear_json_file(object_list_file_path)
        self.fwh.clear_folder(self.battle_map_save_file+"\\structure_list_layout")
        array_of_object_dicts = []

        for a in self.structure_list:
            array_of_object_dicts.append(a.return_as_dictionary())
            
        self.fwh.write_array_of_dicts_to_json(array_of_object_dicts,object_list_file_path)
    def pil_render_object_layer_image(self):
        self.cache_object_layer_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))
        for object in self.object_list:
            size = (object.x2-object.x1, object.y2-object.y1)
            png_image = Image.open(object.image_file_path)
            position = (object.x1, object.x2)
            self.cache_object_layer_image = self.place_png_on_image(self.cache_object_layer_image,png_image,position,size)  
    def place_png_on_image(self, existing_image, png_image, position, size):
        resized_png_image = png_image.resize(size)

        # Create a composite image by pasting the resized PNG image onto the existing image
        composite_image = existing_image.copy()
        composite_image.paste(resized_png_image, position)

        # Save the composite image
        return composite_image

    # - Render rendered image #
    
    def layout_to_render_format(self,layout_grid):
        def subjected_to_change(cell_type_texture_hiearchy, base, overwrites):
            x_index = 0 # base - collumns
            y_index = 0 # overwrites - rows

            for i in range(1,len(cell_type_texture_hiearchy)):
                if str(cell_type_texture_hiearchy[i][0]) == overwrites:
                    x_index = i
            for j in range(1,len(cell_type_texture_hiearchy[0])):
                if str(cell_type_texture_hiearchy[0][j]) == base:
                    y_index = j
            if x_index == 0 or y_index == 0:
                print("can't find the corrosponding cell type")
                return False
            else:
                boolean_value = ("TRUE" == str(cell_type_texture_hiearchy[x_index][y_index]))
                return boolean_value
        def return_neigboring_cell_types(layout_grid,x1,y1):
            nx, ny, ex, ey, sx, sy, wx, wy = 0,0,0,0,0,0,0,0
            nx = x1
            ny = y1 -1
            ex = x1 +1
            ey = y1
            sx = x1
            sy = y1 +1
            wx = x1 -1
            wy = y1

            sizex = len(layout_grid)
            sizey = len(layout_grid[0])

            # check if cells on border

            if x1 == 0: # on the west border
                wx, wy = x1, y1
            if x1 == sizex-1: # on the east border
                ex, ey = x1, y1
            if y1 == 0: # on the north border
                nx, ny = x1, y1
            if y1 == sizey-1: # on the south border
                sx, sy = x1, y1
            
            # check if any of them are connected cells
            cell_array = [[nx, ny],[ex, ey], [sx, sy],[wx, wy]]
            neighboring_cell_types = []
            for a in cell_array:
                if a[0] == x1 and a[1] == y1:
                    neighboring_cell_types.append("void")
                else:
                    neighboring_cell_types.append(layout_grid[a[0]][a[1]])
            return neighboring_cell_types
        def get_cell_type_index(cell_types_csv, cell_type):
            for i in range(0,len(cell_types_csv)):
                if cell_types_csv[i][1] == cell_type:
                    return i
            #print("no value found so return 0 instead")
            return 0

        self.layout_render_format = self.grid = [["void" for _ in range(self.sizey)] for _ in range(self.sizex)] #x -> y -> properties
        
        # looping through the initial layout grid
        for i in range(0, self.sizex):
            for j in range(0, self.sizey):
                base_cell_type = layout_grid[i][j]
                base_cell_type_index = get_cell_type_index(self.cell_types_csv,base_cell_type)
                neigboring_cell_types = return_neigboring_cell_types(layout_grid,i,j)
                cell_id = base_cell_type

                
                for a in range(0, 4):
                    if subjected_to_change(self.cell_type_texture_hiearchy, base_cell_type, neigboring_cell_types[a]):
                        cell_id = cell_id + '_' + str(get_cell_type_index(self.cell_types_csv,neigboring_cell_types[a]))
                    else:
                        cell_id = cell_id + '_' + str(base_cell_type_index)

                    self.layout_render_format[i][j] = cell_id

        # rules for naming:
        # if only 1 celltype, then {base_cell_type}_0_0_0_0
    def render_rendered_layout_image(self):
        self.cache_rendered_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba('#000000',0))

        progress = 0

        for i in range(0,self.sizex):
            for j in range(0,self.sizex):
                # debug + progress update

                progress += 1
                if progress%100 == 0:
                    print(f"Rendering Rendered Image, tile {progress} out of {self.sizex*self.sizey} tiles generated.")

                cell_id = self.layout_render_format[i][j]
                size = (self.cell_resolution,self.cell_resolution)
                position = (i*self.cell_resolution, j*self.cell_resolution)

                try:
                    png_image = Image.open(self.textures_file_path+"\\"+self.texture_pack+"\\"+cell_id+".png")
                except Exception as e:
                    margin_2 = 32
                    size_2 = 128
                    self.texture_tile_set_generator.generate_tile_from_formatted_layout_cell(cell_id, margin_2, size_2, self.textures_file_path+"\\"+self.texture_pack)
                    png_image = Image.open(self.textures_file_path+"\\"+self.texture_pack+"\\"+cell_id+".png")
                
                self.cache_rendered_image = self.place_png_on_image(self.cache_rendered_image, png_image, position, size)
        
        return self.cache_rendered_image

    # - render final + outside accessro functions #
    
    def render_chosen_layers(self, structure_list, layout_grid, active_layers):
        # keys = ["structure", "layout", "rendered", "object"]
        if active_layers["structure"]:
            self.pil_render_structures(structure_list, self.sizex, self.sizey, self.cell_resolution)
        if active_layers["layout"]:
            self.pil_render_layout(layout_grid, self.cell_resolution)
        if active_layers["rendered"]:
            self.layout_to_render_format(layout_grid)
            self.render_rendered_layout_image()
        if active_layers["object"]:
            self.pil_render_object_layer_image()
    def render_all_layers(self, structure_list, layout_grid): # save everything to cache layers

        self.pil_render_structures(structure_list)
        self.pil_render_layout(layout_grid)
        self.layout_to_render_format(layout_grid)
        self.render_rendered_layout_image()
        self.pil_render_object_layer_image()    
    def render_display_image(self, active_layers, background_color): # dictionary using key layer names with boolean values
        self.cache_display_image = Image.new("RGBA", (self.pixel_x, self.pixel_y), self.color_helper.hex_to_rgba(background_color,255))
        size = (self.pixel_x,self.pixel_y)
        position = (0,0)

        layers = ["structure", "layout", "rendered", "object"]

        active_layer_image = {
            "structure": self.cache_structure_layer_image,
            "layout": self.cache_layout_image,
            "rendered": self.cache_rendered_image,
            "object": self.cache_object_layer_image
            }
        
        for key in layers:
            if active_layers[key]:
                self.cache_display_image.paste(active_layer_image[key], (0, 0), mask=active_layer_image[key])
                #self.cache_display_image = self.place_png_on_image(self.cache_display_image, active_layer_image[key], position, size)

# - - - change size - - - #
    
    def change_size(self):
        finished = False


# - - - Documentation + save to file - - - #
               
    def save_object_list_to_file(self):
        object_list_file_path = self.battle_map_save_file+"\\json_lists\\object_list.json"
        self.fwh.clear_json_file(object_list_file_path)
        array_of_object_dicts = []
        for object in self.object_list:
            array_of_object_dicts.append(object.return_as_dictionary())
        self.fwh.write_array_of_dicts_to_json(array_of_object_dicts,object_list_file_path)
    def save_cache_images_to_file(self):

        image_file_path = self.battle_map_save_file + "\\images"

        self.cache_structure_layer_image.save(image_file_path+"\\cache_structure_layer_image.png", "PNG")
        self.cache_layout_image.save(image_file_path+"\\cache_layout_image.png", "PNG")
        self.cache_object_layer_image.save(image_file_path+"\\cache_object_layer_image.png", "PNG")
        self.cache_rendered_image.save(image_file_path+"\\cache_rendered_image.png", "PNG")
        self.cache_selection_overlay_image.save(image_file_path+"\\cache_selection_overlay_image.png", "PNG")
        self.cache_display_image.save(image_file_path+"\\cache_display_image.png", "PNG")
        self.cache_selection_overlay_applied_image.save(image_file_path+"\\cache_selection_overlay_applied_image.png", "PNG")

    def pil_render_layout_and_save(self, grid, cellsize, file_path, filename):
        image = self.pil_render_layout(grid, cellsize)
        file_path = file_path+"\\"+filename+".png"
        image.save(file_path, "PNG")
    def pil_render_structures_and_save(self,structure_list, sizex, sizey, cellsize,file_path,filename):
        image = self.pil_render_structures(structure_list, sizex, sizey, cellsize)
        file_path = file_path+"\\"+filename+".png"
        image.save(file_path, "PNG")

