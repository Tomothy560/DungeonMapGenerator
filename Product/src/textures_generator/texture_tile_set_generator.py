from helpers.file_write_helper import FileWriteHelper
from helpers.color_helper import ColorHelper
from PIL import Image, ImageDraw
import numpy
from itertools import combinations

class TileSetGenerator:
    def __init__(self, map_properties, battle_map_save_file, file_paths):
        self.fwh = FileWriteHelper
        self.color_helper = ColorHelper

        #Source Path
        self.file_paths = file_paths
        self.cell_types_file_path = self.file_paths['application_path'] + self.file_paths['cell_types.csv']
        self.structure_types_file_path = self.file_paths['application_path']+self.file_paths['structure_types.csv']
        self.textures_file_path = self.file_paths['application_path']+self.file_paths['textures']

        self.cell_types_CSV = []
        self.structure_types_CSV = []
        self.texture_pack = map_properties["texture_pack"]
        
        self.extract_cell_types()
        self.extract_structure_types()

# basic file extraction
    def csv_to_array(self, file_path, skipline):
        data = numpy.genfromtxt(file_path, delimiter=',', skip_header=skipline, dtype=str, encoding='utf-8')
        return data
    def extract_cell_types(self):
        temp = self.csv_to_array(self.cell_types_file_path, 1)
        for i in temp:
            i[2] = "#"+str(i[2])
        self.cell_types_CSV = temp
        return temp
    def extract_structure_types(self):
        temp = self.fwh.csv_to_array(self.structure_types_file_path, self.structure_types_file_path, 1) #skips 1 line of header
        self.structure_types_CSV = temp
        returnA = []
        for i in temp:
            if i[1] == "None":
                i[1] = None
            returnA.append(i[1])
        self.structure_types = returnA

    def start_test(self):
        color_list = ["#aa2222","#000000","#5a6bae"]
        cell_type_list = ["path","void","wall"]
        margin = 32
        size = 128
        textures_file_path = "C:\\Users\\user\\OneDrive\\Desktop\\Battle_Map_Creator_Python\\src\\assets\\textures\\sample_tile_set"

    
        #self.generate_tile_set(color_list, cell_type_list, margin, size, textures_file_path)
        #print(self.cell_types_CSV)

        self.generate_full_tile_set(margin, size, textures_file_path)


# combination
        
    def get_combinations(self,lst,choose_num):
        # Check if the list size is greater than or equal to 4
        if len(lst) >= choose_num:
            # Generate all combinations of picking 4 elements from the list
            combinations_list = list(combinations(lst, choose_num))
            return combinations_list
        else:
            return []

