import tkinter as tk
from tkinter import simpledialog
from tkinter import font
import numpy
from helpers.color_helper import ColorHelper
from map_panel.layer import Layer


class MainPanel:
    def __init__(self, sizex, sizey, cellsize, Map_Folder_Path, initialize_panel):
        #path to the folder which the map is stored
        self.Map_Folder_Path = Map_Folder_Path

        #Map render
        self.height = sizey*cellsize
        self.width = sizex*cellsize
        self.cellsize = cellsize

        self.root = tk.Tk()
        self.root.title('Map Panel Canvas')
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg='#bbbbbb')
        self.font = font.Font(size=8, weight="bold")

        self.brushsize = 15
        self.minbrushsize = 15
        self.maxbrushsize = 50
        self.brushcolor = 'black'
        self.free_draw_toggle = False

        self.color_toggle = "Brush Color" #Background or Brush
        self.color_hex_input = "#000000"
        self.color_selection = [
            "Ink",
            "Crimson",
            "Copper",
            "Goldenrod",
            "Olive",
            "Lime",
            "Emerald",
            "Sea Green",
            "Teal",
            "Cyan",
            "Sky Blue",
            "Royal Blue",
            "Indigo",
            "Purple",
            "Magenta",
            "Ruby",
            "Coral"
        ]
        self.color_dict = {
            "Ink": "#333333",
            "Crimson": "#bf4040",
            "Copper": "#bf7040",
            "Goldenrod": "#bf9f40",
            "Olive": "#afbf40",
            "Lime": "#80bf40",
            "Emerald": "#50bf40",
            "Sea Green": "#40bf60",
            "Teal": "#40bf8f",
            "Cyan": "#40bfbf",
            "Sky Blue": "#408fbf",
            "Royal Blue": "#4060bf",
            "Indigo": "#5040bf",
            "Purple": "#7f40bf",
            "Magenta": "#af40bf",
            "Ruby": "#bf409f",
            "Coral": "#bf4070"
        }
        
        self.drawing_modes = ['FreeDraw', 'DrawLine', 'DrawRectangle', 'DrawCircle']
        self.current_mode = 'FreeDraw'
        self.previous_x = None
        self.previous_y = None

        self.layers = []
        self.active_layer_index = 0 #layer selected for drawing + adding objects
        self.max_layer = 0
        self.textbox_layer_name = ""

        #color picker
        self.color_picker_canvas = tk.Canvas(self.root, width=256, height=256)
        self.color_picker_colorS = "00000000" #string
        self.color_picker_colorA = [00,00,00,00] #Array - RGBA
        self.color_helper = ColorHelper()

        #png Convertor
        #self.PNGConverter = CanvasToPNGConverter
        self.Canvas_Save_File_Path = self.Map_Folder_Path

        #Cell Types
        self.cell_types_file_path = "C:\\Users\\user\\OneDrive\\Desktop\\Battle_Map_Creator_Python\\src\\assets\\csv_files\\cell_types.csv"
        self.cell_types_CSV = []
        self.extract_cell_types()

# Start
    def start(self):
        # initialize all
        self.update_all(True)
        self.create_new_layer("")
        self.update_all(True)

        self.canvas.bind('<Motion>', self.on_canvas_motion)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        self.canvas.bind('<Button-3>', self.on_canvas_click_3)
        self.canvas.bind('<Button-2>', self.on_canvas_click_2)
        self.canvas.bind('<MouseWheel>', self.on_canvas_scroll)
        self.canvas.bind('<Button-1>', self.on_canvas_click_1)

        self.root.mainloop()

# Rendering Grid - localise
    def draw_grid(self, grid, cellsize):
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                color = self.cell_type_to_color(grid[i][j])
                if color != None: #don't draw transparent values
                    self.canvas.create_rectangle(i*cellsize,j*cellsize,i*cellsize+cellsize,j*cellsize+cellsize,fill=color, outline=color)  
    def cell_type_to_color(self, cell_type):
        if cell_type == 'void':
            return None
        #match color to cell type
        for i in self.cell_types_CSV:
            color = self.color_helper.color_to_hex(i[2])
            if cell_type == i[1]:
                return color
        #no cell types matched, return None as color
        return None
    def draw_chunk_borders(self, chunksize, cellsize, color):
        # Calculate the dimensions of the chunk borders
        chunk_width = chunksize * cellsize
        chunk_height = chunksize * cellsize

        # Draw vertical chunk borders
        for x in range(0, self.width, chunk_width):
            self.canvas.create_line(x, 0, x, self.height, fill=color, width=2)

        # Draw horizontal chunk borders
        for y in range(0, self.height, chunk_height):
            self.canvas.create_line(0, y, self.width, y, fill=color, width=2)
