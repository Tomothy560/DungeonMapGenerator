import math
import random
class Structure: #
    def __init__(self, x1, y1, x2, y2, structure_type, id):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.id_value = id
        self.structure_type = structure_type
        self.grid = []#actual grid with cell types, localise
    
    # basic functions
    def get_structure_properties_as_string(self):
        coordinates = str(self.x1) + "," + str(self.y1) + "," + str(self.x2) + "," + str(self.y2) + "," + self.id_value
        return_text = coordinates+"\n"+self.structure_type
        return return_text
    
    def get_structure_properties_as_dict(self):
        return_dict = {
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "id_value": self.id_value,
            "structure_type": self.structure_type,
        }

        return return_dict
    
    def generate_layout(self):
        self.grid = []

    # helper functions
    def generate_fill_grid(self, sizex, sizey, celltype):
        grid = []
        for _ in range(sizex):
            row = [celltype] * sizey
            grid.append(row)
        return grid

class StructureCorridor(Structure):
    def __init__(self, x1, y1, x2, y2, id,orientation):
        super().__init__(x1, y1, x2, y2, 'failed_corridor',id)
        self.orientation = orientation #horizontal or vertical
        self.grid = self.generate_layout()
    
    def get_structure_properties_as_string(self):
        coordinates = str(self.x1) + "," + str(self.y1) + "," + str(self.x2) + "," + str(self.y2)+ "," + self.id_value
        return_text = coordinates+"\n"+self.structure_type # padrent variables
        return_text = return_text + "\n"+self.orientation # child variables
        return return_text
    
    def get_structure_properties_as_dict(self):
        return_dict = {
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "id_value": self.id_value,
            "structure_type": self.structure_type,
            "orientation": self.orientation
        }

        return return_dict
    
    def generate_layout(self):
        grid = []
        sizex = abs(self.x2-self.x1+1)
        sizey = abs(self.y2-self.y1+1)

        #populate and pad with void values
        grid = self.generate_fill_grid(sizex, sizey, 'void')

        #define middle path
        for i in range(0, sizex):
            for j in range(0, sizey):
                grid[i][j] = 'path'#path

        #define walls

        if self.orientation == "horizontal":
            top, bottom = 'wall','wall' #wall
            left, right = 'path', 'path' #path
        elif self.orientation == "vertical":
            top, bottom = 'path', 'path' #path
            left, right = 'wall','wall' #wall
        
        # define walls
        for i in range(0, sizex): 
            grid[i][0] = top
            grid[i][sizey-1] = bottom
            
        for j in range(0, sizey):
            grid[0][j] = left
            grid[sizex-1][j] = right

        #patch the corners
        grid[0][0] = 'wall'
        grid[0][sizey-1] = 'wall'
        grid[sizex-1][0] = 'wall'
        grid[sizex-1][sizey-1] = 'wall'

        return grid

class StructureMaze(Structure):
    def __init__(self, x1, y1, x2, y2,id):
        super().__init__(x1, y1, x2, y2, 'maze',id)
        self.grid = self.generate_layout()
        
    def generate_layout(self):

        def generate_maze_helper(maze_height, maze_width):
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

        # reoganize and make function flexible
        maze_width = abs(self.x1-self.x2+1)
        maze_height = abs(self.y1-self.y2+1)
        # make sure its NOT a multiple of 2
        if maze_width%2 == 0:
            self.x2 += -1
            maze_width += -1
        if maze_height%2 == 0:
            self.y2 += -1
            maze_height += -1
        
        # Generate random paths using a turtle
        grid = generate_maze_helper(maze_width, maze_height)
        for i in range(maze_width):
            for j in range(maze_height):
                if grid[i][j] == 0:
                    grid[i][j] = "path"
                else:
                    grid[i][j] = "wall"
        return grid
    #no need overrisde get structure properties

