from map_generator.layout_generator import LayoutGenerator
from map_generator.structures import *
from helpers.file_write_helper import FileWriteHelper
from map_panel.main_panel import MainPanel
import random
import math
import colorsys
import secrets
import tkinter as tk

class StructureOrganiser:
    def __init__(self, map_properties, battle_map_save_file, file_paths):
        self.battle_map_save_file = battle_map_save_file
        self.file_paths = file_paths
        self.map_properties = map_properties

        self.chunk_x = int(self.map_properties["chunk_x"])
        self.chunk_y = int(self.map_properties["chunk_y"])
        self.chunk_size = int(self.map_properties["chunk_size"])
        self.path_radius = 1 # Dont Change

        self.chunk_grid = [["void" for _ in range(self.chunk_x)] for _ in range(self.chunk_y)]
        self.sizex = self.chunk_x*self.chunk_size
        self.sizey = self.chunk_y*self.chunk_size

        self.structure_list = []
        self.path_list = []
        self.hazard_list = []
        self.water_list = []

        structure_0_grid = [] #empty grid
        structure_0 = Structure(0,0,0,0,structure_0_grid,"0000000000")
        self.structure_list.append(structure_0) #get the base structure 0

        # Layout class - and will use this grid for written structures

        self.mp = LayoutGenerator(self.chunk_size*self.chunk_x, self.chunk_size*self.chunk_y, self.battle_map_save_file, file_paths)
        self.fwh = FileWriteHelper()

        # get structure type list
        self.structure_types_file_path = self.file_paths['application_path']+self.file_paths['structure_types.csv']
        self.structure_types_CSV = []
        self.structure_types = []

        self.extract_structure_types()

        # helper grid for generation
        self.check_void_helper_grid = [[0 for _ in range(self.sizey)] for _ in range(self.sizex)]
        self.check_rooms_connected_grid = [["void" for _ in range(self.sizey)] for _ in range(self.sizex)]
        
        # generation setting that is always subject to change
        self.a_star_evaluate_g_values = False
        self.visualize_a_star = False
        self.detailed_visualisation = False
        self.enforce_margin = True
        self.margin = 8 # This can change
        self.structure_generation_try_amount = 500
        self.path_generation_try_amount = 200
        self.min_room_size = 20
        self.max_room_size = 50
        self.force_grid_offset = 1 #cannot be 0
        self.force_grid = 1 #1 = none, CANNOT BE 0

# Debug!
        
    def debug_visuals(self):
        self.cell_size = 4
        self.funky = 1
        #debug visualizeation
        self.app = MainPanel(self.sizex, self.sizey, self.cell_size, self.battle_map_save_file, False)
        self.visualize_a_star = True
        self.root = tk.Tk() 
        self.label1 = tk.Label(self.root)
        self.label2 = tk.Label(self.root)
        self.label3 = tk.Label(self.root)
        self.label5 = tk.Label(self.root)
        self.canvas1 = tk.Canvas(self.root, width=self.sizex*self.cell_size, height=self.sizey*self.cell_size, bg='#bbbbbb')
        self.canvas2 = tk.Canvas(self.root, width=self.sizex*self.cell_size, height=self.sizey*self.cell_size, bg='#bbbbbb')
        self.label1.grid(row = 0)
        self.label2.grid(row = 1)
        self.label3.grid(row = 2,column=0)
        self.label5.grid(row = 2, column=1)
        self.canvas1.grid(row = 3, column=0)
        self.canvas2.grid(row = 3, column=1)
        self.root.mainloop()
    def close_debug_visuals(self):
        self.visualize_a_star = False
        self.root.destroy()
    def debug_set_label_text(self, label, text):
        label['text'] = text
        label.update()
    def debug_add_text_to_label(self, label, text):
        current_text = label['text']
        new_text = current_text + text
        if len(new_text) >100:
            new_text = ""
        label['text'] = new_text
    def debug_draw_cell_margin(self, cell, cell_color):
        funky = self.funky
        cellsize = self.cell_size
        i, j = cell[0], cell[1]
        self.canvas1.create_rectangle(i*cellsize+funky,j*cellsize+funky,i*cellsize+cellsize-funky,j*cellsize+cellsize-funky, outline=cell_color)
        self.canvas1.update()
    def debug_draw_cell(self, cell, cell_color):
        cellsize = self.cell_size
        i, j = cell[0], cell[1]
        self.canvas1.create_rectangle(i*cellsize+self.funky,j*cellsize+self.funky,i*cellsize+cellsize-self.funky,j*cellsize+cellsize-self.funky,fill=cell_color, outline=cell_color)
        self.canvas1.update()
    def debug_draw_grid(self, grid):
        self.canvas1.delete('all')
        cellsize = self.cell_size
        for i in range(len(grid)):
            for j in range(len(grid[i])):   
                color = self.app.cell_type_to_color(grid[i][j])
                if color != None: #don't draw transparent values
                    self.canvas1.create_rectangle(i*cellsize,j*cellsize,i*cellsize+cellsize,j*cellsize+cellsize,fill=color, outline=color)
        self.canvas1.update()
    def update_canvas2_values(self, cell, f):
        i_can_be_aresed = False
        if i_can_be_aresed:
            cellsize = self.cell_size
            i, j = cell[0], cell[1]
            color = self.hue_to_hex(self.get_hue(f,0,self.sizex*2))
            self.canvas2.create_rectangle(i*cellsize,j*cellsize,i*cellsize+cellsize,j*cellsize+cellsize,fill=color, outline=color)
    def get_hue(self, number, min_value, max_value):
        hue_range = 360  # Hue range in degrees

        if number < min_value:
            number = min_value
        elif number > max_value:
            number = max_value

        normalized_value = (number - min_value) / (max_value - min_value)  # Normalize the value within the range

        hue = normalized_value * hue_range  # Calculate the hue value
        hue = int(hue)  # Convert the hue to an integer

        return hue
    def hue_to_hex(self, hue):
        # Convert hue to RGB
        rgb = colorsys.hsv_to_rgb(hue / 360, 1, 1)
        
        # Scale RGB values to 0-255 range
        rgb_scaled = [int(val * 255) for val in rgb]
        
        # Convert RGB to hexadecimal color representation
        hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb_scaled)
        
        return hex_color

