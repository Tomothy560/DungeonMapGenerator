import colorsys
import re

class ColorHelper:
    def __init__(self):
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

    def get_hue_from_range(self, number, min_value, max_value):
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
    
    def color_to_hex(self,color_name): #localise function
        if color_name == None:
            return None
        color_name.lower()
        if color_name.startswith("#"):
            # If the color name is already a hexadecimal code, return it as is

            pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'

            # Check if the color code matches the pattern
            if re.match(pattern, color_name):
                return color_name
            else:
                return None
        if color_name in self.color_dict:
            return self.color_dict[color_name]
        else:
            return None

    def get_complementary_color(self, hex_code):
        # Remove the '#' symbol if present
        hex_code = hex_code.lstrip('#')

        # Convert the hex code to RGB values
        r, g, b = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

        # Calculate the complementary color
        comp_r = 255 - r
        comp_g = 255 - g
        comp_b = 255 - b

        # Convert the complementary color back to hex code
        comp_hex_code = '#{:02x}{:02x}{:02x}'.format(comp_r, comp_g, comp_b)
        
        return comp_hex_code

    def hex_to_rgb(self,hex_color):
        hex_color = str(hex_color)
        hex_color = hex_color.lstrip("#")  # Remove the "#" symbol if present
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    def hex_to_rgba(self,hex_color,A):
        hex_color = str(hex_color)
        hex_color = hex_color.lstrip("#")  # Remove the "#" symbol if present
        print(hex_color)
        if hex_color == None or hex_color == '':
            return (0,0,0,0)
        else:
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return rgb + (A,)
