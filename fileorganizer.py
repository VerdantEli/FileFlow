import os
import glob
import shutil
from gui import *

class Organizer:
    def __init__(self,path):
        self.path = path
        self.extensions = {
            "jpg": "Images", "png": "Images", "jpeg": "Images", 
            "docx" : "Documents", "pptx" : "Documents", "xlsx" : "Documents", "pdf" : "Documents",
            "mp3" : "Audio",
            "mp4" : "Videos"
        }

    def organize(self):
        for extension, folderName in self.extensions.items():
            files = glob.glob(os.path.join(self.path, f"*.{extension}"))
            if not os.path.isdir(os.path.join(self.path, folderName)) and files:
                os.mkdir(os.path.join(self.path, folderName))

            for file in files:
                basename = os.path.basename(file)
                dst = os.path.join(self.path, folderName, basename)
                shutil.move(file, dst)