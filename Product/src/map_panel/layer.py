import tkinter as tk
from tkinter import Tk, Canvas
from PIL import Image, ImageTk
import math


class Layer:
    def __init__(self, canvas, index, name):
        self.canvas = canvas
        self.id = canvas.create_rectangle(0, 0, canvas.winfo_width(), canvas.winfo_height(), fill='', outline='')
        self.is_active = False #visibility
        self.opacity = 1 #0.00 - 1.00
        self.index = index
        self.previous_x = 0
        self.previous_y = 0
        self.erase_toggle = False

        self.layer_name = name # layer Name
        self.layer_type = "" # Not finish - Object or Annotation Canvas

    def get_index(self):
        return self.index
    def activate(self):
        self.is_active = True
    def deactivate(self):
        self.is_active = False
    def get_name(self):
        return self.layer_name
    def toggle_erase(self, TF):
        self.erase_toggle = TF

    def add_opacity(self, amount):
        if self.opacity + amount > 1:
            return 'Error, value > 1'
        elif self.opacity + amount < 0:
            return 'Error, value < 0'
        else:
            self.opacity += amount
    def set_opacity(self, amount):
        if amount > 1:
            return 'Error, value > 1'
        elif amount < 0:
            return 'Error, value < 0'
        else:
            self.opacity = amount

#erase checklist: Draw circle

    def erase_line(self, event, size):
        x1, y1 = self.previous_x, self.previous_y
        x2, y2 = event.x, event.y

        # Calculate the difference between the start and end points
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        # Calculate the increments for each axis
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        # Initialize the error and current coordinates
        error = dx - dy
        x = x1
        y = y1

        # Iterate over the line and delete items within the specified thickness
        while x != x2 or y != y2:
            # Find the items within the rectangular area based on the thickness
            items = self.canvas.find_overlapping(x - size, y - size, x + size, y + size)

            # Delete the items
            for item in items:
                self.canvas.delete(item)

            # Calculate the next coordinates using the Bresenham's algorithm
            error2 = 2 * error
            if error2 > -dy:
                error -= dy
                x += sx
            if error2 < dx:
                error += dx
                y += sy

    def draw_line(self, event, color, size):
        x = event.x
        y = event.y

        
        if self.previous_x is not None and self.previous_y is not None:
            if self.erase_toggle: #erase
                self.erase_line(event, size)
            else: #draw
                self.canvas.create_line(self.previous_x, self.previous_y, x, y, fill=color, width=size)

        self.stop_drawing()
    def draw_rectangle(self, event, color, size):
        x = event.x
        y = event.y


        if self.previous_x is not None and self.previous_y is not None:
            if self.erase_toggle: #erase
                # Find the items within the given rectangular area
                items = self.canvas.find_overlapping(x, y, self.previous_x, self.previous_y)

                # Delete the items
                for item in items:
                    self.canvas.delete(item)
            else: #draw
                self.canvas.create_rectangle(self.previous_x, self.previous_y, x, y, outline=color, width=size)

        self.stop_drawing()
    def draw_circle(self, event, color, size):
        x = event.x
        y = event.y

        if self.previous_x is not None and self.previous_y is not None:
            if self.erase_toggle: #erase
                asd
            else: #draw
                self.canvas.create_oval(self.previous_x, self.previous_y, x, y, outline=color , width=size)

        self.stop_drawing()
    def free_draw(self, event, color, size):
        x = event.x
        y = event.y

        if self.previous_x is not None and self.previous_y is not None:
            if self.erase_toggle: #erase
                # Find the items within the given rectangular area
                items = self.canvas.find_overlapping(x, y, self.previous_x, self.previous_y)

                # Delete the items
                for item in items:
                    self.canvas.delete(item)    
            else: #draw
                self.canvas.create_oval(self.previous_x, self.previous_y, x, y, fill=color, width=size , outline=color)

        self.previous_x = x
        self.previous_y = y

    def start_drawing(self, event):
        # Initialize the previous coordinates when starting to draw
        self.previous_x = event.x
        self.previous_y = event.y
    def stop_drawing(self):
        # Reset the previous coordinates when stopping drawing
        self.previous_x = None
        self.previous_y = None

    def erase(self, event, size):
        x = event.x
        y = event.y

        # Find the items within a given rectangular area
        items = self.canvas.find_overlapping(x - size, y - size, x + size, y + size)

        # Delete the items
        for item in items:
            self.canvas.delete(item)