# CSV Helper

    def csv_to_array(self, file_path, skipline):
        data = numpy.genfromtxt(file_path, delimiter=',', skip_header=skipline, dtype=str, encoding='utf-8')
        return data
    def extract_cell_types(self):
        temp = self.csv_to_array(self.cell_types_file_path, 1)

        #print(temp)
        # color hex code add the "#"
        for i in temp:
            i[2] = "#"+str(i[2])
        self.cell_types_CSV = temp
        return temp
    

# Pop up helper

    def pop_up_helper(self, message):
        # Create the main window
        root = tk.Tk()

        # Hide the main window
        root.withdraw()

        # Show a pop-up dialog for user input
        user_input = simpledialog.askstring("User Input", message)

        # Process the user input
        if user_input:
           print("User entered:", user_input)
        else:
            print("User canceled the input.")

        # Destroy the main window (optional)
        root.destroy()
        return user_input

# Update Methods # CAN NOW

    def update_all(self, initialize):
        print(initialize)
        if initialize == False:
            self.delete_widgets(0, 0, 100, 100)

        self.update_drawmode_window(initialize)
        self.update_layer_window(initialize)
        self.update_color_window(initialize)
        self.update_canvas(initialize)
        self.update_color_picker(initialize)
        self.update_convertToPNG_window(initialize)

    def update_drawmode_window(self, initialize): #column 0.1
        column_format = 0
        # Delete Current Widgets
        if initialize == False:
            print("Draw Mode Widgets Delete")
            self.delete_widgets(column_format, 0, column_format, len(self.drawing_modes)-1)

        # Create buttons for each drawing mode
        a = 0
        for mode in self.drawing_modes:
            button = tk.Button(self.root, text=mode, font=self.font, command=lambda m=mode: self.set_drawing_mode(m))
            button.grid(row=a, column=column_format, rowspan=1)
            a+=1

    def update_convertToPNG_window(self, initialize): #column 0.2
        column_format = 0
        # Delete Current Widgets
        if initialize == False:
            print("ConvertToPNG Widgets Delete")
            self.delete_widgets(column_format, 4, column_format, 4)
            

        # Create buttons for each drawing mode
        button = tk.Button(self.root, font=self.font, text="Save as PNG", command=lambda: self.save_canvas_as_png())
        button.grid(row=4, column=column_format, rowspan=1)

    def update_layer_window(self, initialize): # column 0.3
        column_format = 0
        # Delete Current Widgets
        if (initialize == False):
            print("Delete Layer Widgets",initialize, len(self.drawing_modes)+2, len(self.drawing_modes)+5+self.max_layer)#debug
            self.delete_widgets(column_format, len(self.drawing_modes)+2, column_format, len(self.drawing_modes)+5+self.max_layer)


        # Create a text box for layer name
        a = len(self.drawing_modes)+2
        layer_name_label = tk.Label(self.root, font=self.font, text="Layer Name:")
        layer_name_label.grid(row=a, column=column_format, rowspan=1)
        a+=1

        layer_name_entry = tk.Entry(self.root, text=self.textbox_layer_name, font=self.font)
        layer_name_entry.grid(row=a, column=column_format, rowspan=1)
        a+=1

        # Create buttons for adding layers and deleting layer

        create_new_layer = tk.Button(self.root, text="Create Layer", font=self.font, command=lambda: self.create_new_layer(layer_name_entry.get()))
        create_new_layer.grid(row=a, column=column_format, rowspan=1)
        a+=1

        delete_layer = tk.Button(self.root, text='Delete Layer', font=self.font, command=lambda: self.delete_active_layer())
        delete_layer.grid(row=a, column=column_format, rowspan=1)
        a+=1


        # Create buttons for activating and deactivating each layer
        for i, layer in enumerate(self.layers):
            button_text = '{}: {}'.format(layer.get_name(), 'Active' if layer.is_active else 'Inactive')
            if i == self.active_layer_index:
                color_temp = 'Cyan' if layer.is_active else 'purple'
            else:
                color_temp = 'white' if layer.is_active else 'red'

            button = tk.Button(self.root, bg = color_temp, font=self.font, text=button_text, command=lambda index=i: self.toggle_layer(index) or self.select_layer(index))
            button.grid(row=i+a, column=column_format, rowspan=1)

    def update_color_window(self, initialize): #column 2
        column_format = 2

        # Delete Current Widgets
        if (initialize == False):
            print("Delete Color Widgets")#debug
            self.delete_widgets(column_format, 0, column_format, 3)


        # Create color selection cycle toggle
        Color_Toggle_Button = tk.Button(self.root, text = self.color_toggle, font=self.font, bg='white', width=10, height=1, command=lambda: self.color_cylce_toggle())
        Color_Toggle_Button.grid(row=0, column=column_format, rowspan=1)

        # Create Erase and Hex Input
        a = 1
        erase = tk.Button(self.root, text = "Erase", bg="white", font=self.font, width=10, height=1, command=lambda: self.set_color("erase"))
        erase.grid(row=a, column=column_format, rowspan=1)
        a+=1

        # hex color input
        change_to_hexcolor = tk.Button(self.root, text = "Hex Color", font=self.font, bg=self.color_hex_input, width=10, height=1, command=lambda: self.set_color(color_hex_input.get()))
        change_to_hexcolor.grid(row=a, column=column_format, rowspan=1)
        a+=1
        
        color_hex_input = tk.Entry(self.root, text=self.color_hex_input, font=self.font, bg = "White")
        color_hex_input.grid(row=a, column=column_format, rowspan=1)

        # Create buttons for activating each color
        a+=1
        for c in self.color_selection:
            fgc = "#ffffff"
            button = tk.Button(self.root, text = c, bg=self.color_helper.color_to_hex(c), width=10, height=1, fg = fgc, font=self.font, command=lambda C=c: self.set_color(C))
            button.grid(row=a, column=column_format, rowspan=1)
            a+=1

    def update_canvas(self, initialize): #column 3
        column_format = 3
        self.canvas.grid(row=0, column=column_format, rowspan=20)

    def update_color_picker(self, initialize):#column 4
        column_format = 4
        self.color_picker_canvas.grid(row=0, column=column_format, rowspan=10)
        #for i in range (256):
        #    for j in range (256):
        #        temp_color_hex = ""
        #        temp_color_hex = "#" + format(i, '02x') + format(j, '02x') + "00"
        #        self.color_picker_canvas.create_rectangle(i, j, i, j, fill=temp_color_hex, outline=temp_color_hex )
        #self.PNGConverter.export_to_png(self, self.color_picker_canvas, "C:\\Users\\user\\OneDrive\\Desktop\\Battle_Map_Creator_Python\\docs\\Canvas_Save_File", "")