class StructureLRoom(Structure):
    def __init__(self, x1, y1, x2, y2, id, midx, midy, missing_q):
        super().__init__(x1, y1, x2, y2, 'L_room', id)
        self.midx = midx
        self.midy = midy
        self.missing_q = missing_q
        self.grid = self.generate_layout()
    
    def get_structure_properties_as_string(self):
        coordinates = str(self.x1) + "," + str(self.y1) + "," + str(self.x2) + "," + str(self.y2)+ "," + self.id_value
        return_text = coordinates+"\n"+self.structure_type # padrent variables
        return_text = return_text + "\n"+str(self.midx) + "\n"+str(self.midy) + "\n"+str(self.missing_q) # child variables
        return return_text
        
    def get_structure_properties_as_dict(self):
        return_dict = {
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "id_value": self.id_value,
            "structure_type": self.structure_type,
            "midx": self.midx,
            "midy": self.midy,
            "missing_q": self.missing_q
        }
        return return_dict
    
    def generate_layout(self):
        grid = []
        sizex = self.x2-self.x1+1
        sizey = self.y2-self.y1+1

        r_midx = self.midx - self.x1 #relative mid coords
        r_midy = self.midy - self.y1 #relative mid

        #populate and pad with a normal rectangle
        grid = [["path" for _ in range(sizey)] for _ in range(sizex)]

        for i in range(0, sizex): 
            grid[i][0] = "wall"#wall
            grid[i][sizey-1] = "wall"#wall
                
        for j in range(0, sizey):
            grid[0][j] = "wall"#wall
            grid[sizex-1][j] = "wall"#wall
        
        deletion_quardrant_to_coords = { #stored in x1 x2 y1 y2
            1:[r_midx+1, sizex, 0, r_midy],
            2:[0, r_midx, 0, r_midy],
            3:[0, r_midx, r_midy+1, sizey],
            4:[r_midx+1, sizex, r_midy+1, sizey]
        }

        dc = deletion_quardrant_to_coords[self.missing_q]

        #delete the quardrant
        for i in range(dc[0], dc[1]):
            for j in range(dc[2], dc[3]):
                grid[i][j] = 'void'

        #draw horizontal wall
        if self.missing_q == 3 or self.missing_q == 2:
            for i in range(0, r_midx+1): 
                grid[i][r_midy] = "wall"#wall
        else:
            for i in range(r_midx, sizex): 
                grid[i][r_midy] = "wall"#wall

        #draw vertical wall
        if self.missing_q == 1 or self.missing_q == 2:
            for j in range(0, r_midy+1):
                grid[r_midx][j] = "wall"#wall
        else:
            for j in range(r_midy, sizey):
                grid[r_midx][j] = "wall"#wall

        return grid    

class StructureRectangularRoom(Structure):
    def __init__(self, x1, y1, x2, y2, id, nesw):
        super().__init__(x1, y1, x2, y2, 'rectangular_room', id)
        self.NESW = nesw # arrays of [0,0,0,0] 1 and 0 as boolean
        self.grid = self.generate_layout()
    
    def get_structure_properties_as_string(self):
        coordinates = str(self.x1) + "," + str(self.y1) + "," + str(self.x2) + "," + str(self.y2)+ "," + self.id_value
        return_text = coordinates+"\n"+self.structure_type # padrent variables
        return_text = return_text + "\n"+str(self.NESW) # child variables
        return return_text
        
    def get_structure_properties_as_dict(self):
        return_dict = {
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "id_value": self.id_value,
            "structure_type": self.structure_type,
            "NESW": self.NESW
        }
        return return_dict
    
    def generate_layout(self):
        grid = []
        cell_types = ["","path","wall"]
        sizex = abs(self.x2-self.x1+1)
        sizey = abs(self.y2-self.y1+1)
        #populate and pad with void values
        grid = self.generate_fill_grid(sizex, sizey, 'void')

        #define middle path
        for i in range(0, sizex):
            for j in range(0, sizey):
                grid[i][j] = 'path'#path

        #define walls - 1 path | 2 walls

        top = self.NESW[0]+1
        right = self.NESW[1]+1
        bottom = self.NESW[2]+1
        left = self.NESW[3]+1
        
        # define walls
        for i in range(0, sizex): 
            grid[i][0] = cell_types[top]
            grid[i][sizey-1] = cell_types[bottom]
            
        for j in range(0, sizey):
            grid[0][j] = cell_types[left]
            grid[sizex-1][j] = cell_types[right]

        #patch the corners
        grid[0][0] = cell_types[2]#wall
        grid[0][sizey-1] = cell_types[2]#wall
        grid[sizex-1][0] = cell_types[2]#wall
        grid[sizex-1][sizey-1] = cell_types[2]#wall

        return grid

