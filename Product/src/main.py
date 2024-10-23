from front_end.main_front_end import MainFrontEnd
from helpers.file_write_helper import FileWriteHelper
import os

fwh = FileWriteHelper()
file_paths = fwh.json_to_dict("assets\\json_files\\file_paths.json")

file_paths["application_path"] = os.path.abspath('main.py').replace('/', '//')[:-12]
fwh.dict_to_json("assets\\json_files\\file_paths.json", file_paths)

main_front_end = MainFrontEnd(file_paths)
main_front_end.start()

    