# tile set generation
    def generate_full_tile_set(self, margin, size, textures_file_path):
        def get_cell_type_index(cell_types_CSV, cell_type):
            for i in range(0,len(cell_types_CSV)):
                if cell_types_CSV[0][i] == cell_type:
                    return i
            return 0
        
        #color list
        color_list = []
        for row in self.cell_types_CSV:
            color_list.append(row[2])
        
        #establish names
        tile_specific_names = []
        tile_images = []

        #generate
        for base in range(0,len(self.cell_types_CSV)):
            for n in range(0,len(self.cell_types_CSV)):
                for e in range(0,len(self.cell_types_CSV)):
                    for s in range(0,len(self.cell_types_CSV)):
                        for w in range(0,len(self.cell_types_CSV)):
                            # check that all types are in place
                            nesw = [n,e,s,w]
                            tile_specific_names.append(self.cell_types_CSV[base][1]+"_"+str(n)+"_"+str(e)+"_"+str(s)+"_"+str(w))
                            tile_images.append(self.generate_tile_png(color_list, margin, size, nesw, base))

        # save to file
        for i in range(0,len(tile_images)):
            tile_images[i].save(textures_file_path+"\\"+tile_specific_names[i]+".png", "PNG")

    def generate_tile_set(self, color_list, cell_type_list, margin, size, textures_file_path):
        def get_cell_type_index(cell_types_CSV, cell_type):
            for i in range(0,len(cell_types_CSV)):
                if cell_types_CSV[i][1] == cell_type:
                    return i
            return 0        
        
        #establish names
        tiles_name = cell_type_list[0]

        tile_specific_names = []
        tile_images = []

        for n in range(0,len(cell_type_list)):
            for e in range(0,len(cell_type_list)):
                for s in range(0,len(cell_type_list)):
                    for w in range(0,len(cell_type_list)):
                        # check that all types are in place
                        nesw = [n,e,s,w]
                        check_all = []
                        for i in range(1,len(cell_type_list)):
                            check_all.append(0)
                        
                        for side in nesw:
                            check_all[side-1] += 1

                        process = True
                        for num in check_all:
                            if num == 0:
                                process = False

                        for a in nesw:
                            a = get_cell_type_index(self.cell_types_CSV,cell_type_list[a])

                        if process:    
                            print(nesw)
                            tile_specific_names.append(tiles_name+"_"+str(n)+"_"+str(e)+"_"+str(s)+"_"+str(w))
                            tile_images.append(self.generate_tile_png(color_list, margin, size, nesw,0))

        # save to file
        for i in range(0,len(tile_images)):
            tile_images[i].save(textures_file_path+"\\"+tile_specific_names[i]+".png", "PNG")
    
    def generate_tile_png_default_layout_tile_set(self, color_list, margin, size, nesw, base_index):
        # 0 = primary base color
        if len(color_list) < 2:
            return
        
        for color in color_list:
            color = self.color_helper.hex_to_rgba(color,color,255)

        image = Image.new("RGBA", (size, size), color_list[int(base_index)])
        draw = ImageDraw.Draw(image)

        nesw_rectangular_coords = [
            [0+margin,0,size-1-margin,0+margin],
            [size-1-margin,0+margin,size-1,size-1-margin],
            [0+margin,size-1-margin,size-1-margin,size-1],
            [0,0+margin,0+margin,size-1-margin]
        ]

        nesw_trapezium_coords = [
            [(0,0),(size-1,0),(size-1-margin,0+margin),(0+margin,0+margin)],
            [(size-1,0),(size-1,size-1),(size-1-margin,size-1-margin),(size-1-margin,0+margin)],
            [(0,size-1),(size-1,size-1),(size-1-margin,size-1-margin),(0+margin,size-1-margin)],
            [(0,0),(0,size-1),(0+margin,size-1-margin),(0+margin,0+margin)]
        ]
        
        for i in range(0,4):
            x1 = nesw_rectangular_coords[i][0]
            y1 = nesw_rectangular_coords[i][1] 
            x2 = nesw_rectangular_coords[i][2]
            y2 = nesw_rectangular_coords[i][3]

            color = color_list[int(nesw[i])]
            draw.polygon(nesw_trapezium_coords[i], fill=color)
        
        return image
    
    def generate_tile_from_formatted_layout_cell(self, cell_id, margin, size, textures_file_path):
        def get_cell_type_index(cell_types_CSV, cell_type):
            for i in range(0,len(cell_types_CSV)):
                if cell_types_CSV[i][1] == cell_type:
                    return int(i)
            return 0  

        #color list
        color_list = []
        for row in self.cell_types_CSV:
            color_list.append(row[2])

        array = cell_id.split("_")
        base_index = get_cell_type_index(self.cell_types_CSV,array[0])
        array.pop(0)
        for element in array:
            element = int(element)

        if self.texture_pack == "default_layout_tile_set":
            image = self.generate_tile_png_default_layout_tile_set(color_list, margin, size, array, base_index)
        elif self.texture_pack == "insert texture generation name":
            finished = False
            #image = self.generate_tile_png_another_tile_png_generation_method(color_list, margin, size, array, base_index)
        else:
            image = Image.open(self.file_paths['application_path']+self.file_paths['window_icons']+ "\\missing_texture_icon.png")

        image.save(textures_file_path+"\\"+cell_id+".png", "PNG")
        print(textures_file_path+"\\"+cell_id+".png")