# actual start test

    def start_test_3(self):
        self.debug_visuals()
        rooms_per_rib = 5
        spine_margin = 3
        room_coords = self.gen_spine_organisation(rooms_per_rib, spine_margin, self.structure_generation_try_amount, self.margin, self.min_room_size, self.max_room_size)

        for a in room_coords:
            self.structure_list.append(self.return_random_structure(a[0],a[1],a[2],a[3],secrets.token_hex(5)))
        
        # generate paths list
        self.main_generate_connecting_path()
            
        # write path and structure list into layout
        self.write_structure_list_into_layout_grid()
        self.write_path_list_into_layout_grid()

        #write both list into file
        self.write_structure_list_into_file()
        self.write_cell_type_list_into_file()
        
        self.fwh.clear_csv(self.battle_map_save_file+"\\Layout.csv")
        self.fwh.write_array_to_csv(self.battle_map_save_file+"\\Layout.csv", self.mp.grid)

# size changes        
    def change_size(self, n_dif, e_dif, s_dif, w_dif, new_chunk_sizex, new_chunk_sizey): 
        self.width = new_chunk_sizex
        self.height = new_chunk_sizey

        for structure in self.structure_list:
            if structure.x1 < -1*w_dif or structure.y1 < -1*n_dif:
                self.structure_list.remove(structure)
            else: # correct coords since NW are the origin coords
                structure.x1 += w_dif
                structure.x2 += w_dif
                structure.y1 += n_dif
                structure.y2 += n_dif
        
            if structure.x2 > self.sizex+e_dif or structure.y2 > self.sizey+s_dif:
                self.structure_list.remove(structure)
                # no need to correct coords since NW are the origin coords

        # delete out of bound paths - update coords for pathlist
        for path in self.path_list:
            if (path[0] < -1*w_dif) or (path[0] > self.sizex+e_dif) or (path[1] < -1*n_dif) or (path[1] > self.sizey+s_dif):
                self.path_list.remove(path)
            else:
                path[0] += w_dif
                path[1] += n_dif

        # after delete structures, update sizex and sizey
        self.sizex += e_dif + w_dif
        self.sizey += n_dif + s_dif

        self.mp.sizex += e_dif + w_dif
        self.mp.sizey += n_dif + s_dif

        #rewrite structures and paths into layout
        self.mp.clear_cache()
        self.write_structure_list_into_layout_grid()
        self.write_path_list_into_layout_grid()

        self.check_void_helper_grid = [[0 for _ in range(self.sizey)] for _ in range(self.sizex)]
        self.check_rooms_connected_grid = [["void" for _ in range(self.sizey)] for _ in range(self.sizex)]

# extract structure types

    def extract_structure_types(self):
        temp = self.fwh.csv_to_array(self.structure_types_file_path, 1) #skips 1 line of header
        self.structure_types_CSV = temp
        returnA = []
        for i in temp:
            if i[1] == "None":
                i[1] = None
            returnA.append(i[1])
        print(returnA)
        self.structure_types = returnA