# localise update function

    def update_hex_button(self):
        self.delete_widgets(2, 2, 2, 2)
        column_format = 2
        change_to_hexcolor = tk.Button(self.root, text = "Hex Color", bg=self.color_hex_input, width=10, height=1, command=lambda: self.set_color(self.color_hex_input))
        change_to_hexcolor.grid(row=2, column=column_format, rowspan=1)

    def delete_widgets(self, x1, y1, x2, y2):
        for widget in self.root.winfo_children():
            info = widget.grid_info()
            row = info['row']
            column = info['column']
    
            # Specify the condition to delete widgets in specific grids
            if row >= y1 and row <= y2 and column >= x1 and column <= x2:
               widget.destroy()
        
# Color Window Methods

    def color_cylce_toggle(self):
        if self.color_toggle == "Background Color":
            self.color_toggle = "Brush Color"
        else:
            self.color_toggle = "Background Color"

        self.update_color_window(False)
        
    def set_drawing_mode(self, mode):
        self.current_mode = mode
        print('Current mode:', self.current_mode)


    def set_color(self, color): #can't handle transparent pixel value
        color = self.color_helper.color_to_hex(color) #convert everything is hex
        self.color_hex_input = color
        if color == None:
            color = "erase"

        self.color_hex_input = color   
        if self.color_toggle == "Background Color":
            print('Background Color:', color)
        else:
            print('Brush Color:', color)    


        self.layers[self.active_layer_index].toggle_erase(False)
        erase = False
        if color == "erase":
            erase = True

        if erase == True:
            self.color_hex_input = "#FFFFFF"
            if self.color_toggle == "Background Color":
                self.canvas.config(bg="white")
            else:
                self.layers[self.active_layer_index].toggle_erase(True)
        else:
            self.color_hex_input = color
            if self.color_toggle == "Background Color":
                self.canvas.config(bg=color)
            else:
                self.brushcolor = color

        self.update_hex_button()