class StructureCircularRoom(Structure):
    def __init__(self, x1, y1, x2, y2, id, perfect_circle):
        super().__init__(x1, y1, x2, y2, 'circular_room', id)
        self.perfect_circle = perfect_circle #boolean
        self.grid = self.generate_layout()
    
    def generate_layout(self): #doesnt work yet
        def check_neighboring_cell_contain(x1, y1, grid, cell_type):
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
            cell_array = [[nx, ny],[ex, ey], [sx, sy],[wx, wy],[ex, ny],[wx, ny], [ex, sy],[wx, sy]]
            for a in cell_array:
                if grid[a[0]][a[1]] == cell_type:
                    return True       
        if self.perfect_circle == True:
            difference = abs(self.x2-self.x1 - self.y2+self.y1)
            if self.x2-self.x1 > self.y2-self.y1: #Square the circle
                self.x1 += math.floor(difference/2)
                self.x2 -= math.ceil(difference/2)
            else:
                self.y1 += math.floor(difference/2)
                self.y2 -= math.ceil(difference/2)

            origin = [(self.x2+self.x1)/2-self.x1,(self.y2+self.y1)/2-self.y1]
            diameter = min([self.x2-self.x1+1,self.y2-self.y1+1])
            grid = [["void" for _ in range(diameter)] for _ in range(diameter)]
            for i in range(diameter):
                for j in range(diameter):
                    if math.ceil((i-origin[0])**2 + (j-origin[1])**2)**0.5+1 < diameter/2:
                        grid[i][j] = "path"
            sizex, sizey = diameter, diameter
            def debug():
                print(self.x1,self.y1,self.x2,self.y2,diameter,origin)
                grid[0][0] = "wall"
                grid[diameter-1][0] = "wall"
                grid[0][diameter-1] = "wall"
                grid[diameter-1][diameter-1] = "wall"
                grid[math.floor(origin[0])][math.floor(origin[1])] = "wall"
                grid[math.ceil(origin[0])][math.ceil(origin[1])] = "wall"

            #debug()
        else: #https://www.desmos.com/calculator/fowhgw03ff ovals
            # https://www.desmos.com/calculator/z5b1g7bd32 
            sizex = self.x2-self.x1+1
            sizey = self.y2-self.y1+1

            #populate and pad with a normal rectangle
            grid = [["void" for _ in range(sizey)] for _ in range(sizex)]
            a= sizex-1-1
            b= sizey-1-1
            for i in range(0,sizex):
                for j in range(0,sizey):
                    if ((2*math.ceil(i)-a-2)/(a-1))**2+((2*math.ceil(j)-b-2)/(b-1))**2 <= 1:
                        grid[i][j] = "path"

        for i in range(0,sizex):
            for j in range(0,sizey):
                if check_neighboring_cell_contain(i,j, grid, "path") and grid[i][j] == "void":
                    grid[i][j] = "wall"

        return grid

    def get_structure_properties_as_string(self):
        coordinates = str(self.x1) + "," + str(self.y1) + "," + str(self.x2) + "," + str(self.y2)+ "," + self.id_value
        return_text = coordinates+"\n"+self.structure_type # padrent variables
        return_text = return_text + "\n"+str(self.perfect_circle) # child variables
        return return_text
        
    def get_structure_properties_as_dict(self):
        return_dict = {
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "id_value": self.id_value,
            "structure_type": self.structure_type,
            "perfect_circle": self.perfect_circle
        }
        return return_dict
    
   