# - - - Room Generation - - - #

    # room gen helper

    def generate_valid_random_room_coords(self, rx1, ry1, rx2, ry2, try_amount, margin, minsize, maxsize): #localise - return sucess + coords
        stop = False
        tries = 0
        success = False
        while stop == False:
            x1, y1, x2, y2 = self.generate_random_room_coords(rx1, ry1, rx2, ry2, margin, minsize, maxsize)
            if x1 != -1:
                success = True
                break
            elif tries >= try_amount:
                success = False
                print("Room Unsuccessfully Generated. Tries: ", tries, rx1, ry1, rx2, ry2, margin, minsize, maxsize)
                break
            tries+=1
        print("Room Successfully Generated. Tries: ", tries, rx1, ry1, rx2, ry2, margin, minsize, maxsize)
        return success, x1, y1, x2, y2
    def generate_random_room_coords(self, rx1, ry1, rx2, ry2, margin, minsize , maxsize): #semi localise    
        #apply margin shrink
        rx1 += margin
        ry1 += margin
        rx2 -= margin
        ry2 -= margin
        #check if range is witihn
        rx1, ry1, rx2, ry2 = self.mp.xy_order_helper(rx1, ry1, rx2, ry2)
        if self.mp.check_x1y1x2y2_in_range(rx1, ry1, rx2, ry2) == False:
            print("Not in range from structure generator")
            return -1, -1, -1, -1

        sizex = random.randint(minsize, maxsize)
        sizey = random.randint(minsize, maxsize)

        #enforcing size prioty in generation
        x1 = random.randint(rx1, rx2)
        y1 = random.randint(ry1, ry2)
        x2 = x1 + sizex-1
        y2 = y1 + sizey-1

        x1 ,y1 ,x2 ,y2 = self.mp.xy_order_helper(x1 ,y1 ,x2 ,y2)

        #check if random generated coord is with range
        if x2 > rx2 or y2 > ry2:
            return -1, -1, -1 , -1
        
        #check for current overlappings with margins
        if self.check_void_helper_grid_check_void(x1-margin, y1-margin, x2+margin, y2+margin):
            return x1, y1, x2, y2
        else:
            return -1, -1, -1 , -1

    # check void helpers
    def clear_check_void_helper_grid(self):
        self.check_void_helper_grid = [[0 for _ in range(self.sizey)] for _ in range(self.sizex)]
    def write_check_void_helper_grid(self,x1,y1,x2,y2): # write a rectangle
        for i in range(x1,x2+1):
            for j in range(y1,y2+1):
                self.check_void_helper_grid[i][j] = 1
    def check_void_helper_grid_check_void(self, x1, y1, x2, y2): # check if it is all void within the given region
        is_all_void = True
        for i in range(x1, x2+1):
            for j in range(y1, y2+1):
                if (self.check_void_helper_grid[i][j] == 0 or self.check_void_helper_grid[i][j] == "void") == False:
                    j = y2
                    i = x2
                    is_all_void = False
        return is_all_void
    def write_grid_into_check_void_helper_grid(self, x1, y1, clipgrid): # write rooms
        if x1+1+len(clipgrid) < self.sizex or y1+1+len(clipgrid[0]) < self.sizey:
            for i in range(0, len(clipgrid)):
                for j in range(0, len(clipgrid[0])):
                    if clipgrid[i][j] != "void": #do not write void into grid
                        self.check_void_helper_grid[x1+i][y1+j] = clipgrid[i][j]
        else:
            print("Error, Out of Range", x1+1+len(clipgrid) - self.sizex, y1+1+len(clipgrid[0]) - self.sizey)
            return "error"
        
    def write_structure_list_into_check_void_helper_grid(self):
        for structure in self.structure_list:
            self.write_grid_into_check_void_helper_grid(structure.x1, structure.y1, structure.grid)
    def write_path_list_into_check_void_helper_grid(self):
        path_radius = self.path_radius
        for a in self.path_list:
            x1 = a[0]-path_radius
            y1 = a[1]-path_radius
            x2 = a[0]+path_radius
            y2 = a[1]+path_radius

            while x1 < 0:
                x1 += 1
            while y1 < 0:
                y1 += 1
            while x2 >= self.sizex:
                x2 += -1
            while y2 >= self.sizey:
                y2 += -1
            self.write_check_void_helper_grid(x1,y1,x2,y2)
            

    # specific room layout format - returns coords[][x1, y1, x2, y2] - takes current chunkgrid and chunk size

    def gen_1_room_per_chunk_organisation(self, try_amount, margin, minsize, maxsize): #finished
        rooms_coords = []
        success = False
        prc = [0, 0, 0, 0] #potential_room_coords
        rx1, ry1, rx2, ry2 = 0,0,0,0

        self.clear_check_void_helper_grid()
        self.write_structure_list_into_check_void_helper_grid()
        self.write_path_list_into_check_void_helper_grid()

        for i in range(0,self.width):
            for j in range(0,self.height):
                success = False
                prc = [0, 0, 0, 0] #for some reason i need to reset this.
                rx1, ry1 = self.chunk_size*i, self.chunk_size*j
                rx2, ry2 = self.chunk_size*(i+1)-1, self.chunk_size*(j+1)-1 #-1 cause index
                success, prc[0], prc[1], prc[2], prc[3] = self.generate_valid_random_room_coords(rx1, ry1, rx2, ry2, try_amount, margin, minsize, maxsize)

                if success:
                    rooms_coords.append(prc)
                    self.write_check_void_helper_grid(prc[0], prc[1], prc[2], prc[3])


        self.clear_check_void_helper_grid()
        return rooms_coords
    def gen_spine_organisation(self, rooms_per_rib, spine_margin, try_amount, margin, minsize, maxsize): # doesnt use chunks, just split in half
        middle_of_grid = math.floor(self.sizex/2)
        #bass gen variable
        rooms_coords = []
        success = False
        prc = [0, 0, 0, 0] #potential_room_coords
        rx1, ry1, rx2, ry2 = 0,0,0,0

        self.clear_check_void_helper_grid()
        self.write_structure_list_into_check_void_helper_grid()
        self.write_path_list_into_check_void_helper_grid()

        #generate left rib
        for _ in range(0, rooms_per_rib):
            success = False #reset
            prc = [0, 0, 0, 0]
            rx1, ry1 = 0,0
            rx2, ry2 = middle_of_grid - spine_margin ,self.sizey-1

            success, prc[0], prc[1], prc[2], prc[3] = self.generate_valid_random_room_coords(rx1, ry1, rx2, ry2, try_amount, margin, minsize, maxsize)
            if success:
                rooms_coords.append(prc)
                self.write_check_void_helper_grid(prc[0], prc[1], prc[2], prc[3])

        for _ in range(0, rooms_per_rib):
            success = False #reset
            prc = [0, 0, 0, 0]
            rx1, ry1 = middle_of_grid + spine_margin,0
            rx2, ry2 = self.sizex-1,self.sizey-1

            success, prc[0], prc[1], prc[2], prc[3] = self.generate_valid_random_room_coords(rx1, ry1, rx2, ry2, try_amount, margin, minsize, maxsize)
            if success:
                rooms_coords.append(prc)
                self.write_check_void_helper_grid(prc[0], prc[1], prc[2], prc[3])

        self.clear_check_void_helper_grid()

        #place spine

        for a in range(0, self.sizey):
            temp_path = [middle_of_grid,a]
            self.path_list.append(temp_path)

        return rooms_coords
    def gen_any_and_everywhere(self, try_amount, margin, minsize, maxsize ,max_room_amount): #finished
        rooms_coords = []
        success = False

        self.clear_check_void_helper_grid()
        self.write_structure_list_into_check_void_helper_grid()
        self.write_path_list_into_check_void_helper_grid()

        rx1, ry1 = 0+margin, 0+margin
        rx2, ry2 = self.sizex-margin-1, self.sizey-margin-1 #-1 cause index

        for _ in range(0,max_room_amount):
            success = False
            prc = [0, 0, 0, 0] #for some reason i need to reset this.
            success, prc[0], prc[1], prc[2], prc[3] = self.generate_valid_random_room_coords(rx1, ry1, rx2, ry2, try_amount, margin, minsize, maxsize)

            if success:
                rooms_coords.append(prc)
                self.write_check_void_helper_grid(prc[0], prc[1], prc[2], prc[3])

        self.clear_check_void_helper_grid()
        return rooms_coords

    #set grid size generation

    def hypixel_dungeon(self, try_amount, margin, minsize, maxsize): #NOT_finished AT ALL
        chunk_grid = self.chunk_grid #0 for empty, 1 for filled in
        rooms_coords = []
        success = False
        prc = [0, 0, 0, 0, 0, 0] #potential_room_coords + potential mid points for L rooms
        rx1, ry1, rx2, ry2 = 0,0,0,0
        self.clear_check_void_helper_grid()
        
        
        
        for i in range(0,self.width):
            for j in range(0,self.height):
                success = False
                prc = [0, 0, 0, 0] #for some reason i need to reset this.

                chunkx1 = 0
                chunky1 = 0
                chunkx2 = 0
                chunky2 = 0


                rx1, ry1 = self.chunk_size*chunkx1, self.chunk_size*chunky1
                rx2, ry2 = self.chunk_size*(chunkx2+1)-1, self.chunk_size*(chunky2+1)-1 #-1 cause randint range

                success, prc[0], prc[1], prc[2], prc[3] = rx1, ry1, rx2, ry2

                if success:
                    rooms_coords.append(prc)
                    self.write_check_void_helper_grid(prc[0], prc[1], prc[2], prc[3])


        self.clear_check_void_helper_grid()
        return rooms_coords

