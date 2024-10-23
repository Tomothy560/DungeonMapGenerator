
class Object:
    def __init__(self, image_file_path, id_value) -> None:
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.image_file_path = image_file_path
        self.id_value = id_value #defines the object type and object count.
    
    def return_as_dictionary(self):
        dictionary = {
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "id_value": self.id_value,
            "image_file_path": self.image_file_path,
        }
        return dictionary