# Layer Window Methods

    def create_new_layer(self, name): 
        # create, activate and select layer
        if name == "":
            layer_name = "Layer_{}".format(self.max_layer)
        else:
            layer_name = name

        #delete current widgits before updating #column formate = 0
        column_format = 0
        self.delete_widgets(column_format, len(self.drawing_modes)+2, column_format, len(self.drawing_modes)+5)

        layer = Layer(self.canvas, self.max_layer, layer_name)
        self.layers.append(layer)
        self.active_layer_index = self.max_layer
        self.max_layer += 1
        self.layers[self.active_layer_index].activate()

        print('Layer Created:', " ", self.layers[self.active_layer_index].get_name())
        print('Maximum Layer:', self.max_layer)

        print(len(self.layers), self.max_layer)

        # Update the layer management window
        self.update_layer_window(False)

    def delete_active_layer(self):
        if self.active_layer_index == None:
            return "No Layer Selected"

        print('Layer Deleted:', " ", self.layers[self.active_layer_index].get_name())

        #delete current widgits before updating #column formate = 0
        column_format = 0
        self.delete_widgets(column_format, len(self.drawing_modes)+2, column_format, len(self.drawing_modes)+5+self.max_layer)

        self.layers.pop(self.active_layer_index)
        self.max_layer += -1
        self.active_layer_index += -1

        if self.active_layer_index < 0:
            self.active_layer_index = None

        # Update the layer management window
        self.update_layer_window(False)

    def toggle_layer(self, index):
        a = None
        # toggle layer
        if self.layers[index].is_active:
            self.layers[index].deactivate()
            a = 'False'
        else:
            self.layers[index].activate()
            a = 'True'

        print('Layer Toggled:', a, " ", self.layers[index].get_name())
        # Update the layer management window
        self.update_layer_window(False)

    def select_layer(self, index):
        if index >= self.max_layer:
            return
        self.active_layer_index = index
        print('Layer Selected:', " ", self.layers[index].get_name())
        self.update_layer_window(False)

    def save_canvas_as_png(self): #png converter
        name = "Temp_Map"
        self.PNGConverter.export_to_png("Why", self.canvas, self.Canvas_Save_File_Path, name)

# Canvas Mouse Clicks Options

    def on_canvas_release(self, event):
        # Check for Chosen Active Layers
        if self.layers[self.active_layer_index] == None:
            print("No Layers Chosen")
            return

        self.free_draw_toggle = False

        if self.current_mode == 'Erase':
            self.canvas.delete('current')
        elif self.current_mode == 'DrawLine':
            self.layers[self.active_layer_index].draw_line(event, self.brushcolor, self.brushsize)
        elif self.current_mode == 'DrawRectangle':
            self.layers[self.active_layer_index].draw_rectangle(event, self.brushcolor, self.brushsize)
        elif self.current_mode == 'DrawCircle':
            self.layers[self.active_layer_index].draw_circle(event, self.brushcolor, self.brushsize)

    def on_canvas_scroll(self, event):
        scroll_direction = event.delta // abs(event.delta)
        self.brushsize += scroll_direction
        self.brushsize = max(self.minbrushsize, min(self.maxbrushsize, self.brushsize))
        print('Brush size:', self.brushsize)

    def on_canvas_click_1(self, event):
        # Check for Chosen Active Layers
        if self.layers[self.active_layer_index] == None:
            print("No Layers Chosen")
            return
        
        self.previous_x = event.x
        self.previous_y = event.y
        if self.current_mode == 'FreeDraw':
            self.free_draw_toggle = True
        self.layers[self.active_layer_index].start_drawing(event)

    def on_canvas_click_2(self, event): #debug temp
        self.update_layer_window(False)

    def on_canvas_click_3(self, event): #empty
        a = 1

    def on_canvas_motion(self, event):
        if self.current_mode == 'FreeDraw' and self.free_draw_toggle == True:
            self.layers[self.active_layer_index].free_draw(event, self.brushcolor, self.brushsize)