# - - - Path Generation - - - #

    # generate coords for connections
 
    def choose_random_point_with_cell_values(self, grid, cell_value, tries):
        sizex = len(grid)
        sizey = len(grid[0])
        for i in range(tries*10):
            randx = random.randint(0,sizex-1)
            randy = random.randint(0,sizey-1)
            if grid[randx][randy] == cell_value:
                print(f"Try number {i}: Cell found with {cell_value}: {randx}, {randy}")
                if self.visualize_a_star == True:
                    self.debug_draw_cell([randx, randy], 'white')
                return randx, randy
            print(f"Try number {i}: No cell Value Found at {randx}, {randy} with {cell_value}: {grid[randx][randy]}")
        
        print(f"No cell Found with {cell_value}")
        return -1, -1
    def grid_to_find_path_format(self, grid_in):
        sizex = len(grid_in)
        sizey = len(grid_in[0])

        grid_out = [["" for _ in range(sizey)] for _ in range(sizex)]
        for i in range(sizex):
            for j in range(sizey):
                if grid_in[i][j] == "void" or grid_in[i][j] == " ":
                    grid_out[i][j] = "void"
                else:
                    grid_out[i][j] = "not_void"
        return grid_out
    def find_nearest_cell_value(self, x1, y1, grid, cell_value):#but somehow has be void as well
        rows = len(grid[0]) #sizey
        cols = len(grid) #sizex

        # Initialize a queue for the breadth-first search
        queue = [(x1, y1)]
        visited = set([(x1, y1)])

        while queue:
            x, y = queue.pop(0)

            # qualifying statement
            if (grid[x][y] == cell_value and cell_value != "wall") or (cell_value == "wall" and self.check_neighboring_cell_contain(x, y, grid, "path")):
                return (x, y)

            # Check the neighboring cells
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy

                if  nx >= 0 and nx < cols and ny >= 0 and ny < rows and (nx, ny) not in visited:
                    queue.append((nx, ny))
                    visited.add((nx, ny))

        return -1, -1
    
    # Path finding - Astar
    
    def main_generate_connecting_path(self, debug_visuals = False):
        if debug_visuals:
            self.debug_visuals()
        # initial variables
        tries = self.path_generation_try_amount
        force_grid = self.force_grid
        force_grid_offsetx, force_grid_offsety = self.force_grid_offset, self.force_grid_offset
        margin = self.margin

        # initialize 
        self.clear_all_check_all_rooms_connected_grid()
        self.write_structure_list_into_check_all_rooms_connected_grid()
        self.write_path_into_check_all_rooms_connected_grid(self.path_list)
        self.establish_root_of_recurssive_expansion()
        potential_new_paths = []

        close_node_tries = (self.sizex+self.sizey)*0.5*force_grid #average length of path
        success = False

        if self.enforce_margin == True:
            self.establish_structure_margins_in_check_all_rooms_connected_grid(margin)
        
        # --- force grid --- #
        if force_grid > 1:
            for i in range(0,self.sizex-1):
                for j in range(0,self.sizey-1):
                    if (i+force_grid_offsetx) % force_grid != 0 and (j+force_grid_offsety) % force_grid != 0:
                        self.check_rooms_connected_grid[i][j] = 'wall'
        elif force_grid <= 1:
            force_grid = 1
        # --- abandone this ideaa for now --- #

        for _ in range(tries):            
            #self.establish_structure_margins_in_check_all_rooms_connected_grid(margin)
            if self.check_rooms_connected_recurssive_expansion(_) == False: #expand root to all related cells
                         
                x, y = self.choose_random_point_with_cell_values(self.check_rooms_connected_grid, "void", tries)
                # choose random cell to extend thy grasp into nearest connection and wall cell
                if x == -1:
                    return False
                
                if self.enforce_margin == True:
                    self.establish_path_margins_in_check_all_rooms_connected_grid(margin)
            
                x1, y1 = self.find_nearest_cell_value(x,y, self.check_rooms_connected_grid, "connection")
                
                if self.enforce_margin == True:
                    x2, y2 = self.find_nearest_cell_value(x,y, self.check_rooms_connected_grid, "path")
                else:
                    x2, y2 = self.find_nearest_cell_value(x,y, self.check_rooms_connected_grid, "wall")
                
                # make sure these two burrows out to void
                if self.enforce_margin == True:
                    x1, y1, x2, y2, potential_new_paths = self.start_end_burrow_out_of_margin(x1,y1,x2,y2,margin, force_grid)

                if x1 == -1:
                    print("find_nearest_cell: No such cell Values exist") #fucking probelm

                else:            
                    start = [x1,y1]
                    end = [x2,y2]
                    # print(f"Start: {x1, y1} | End: {x2, y2}") # debug
                    paths = self.A_star_find_path(self.check_rooms_connected_grid, start, end, close_node_tries)

                    # print("pathlist:", type(self.path_list), type(paths), "\n\n\n\n\n")

                    if paths != None and paths != []: #draw in the paths
                        self.write_path_into_check_all_rooms_connected_grid(paths+potential_new_paths)
                        self.path_list = self.path_list+paths+potential_new_paths
            else:
                success = True
                break
            print("\n")
        return success
    def A_star_find_path(self, grid_input, start, end, Close_node_tries):
        grid = self.grid_to_find_path_format(grid_input) #convert to this BSF version, but not affecting the original
        sizey = len(grid[0])
        sizex = len(grid) 

        grid[start[0]][start[1]] = "void"
        grid[end[0]][end[1]] = "void"
        
        G_cost = [[10000] * sizey for _ in range(sizex)] #walking distance from starting node
        H_cost = [[10000] * sizey for _ in range(sizex)] #heuristic distance from end node
        F_cost = [[10000] * sizey for _ in range(sizex)] # fcost + gccost

        open_nodes = []
        closed_nodes = []
        path_taken = {}

        newly_added_closed_node = start
        closed_nodes.append(newly_added_closed_node)

        # set start and end g h f cost
        G_cost[start[0]][start[1]] = 0
        H_cost[start[0]][start[1]] = abs(start[0] - end[0]) + abs(start[1] - end[1])
        F_cost[start[0]][start[1]] = abs(start[0] - end[0]) + abs(start[1] - end[1])

        G_cost[end[0]][end[1]] = 0
        H_cost[end[0]][end[1]] = 0
        F_cost[end[0]][end[1]] = 0

        if self.visualize_a_star == True:
            self.debug_draw_grid(grid_input)

        tries = 0
        
        while newly_added_closed_node != end:
            if tries > Close_node_tries:
                return []
            tries +=1

            if self.visualize_a_star == True and self.detailed_visualisation == True:
                self.debug_set_label_text(self.label2, '')
                for p in closed_nodes:
                    self.debug_add_text_to_label(self.label2, f"[{p[0]},{p[1]}]  ")
                    self.debug_draw_cell(p, 'orange')
                    self.update_canvas2_values(p, F_cost[p[0]][p[1]])
                self.debug_set_label_text(self.label3, '')
                for p in open_nodes:
                    self.debug_add_text_to_label(self.label3, f"[{p[0]},{p[1]}]  ")
                    self.update_canvas2_values(p, F_cost[p[0]][p[1]])
                    self.debug_draw_cell(p, 'yellow')

            if self.visualize_a_star == True:
                self.debug_draw_cell(start, 'green')
                self.debug_draw_cell(end, 'purple')


            #print(f"Newly Added Closed Node: {newly_added_closed_node}")
            #add new open nodes of recently close_nodes and their path
            temp_new_open_nodes = self.A_star_return_neighbor_nodes(grid,newly_added_closed_node[0],newly_added_closed_node[1], closed_nodes, open_nodes, "empty")
            open_nodes = open_nodes + temp_new_open_nodes
            for a in temp_new_open_nodes: #initiate a random but sense making path
                path_taken[tuple(a)] = newly_added_closed_node
                #print(f"Newly Added Open Node: {a}")
                if self.visualize_a_star == True:
                    self.debug_draw_cell(newly_added_closed_node, 'yellow') #visualize?

            #print("Starts revaluating lowest g values")

            #reevaluate all the open_nodes path for lowest g value
            if self.a_star_evaluate_g_values == True:
                for a in open_nodes:
                    temp_neighbor_close_nodes = self.A_star_return_neighbor_nodes(grid,a[0],a[1],closed_nodes,open_nodes,"closed")
                    
                    if temp_neighbor_close_nodes == []: #fix that constant issue
                        temp_neighbor_close_nodes == [[a[0],a[1]]]
                    else:   
                        temp_lowest_g_cost_node = temp_neighbor_close_nodes[0]
                    
                    
                    for b in temp_neighbor_close_nodes:
                        print(f"Potential path root nodes of {a} change to {b}")
                        if G_cost[b[0]][b[1]] <= G_cost[temp_lowest_g_cost_node[0]][temp_lowest_g_cost_node[1]]:
                            temp_lowest_g_cost_node = b

                    if path_taken[tuple(a)] != temp_lowest_g_cost_node:
                        path_taken[tuple(a)] = temp_lowest_g_cost_node
                        print(f"Lowest change to {b}")

            #calculate every open node's GHF cost, closed nodes stay the same
            lowest_fcost_in_open_nodes = 10000000000000

            #print(f"\nStart value: {start} | Lowest fcost value: {lowest_fcost_in_open_nodes}\n")
            for a in open_nodes:
                temp_close_node = path_taken[tuple(a)]
                G_cost[a[0]][a[1]] = G_cost[temp_close_node[0]][temp_close_node[1]]+1
                H_cost[a[0]][a[1]] = 2* abs(a[0] - end[0]) + 2* abs(a[1] - end[1])
                F_cost[a[0]][a[1]] = G_cost[a[0]][a[1]] + H_cost[a[0]][a[1]]

                if F_cost[a[0]][a[1]] < lowest_fcost_in_open_nodes: #get lowest f cost
                    lowest_fcost_in_open_nodes = F_cost[a[0]][a[1]]
                    #print(f"Lowest Fcost Open Node: {a}")
                    if self.visualize_a_star == True:
                        self.debug_set_label_text(self.label5, f"Lowest Fcost Open Node: {a}") # Lowest Fcost Open Nodes
                #print(f"Open Nodes {a} GHF Value: {G_cost[a[0]][a[1]]}, {H_cost[a[0]][a[1]]}, {F_cost[a[0]][a[1]]}")
                
            temp_low_fcost_nodes = []
            for a in open_nodes:
                if lowest_fcost_in_open_nodes == F_cost[a[0]][a[1]]:
                    temp_low_fcost_nodes.append(a)
                    if self.visualize_a_star == True:
                        self.debug_add_text_to_label(self.label5, f"[{a[0]},{a[1]}]  ")
                        self.update_canvas2_values(a, 0)

            newly_added_closed_node = temp_low_fcost_nodes[0] #node with the lowest fcost and h cost
            for a in temp_low_fcost_nodes:
                if H_cost[newly_added_closed_node[0]][newly_added_closed_node[1]] > H_cost[a[0]][a[1]]:
                    newly_added_closed_node = a

            closed_nodes.append(newly_added_closed_node) #restart loop
            open_nodes.remove(newly_added_closed_node)
            #print(f"Newly Added Closed Node: {newly_added_closed_node}")

            #update visualisation
            if self.visualize_a_star == True:
                self.debug_draw_cell(newly_added_closed_node, 'orange')
                self.debug_set_label_text(self.label1, "ADDED")
        
        #return path array.
        return_path = [end]
        path_tracer  = end
        while path_tracer  != start:
            path_tracer  = path_taken[tuple(path_tracer)]
            return_path.append(path_tracer)
        return_path.append(tuple(start))
        return return_path
    def A_star_return_neighbor_nodes(self, grid, x1, y1, closed_nodes,open_nodes, state): #fixed
        
        def cell_is_in_list(cell, cell_list):
            for a in cell_list:
                if a == cell:
                    return True
            return False
    
        nx = x1
        ny = y1 -1
        ex = x1 +1
        ey = y1
        sx = x1
        sy = y1 +1
        wx = x1 -1
        wy = y1

        sizex = len(grid)
        sizey = len(grid[0])


        # check if cells on border
        cell_array = [[nx, ny],[ex, ey], [sx, sy],[wx, wy]]
        #print(f"Initial Neighbors - {cell_array}")

        if x1 == 0: # on the west border
            cell_array.remove([wx, wy])
        if x1 == sizex-1: # on the east border
            cell_array.remove([ex, ey])
        if y1 == 0: # on the north border
            cell_array.remove([nx, ny])
        if y1 == sizey-1: # on the south border
            cell_array.remove([sx, sy])
            
        for a in cell_array:
            removed = False
            if self.visualize_a_star == True:
                self.debug_draw_cell_margin(a, 'orange')
            if grid[a[0]][a[1]] != 'void' or grid[a[0]][a[1]] == "wall":
                cell_array.remove(a)
                removed = True
            elif grid[a[0]][a[1]] == "wall" and removed == False:
                print("Wall detected and somehow not added anyway")
        output = []
        for a in cell_array:
            if (state == "closed" and cell_is_in_list(a, closed_nodes)) or (state == 'open' and cell_is_in_list(a, open_nodes)) or (((cell_is_in_list(a, closed_nodes) or cell_is_in_list(a, open_nodes)) == False and state != 'closed' and state != 'open')):
                output.append(a)
                if self.visualize_a_star == True:
                    self.debug_set_label_text(self.label1, f"{a[0]} , {a[1]}")
                    self.debug_draw_cell_margin(a, 'green')
        return output
           
    # check all rooms connected grid + path finding functions
    
    def clear_all_check_all_rooms_connected_grid(self):
        self.check_rooms_connected_grid = [["void" for _ in range(self.sizey)] for _ in range(self.sizex)]
    def write_structure_list_into_check_all_rooms_connected_grid(self):
        def write_structure_into_check_all_rooms_connected_grid(structure): #DONE
            x1 = structure.x1
            y1 = structure.y1
            clipgrid = structure.grid
            
            if x1+1+len(clipgrid) < self.sizex or y1+1+len(clipgrid[0]) < self.sizey:
                for i in range(0, len(clipgrid)):
                    for j in range(0, len(clipgrid[0])):
                        self.check_rooms_connected_grid[x1+i][y1+j]  = clipgrid[i][j]
            else:
                print("Error, Out of Range", x1+1+len(clipgrid) - self.sizex, y1+1+len(clipgrid[0]) - self.sizey)
                return "error"
        
        for a in self.structure_list:
            write_structure_into_check_all_rooms_connected_grid(a)
    def check_neighboring_cell_contain(self, x1, y1, grid, cell_type):
        nx, ny, ex, ey, sx, sy, wx, wy = 0,0,0,0,0,0,0,0
        nx = x1
        ny = y1 -1
        ex = x1 +1
        ey = y1
        sx = x1
        sy = y1 +1
        wx = x1 -1
        wy = y1

        sizex = len(grid)
        sizey = len(grid[0])

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
        for a in cell_array:
            if grid[a[0]][a[1]] == cell_type:
                return True

        return False
    def check_rooms_connected_recurssive_expansion(self, try_number): # should be working
        # recurssive to expand out all the cells
        cell_spread_in_cycle = True
        cell_spread_cycpe_no = 0
        while cell_spread_in_cycle:
            cell_spread_in_cycle = False
            for i in range(0, self.sizex):
                for j in range(0, self.sizey):
                    if self.check_rooms_connected_grid[i][j] != "void" and self.check_rooms_connected_grid[i][j] != "connection" and self.check_rooms_connected_grid[i][j] != "wall":
                        if self.check_neighboring_cell_contain(i,j,self.check_rooms_connected_grid, "connection"):
                            self.check_rooms_connected_grid[i][j] = "connection"
                            cell_spread_in_cycle = True
                            #print(f"Cell spread cycle: {cell_spread_cycpe_no}, cells spread to: {i}, {j}")
            cell_spread_cycpe_no += 1
            
        print("\n=========================\n")
        #check if all cell values are = connection
        for i in range(0, self.sizex):
            for j in range(0, self.sizey):
                local_cell_value = self.check_rooms_connected_grid[i][j]
                if (local_cell_value == "connection" or local_cell_value == "void" or local_cell_value == "wall") == False:
                    print(f"Recursive Expansion All Connected Number {try_number}: False\n")
                    print("\n=========================\n")
                    return False
        print(f"Recursive Expansion All Connected Number {try_number}: True\n")
        print("\n=========================\n")
        return True
        # No such cell Values exist
    def establish_root_of_recurssive_expansion(self):
        #pick one initial point
        check_cell_exist = -1
        for i in range(0, self.sizex):
            for j in range(0, self.sizey):
                if self.check_rooms_connected_grid[i][j] != "void" and self.check_rooms_connected_grid[i][j] != "wall":
                    self.check_rooms_connected_grid[i][j] = "connection" #establish root viral cell
                    #print(f"Root Viral Cell: {i}, {j}")
                    check_cell_exist = 1
                    break
            if check_cell_exist == 1:
                break  # Exit the inner loop

        if check_cell_exist == -1:
            #print("no cells in grid")
            return False
    def establish_structure_margins_in_check_all_rooms_connected_grid(self, margin):
        margin_grid = [["void" for _ in range(self.sizey)] for _ in range(self.sizex)]

        margin = math.floor(margin/2)

        for i in range(0, self.sizex):
            for j in range(0, self.sizey):
                if self.margin_range_contain(i, j, margin,self.check_rooms_connected_grid, "wall"):
                    margin_grid[i][j] = 'wall'

        for i in range(0, self.sizex):
            for j in range(0, self.sizey):
                if margin_grid[i][j] == 'wall' and self.check_rooms_connected_grid[i][j] == 'void':
                    self.check_rooms_connected_grid[i][j] = 'wall'
    def establish_path_margins_in_check_all_rooms_connected_grid(self, margin):
        margin_grid = [["void" for _ in range(self.sizey)] for _ in range(self.sizex)]

        margin = math.floor(margin/2)

        for i in range(0, self.sizex):
            for j in range(0, self.sizey):
                if self.margin_range_contain(i, j, margin,self.check_rooms_connected_grid, "path") or self.margin_range_contain(i, j, margin,self.check_rooms_connected_grid, "connection"):
                    margin_grid[i][j] = 'wall'

        for i in range(0, self.sizex):
            for j in range(0, self.sizey):
                if margin_grid[i][j] == 'wall' and self.check_rooms_connected_grid[i][j] == 'void':
                    self.check_rooms_connected_grid[i][j] = 'wall'
    def margin_range_contain(self, x1,y1,margin,grid, cell_type):
        lengthx = 2*margin+1
        lengthy = 2*margin+1
        x1 -= margin
        y1 -= margin
            
        if x1 < 0:
            lengthx += x1
            x1 = 0
        if y1 < 0:
            lengthy += y1
            y1 = 0

        for i in range(x1, x1+lengthx):
            for j in range(y1, y1+lengthy):
                if (i >= len(grid) or j>=len(grid[0])) == False: #not wanna out of bounds
                    if grid[i][j] == cell_type:
                        return True
        return False
    def margin_range_contain_void(self, x1,y1,margin,grid,force_grid):
        x0, y0 = x1,y1
        lengthx = 2*margin+1+2*force_grid
        lengthy = 2*margin+1+2*force_grid
        x1 -= margin
        y1 -= margin
            
        if x1 < 0:
            lengthx += x1
            x1 = 0
        if y1 < 0:
            lengthy += y1
            y1 = 0

        potential_coords = []
        potential_coords_heuristics = []
        temp_h = 10000000000000

        for i in range(x1, x1+lengthx):
            if (i >= len(grid)) == False:
                if grid[i][y0] == 'void' and abs(i-x0) <= temp_h:
                    if abs(i-x0) < temp_h:
                        potential_coords,potential_coords_heuristics = [],[]
                    temp_h = abs(i-x0)
                    potential_coords.append([i,y0])
                    potential_coords_heuristics.append(abs(i-x0))

        for j in range(y1, y1+lengthy):
            if (j>=len(grid[0])) == False: #not wanna out of bounds
                if grid[x0][j] == 'void' and abs(j-y0) <= temp_h:
                    if abs(j-y0) < temp_h:
                        potential_coords,potential_coords_heuristics = [],[]
                    temp_h = abs(j-y0)
                    potential_coords.append([x0, j])
                    potential_coords_heuristics.append(abs(j-y0))
        
        # return coords with the least heuristic
        if potential_coords == []:
            return -1, -1
        else:
            try:
                a = random.randint(0,len(potential_coords)-1) 
            except ValueError:
                a = 0       
            return potential_coords[a][0], potential_coords[a][1]
    def start_end_burrow_out_of_margin(self, xs,ys,xe,ye,margin,force_grid):
        new_start, new_end = [1,1],[1,1]

        margin = math.floor(margin/2)+2
        # find nearest void values within range
        new_start[0], new_start[1] = self.margin_range_contain_void(xs,ys,margin*2,self.check_rooms_connected_grid,force_grid)
        new_end[0], new_end[1] = self.margin_range_contain_void(xe,ye,margin*2,self.check_rooms_connected_grid,force_grid)  
        if new_start[0] == -1 or new_end[0] == -1:
            return -1, -1, -1, -1, []
        
        potential_new_paths = []

        #burrowing action - potential new paths are burrowed paths

        if new_start[0] == xs and new_start[1] > ys:
            for i in range(ys,new_start[1]+1):
                potential_new_paths.append([xs,i])

        elif new_start[0] == xs and new_start[1] < ys:
            for i in range(new_start[1], ys+1):
                potential_new_paths.append([xs,i])

        elif new_start[1] == ys and new_start[0] > xs:
            for i in range(xs,new_start[0]+1):
                potential_new_paths.append([i,ys])

        elif new_start[1] == ys and new_start[0] < xs:
            for i in range(new_start[0],xs+1):
                potential_new_paths.append([i,ys])
                
        ## SIGH

        if new_end[0] == xe and new_end[1] > ye:
            for i in range(ye,new_end[1]+1):
                potential_new_paths.append([xe,i])

        elif new_end[0] == xe and new_end[1] < ye:
            for i in range(new_end[1], ye+1):
                potential_new_paths.append([xe,i])

        elif new_end[1] == ye and new_end[0] > xe:
            for i in range(xe,new_end[0]+1):
                potential_new_paths.append([i,ye])

        elif new_end[1] == ye and new_end[0] < xe:
            for i in range(new_end[0],xe+1):
                potential_new_paths.append([i,ye])

        return new_start[0], new_start[1], new_end[0], new_end[1], potential_new_paths
    def write_path_into_check_all_rooms_connected_grid(self,paths): #paths array of points
        for a in paths:
            self.write_cell_into_check_all_rooms_connected_grid(a[0],a[1], "path")
            if self.visualize_a_star == True:
                self.debug_draw_cell_margin(a, "red")
        print("Path written into check_connected_grid")
    def write_cell_into_check_all_rooms_connected_grid(self, x, y, cell_type):
        current_cell_type = self.check_rooms_connected_grid[x][y]
        if (cell_type == "entrance") or (current_cell_type == "void") or (cell_type == "path" and current_cell_type != "entrance") or (current_cell_type == "wall"): #Entrance overwrites all for now
            self.check_rooms_connected_grid[x][y] = cell_type

