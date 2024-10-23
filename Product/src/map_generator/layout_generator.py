from helpers.file_write_helper import FileWriteHelper
import random

class LayoutGenerator:
    def __init__(self, sizex, sizey, battle_map_save_file,file_paths):
        self.sizex = sizex
        self.sizey = sizey
        self.battle_map_save_file = battle_map_save_file
        self.file_paths = file_paths

        # at this point its the only class that matter but it will stay

        self.grid = [["void" for _ in range(sizey)] for _ in range(sizex)] #x -> y -> properties

        #helpers
        self.fwh = FileWriteHelper()

        self.cell_types_file_path = self.file_paths['application_path'] + self.file_paths['cell_types.csv']
        self.cell_type_layout_hiearchy_file_path = self.file_paths['application_path'] + self.file_paths['cell_type_layout_hiearchy.csv']

        self.cell_types = []
        self.cell_types_CSV = []
        self.cell_type_layout_hiearchy = []
        self.extract_all_files()
    
    # CSV Function

    def clear_cache(self):
        self.grid = [["void" for _ in range(self.sizey)] for _ in range(self.sizex)]

    def extract_all_files(self):
        temp = self.fwh.csv_to_array(self.cell_types_file_path, 1) #skips 1 line of header
        self.cell_types_CSV = temp
        returnA = []
        for i in temp:
            if i[1] == "None":
                i[1] = None
            returnA.append(i[1])
        print(returnA)
        self.cell_types = returnA

        self.cell_type_layout_hiearchy = self.fwh.csv_to_array(self.cell_type_layout_hiearchy_file_path,0)

    def gridToString(self):
        for a in self.grid:
            print(a)

    def generate_noise(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                text = self.cell_types[random.randint(0, len(self.cell_types)-1)]
                self.grid[i][j] = text

# generator function returns 2D Array - rooms, requires write_rooms_into_grid()
# structure_organiser will write the structure into file before calling generator functions

# Room generator helper width helpers

    def xy_order_helper(self, x1, y1, x2, y2):
        # reoganize and make function flexible
        helper_x = [x1, x2]
        helper_y = [y1, y2]

        x1 = min(helper_x)
        x2 = max(helper_x)
        y1 = min(helper_y)
        y2 = max(helper_y)
        
        return x1, y1, x2, y2
    def write_rooms_into_grid(self, x1, y1, clipgrid):
        if x1+1+len(clipgrid) < self.sizex or y1+1+len(clipgrid[0]) < self.sizey:
            for i in range(0, len(clipgrid)):
                for j in range(0, len(clipgrid[0])):
                    self.write_cell(x1+i,y1+j,clipgrid[i][j])
        else:
            print("Error, Out of Range", x1+1+len(clipgrid) - self.sizex, y1+1+len(clipgrid[0]) - self.sizey)
            return "error"
    def write_cell(self, x, y, overwrite):
        base = self.grid[x][y]
        # find index of both
        for i in range(1,len(self.cell_type_layout_hiearchy)):
            if str(self.cell_type_layout_hiearchy[i][0]) == overwrite:
                overwrite_index = i
        for j in range(1,len(self.cell_type_layout_hiearchy[0])):
            if str(self.cell_type_layout_hiearchy[0][j]) == base:
                base_index = j
        if self.cell_type_layout_hiearchy[overwrite_index][base_index] == "TRUE":
            self.grid[x][y] = overwrite
    def check_x1y1x2y2_in_range(self, x1, y1, x2, y2):
        return_val = True
        if x1 < 0 or x1 > len(self.grid)-1:
            print("Erorr out of range", x1, self.sizex)
            return_val = False
        if x2 < 0 or x2 > len(self.grid)-1:
            print("Erorr out of range", x2, self.sizex)
            return_val = False
        if y1 < 0 or y1 > len(self.grid[0])-1:
            print("Erorr out of range", y1, self.sizey)
            return_val = False
        if y2 < 0 or y2 > len(self.grid[0])-1:
            print("Erorr out of range", y2, self.sizey)
            return_val = False
        return return_val
    def generate_fill_grid(self, sizex, sizey, celltype):
        grid = []
        for _ in range(sizex):
            row = [celltype] * sizey
            grid.append(row)
        return grid
    def check_cell_grid_area_is_all_void(self, x1, y1, x2, y2): #self.mp.grid.fucntions
        is_all_void = True
        for i in range(x1, x2+1):
            for j in range(y1, y2+1):
                if self.grid[i][j] != "void":
                    j = y2
                    i = x2
                    is_all_void = False
        return is_all_void
    

# grid manipulation methods
    def rotate_grid_3oclock(self, input_grid):
        sizex = len(input_grid)
        sizey = len(input_grid[0])
        # Create a new grid with dimensions swapped
        output_grid = [["void" for _ in range(sizex)] for _ in range(sizey)] #flip size x and size y
        
        for i in range(sizex):
            for j in range(sizey):
                output_grid[sizey-j-1][i] = input_grid[i][j]
        return output_grid
    def rotate_grid_6oclock(self, input_grid):
        sizex = len(input_grid)
        sizey = len(input_grid[0])
        # Create a new grid with dimensions swapped
        output_grid = [["void" for _ in range(sizey)] for _ in range(sizex)] #DONT flip size x and size y
        
        for i in range(sizex):
            for j in range(sizey):
                output_grid[sizex-1-i][sizey-1-j] = input_grid[i][j]
        return output_grid
    def rotate_grid_9oclock(self, input_grid):
        sizex = len(input_grid)
        sizey = len(input_grid[0])
        # Create a new grid with dimensions swapped
        output_grid = [["void" for _ in range(sizex)] for _ in range(sizey)] #flip size x and size y
        
        for i in range(sizex):
            for j in range(sizey):
                output_grid[j][sizex-1-i] = input_grid[i][j]
        return output_grid

    def flip_grid_vertically(self, input_grid):
        sizex = len(input_grid)
        sizey = len(input_grid[0])
        # Create a new grid with dimensions swapped
        output_grid = [["void" for _ in range(sizey)] for _ in range(sizex)] #DONT flip size x and size y
        
        for i in range(sizex):
            for j in range(sizey):
                output_grid[i][sizey-1-j] = input_grid[i][j]
        return output_grid
    def flip_grid_horizontally(self, input_grid):
        sizex = len(input_grid)
        sizey = len(input_grid[0])
        # Create a new grid with dimensions swapped
        output_grid = [["void" for _ in range(sizey)] for _ in range(sizex)] #DONT flip size x and size y
        
        for i in range(sizex):
            for j in range(sizey):
                output_grid[sizex -1-i][j] = input_grid[i][j]
        return output_grid
# maze generator - doesnt need a entrance unless its trapdoor

    def generate_maze_helper(self, maze_height, maze_width):
        maze = [[1] * maze_width for _ in range(maze_height)]
        corridor_length = 1+1

        def recursive_backtracking(row, col):
            maze[row][col] = 0
            directions = [(0, corridor_length), (0, -corridor_length), (corridor_length, 0), (-corridor_length, 0)]
            random.shuffle(directions)

            for dx, dy in directions:
                next_row, next_col = row + dx, col + dy
                if 0 <= next_row < maze_height and 0 <= next_col < maze_width and maze[next_row][next_col] != 0:
                    maze[next_row][next_col] = 0
                    maze[row + dx // 2][col + dy // 2] = 0
                    recursive_backtracking(next_row, next_col)

        recursive_backtracking(1, 1)
        return maze
    def generate_maze(self, x1, y1, x2, y2):
        #check for errors and order helper
        if self.check_x1y1x2y2_in_range(x1, y1, x2, y2) == False:
            return
        x1, y1, x2, y2 = self.xy_order_helper(x1, y1, x2, y2)
        # reoganize and make function flexible
        maze_width = abs(x1-x2+1)
        maze_height = abs(y1-y2+1)
        # make sure its NOT a multiple of 2
        if maze_width%2 == 0:
            x2 += -1
            maze_width += -1
        if maze_height%2 == 0:
            y2 += -1
            maze_height += -1
        
        # Generate random paths using a turtle
        grid = self.generate_maze_helper(maze_width, maze_height)
        for i in range(maze_width):
            for j in range(maze_height):
                if grid[i][j] == 0:
                    grid[i][j] = "path"
                else:
                    grid[i][j] = "wall"
        return grid
    def generate_maze_with_treasure_room(self, x1, y1, x2, y2, x3, y3 ,x4, y4): #somehow not working
        grid = self.generate_maze(x1, y1, x2, y2)
        #check for errors and order helper
        if self.check_x1y1x2y2_in_range(x3, y3 ,x4, y4) == False:
            return
        x3, y3 ,x4, y4 = self.xy_order_helper(x3, y3 ,x4, y4)


        treasure_room = self.generate_rectangular_room(x3, y3 ,x4, y4)

        for i in range(0, len(treasure_room)-1):
            for j in range(0, len(treasure_room[0])-1):
                if treasure_room[i][j] == 'path':
                    grid[i+x3-x1][j+y3-y1]
        return grid
# generate open rooms

    def generate_rectangular_room(self, x1, y1, x2, y2):
        #check for errors and order helper
        if self.check_x1y1x2y2_in_range(x1, y1, x2, y2) == False:
            return
        x1, y1, x2, y2 = self.xy_order_helper(x1, y1, x2, y2)
        grid = []
        sizex = x2-x1+1
        sizey = y2-y1+1
        #populate and pad with void values
        grid = self.generate_fill_grid(sizex, sizey, 'void')

        #fill grid
        for i in range(0, sizex):
            for j in range(0, sizey):
                grid[i][j] = self.cell_types[1]#path
        
        for i in range(0, sizex): 
            grid[i][0] = self.cell_types[2]#wall
            grid[i][sizey-1] = self.cell_types[2]#wall
            
        for j in range(0, sizey):
            grid[0][j] = self.cell_types[2]#wall
            grid[sizex-1][j] = self.cell_types[2]#wall
        return grid
    def generate_simple_corridors(self, x1, y1, x2, y2, direction): #direction = "horizontal" / "vertical"
        #check for errors and order helper
        if self.check_x1y1x2y2_in_range(x1, y1, x2, y2) == False:
            return
        x1, y1, x2, y2 = self.xy_order_helper(x1, y1, x2, y2)

        grid = []
        sizex = x2-x1+1
        sizey = y2-y1+1

        #populate and pad with void values
        grid = self.generate_fill_grid(sizex, sizey, 'void')

        #define middle path
        for i in range(0, sizex):
            for j in range(0, sizey):
                grid[i][j] = self.cell_types[1]#path

        #define walls

        if direction == "horizontal":
            top, bottom = 2, 2 #wall
            left, right = 1, 1 #path
        elif direction == "vertical":
            top, bottom = 1, 1 #path
            left, right = 2, 2 #wall
        
        # define walls
        for i in range(0, sizex): 
            grid[i][0] = self.cell_types[top]
            grid[i][sizey-1] = self.cell_types[bottom]
            
        for j in range(0, sizey):
            grid[0][j] = self.cell_types[left]
            grid[sizex-1][j] = self.cell_types[right]

        #patch the corners
        grid[0][0] = self.cell_types[2]#wall
        grid[0][sizey-1] = self.cell_types[2]#wall
        grid[sizex-1][0] = self.cell_types[2]#wall
        grid[sizex-1][sizey-1] = self.cell_types[2]#wall

        return grid
    def generate_flexible_rectangle(self, x1, y1, x2, y2, N, E, S, W): #NESW = fill cell index
        #check for errors and order helper
        if self.check_x1y1x2y2_in_range(x1, y1, x2, y2) == False:
            return
        x1, y1, x2, y2 = self.xy_order_helper(x1, y1, x2, y2)

        grid = []
        sizex = x2-x1+1
        sizey = y2-y1+1
        #populate and pad with void values
        grid = self.generate_fill_grid(sizex, sizey, 'void')

        #define middle path
        for i in range(0, sizex):
            for j in range(0, sizey):
                grid[i][j] = self.cell_types[1]#path

        #define walls - 1 path | 2 walls

        top = N
        right = E
        bottom = S
        left = W
        
        # define walls
        for i in range(0, sizex): 
            grid[i][0] = self.cell_types[top]
            grid[i][sizey-1] = self.cell_types[bottom]
            
        for j in range(0, sizey):
            grid[0][j] = self.cell_types[left]
            grid[sizex-1][j] = self.cell_types[right]

        #patch the corners
        grid[0][0] = self.cell_types[2]#wall
        grid[0][sizey-1] = self.cell_types[2]#wall
        grid[sizex-1][0] = self.cell_types[2]#wall
        grid[sizex-1][sizey-1] = self.cell_types[2]#wall

        return grid
    def generate_entrance(self, x1, y1, x2, y2): #may be redundant
        #check for errors and order helper
        if self.check_x1y1x2y2_in_range(x1, y1, x2, y2) == False:
            return
        x1, y1, x2, y2 = self.xy_order_helper(x1, y1, x2, y2)
        # Define and generate the Entrance
        grid = []
        sizex = x2-x1+1
        sizey = y2-y1+1

        #populate and pad with void values
        grid = self.generate_fill_grid(sizex, sizey, 'void')

        for i in range(0, sizex):
            for j in range(0, sizey):
                grid[i][j] = self.cell_types[3] #entrance
        return grid
    def generate_L_room(self, x1, y1, x2, y2, midx, midy, missing_q): #works
        #check for errors and order helper
        x1, y1, x2, y2 = self.xy_order_helper(x1, y1, x2, y2)
        if self.check_x1y1x2y2_in_range(x1, y1, x2, y2) == False:
            return
        if midx >= x2 or midx <= x1 or midy >= y2 or midy <= y1:
            return
        grid = []
        sizex = x2-x1+1
        sizey = y2-y1+1
        r_midx = midx -x1 #relative mid coords
        r_midy = midy - y1 #relative mid 
        #populate and pad with a normal rectangle
        grid = self.generate_rectangular_room(x1, y1, x2, y2)
        
        deletion_quardrant_to_coords = { #stored in x1 x2 y1 y2
            1:[r_midx+1, sizex, 0, r_midy],
            2:[0, r_midx, 0, r_midy],
            3:[0, r_midx, r_midy+1, sizey],
            4:[r_midx+1, sizex, r_midy+1, sizey]
        }

        dc = deletion_quardrant_to_coords[missing_q]

        #delete the quardrant
        for i in range(dc[0], dc[1]):
            for j in range(dc[2], dc[3]):
                grid[i][j] = self.cell_types[0]#void

        #draw horizontal wall
        if missing_q == 3 or missing_q == 2:
            for i in range(0, r_midx+1): 
                grid[i][r_midy] = self.cell_types[2]#wall
        else:
            for i in range(r_midx, sizex): 
                grid[i][r_midy] = self.cell_types[2]#wall

        #draw vertical wall
        if missing_q == 1 or missing_q == 2:
            for j in range(0, r_midy+1):
                grid[r_midx][j] = self.cell_types[2]#wall
        else:
            for j in range(r_midy, sizey):
                grid[r_midx][j] = self.cell_types[2]#wall

        return grid
                