# - - - - - - Map Class Ease of Use Methods - - - - - - #

# procedual step for generating map
        
    def generate_full_map(self):
        a = 1

    def return_random_structure(self, x1, y1, x2, y2, id):
        choice = 0
        choice = random.randint(1,5)
        
        if choice == 1:
            temp_structure = StructureRectangularRoom(x1, y1, x2, y2, id, [1,1,1,1])
        elif choice == 2:
            temp_structure = StructureMaze(x1, y1, x2, y2, id)
        elif choice == 3:
            temp_structure = StructureCircularRoom(x1, y1, x2, y2, id, False)
        elif choice == 4:
            temp_structure = StructureRectangularRoom(x1, y1, x2, y2, id, [1,1,1,1])
        elif choice == 5:
            q = random.randint(1,4)
            midx = math.floor(x1/2 + x2/2)
            midy = math.floor(y1/2 + y2/2)
            temp_structure = StructureLRoom(x1, y1, x2, y2, id, midx, midy, q)
        return temp_structure

# organisational methods
            
    def clear_cache(self):
        self.clear_check_void_helper_grid()
        self.clear_all_check_all_rooms_connected_grid()
        self.structure_list = []
        self.path_list = []
        self.mp.clear_cache()

# Write into Layot

    def write_structure_list_into_layout_grid(self):
        for a in self.structure_list:
            self.mp.write_rooms_into_grid(a.x1, a.y1, a.grid)
    def write_path_list_into_layout_grid(self):
        path_radius = self.path_radius
        for a in self.path_list:
            x1 = a[0]-path_radius
            y1 = a[1]-path_radius
            x2 = a[0]+path_radius
            y2 = a[1]+path_radius

            while x1 < 0:
                x1 += 1
            while y1 < 0:
                y1 += 1
            while x2 >= self.sizex:
                x2 += -1
            while y2 >= self.sizey:
                y2 += -1
            temporary_grid = self.mp.generate_rectangular_room(x1, y1, x2, y2)
            self.mp.write_rooms_into_grid(x1, y1, temporary_grid)
            if a[0] == 0 or a[0]  == self.sizex-1 or a[1] == 0 or a[1]  == self.sizey-1:
                self.mp.write_cell(a[0], a[1], "path")
    def write_hazard_list_into_layout_grid(self):
        for coords in self.hazard_list:
            self.mp.write_cell(coords[0], coords[1], "hazard_1")
    def write_water_list_into_layout_grid(self):
        for coords in self.hazard_list:
            self.mp.write_cell(coords[0], coords[1], "water_1")
# Save to File
            
    def write_structure_list_into_file(self):
        structure_list_path = self.battle_map_save_file+"\\json_lists\\structure_list.json"
        self.fwh.clear_json_file(structure_list_path)
        self.fwh.clear_folder(self.battle_map_save_file+"\\structure_list_layout")
        array_of_structure_dicts = []

        for a in self.structure_list:
            array_of_structure_dicts.append(a.get_structure_properties_as_dict())
            
            # write grid information into folder
            id_value = a.id_value
            individual_layout_path = self.battle_map_save_file+"\\structure_list_layout\\"+str(id_value)+".csv"
            self.fwh.write_array_to_csv(individual_layout_path,a.grid)
        self.fwh.write_array_of_dicts_to_json(array_of_structure_dicts,structure_list_path)    
    def write_cell_type_list_into_file(self):
        path_list_path = self.battle_map_save_file+"\\cell_type_list_layout\\path_list.csv"
        hazard_list_path = self.battle_map_save_file+"\\cell_type_list_layout\\hazard_list.csv"
        water_list_path = self.battle_map_save_file+"\\cell_type_list_layout\\water_list.csv"

        self.fwh.clear_csv(path_list_path)
        self.fwh.clear_csv(hazard_list_path)
        self.fwh.clear_csv(water_list_path)

        self.fwh.write_array_to_csv(path_list_path,self.path_list)
        self.fwh.write_array_to_csv(hazard_list_path,self.hazard_list)
        self.fwh.write_array_to_csv(water_list_path,self.water_list)



