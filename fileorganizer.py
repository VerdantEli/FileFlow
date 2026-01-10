import os
import glob
import shutil
import datetime
from database import Database

class Organizer:
    def __init__(self,path):
        self.db=Database()
        self.db.connect()
        self.db.tableCreation()

        self.path = path
        self.extensions = {
            "jpg": "Images", "png": "Images", "jpeg": "Images", 
            "docx" : "Documents", "pptx" : "Documents", "xlsx" : "Documents", "pdf" : "Documents",
            "mp3" : "Audio",
            "mp4" : "Videos",
            "zip" : "Archives", "rar" : "Archives",
            "txt" : "TextFiles",
            "exe" : "Executables"
        }

    def organize(self):
        for extension, folderName in self.extensions.items():
            files = glob.glob(os.path.join(self.path, f"*.{extension}"))
            if not os.path.isdir(os.path.join(self.path, folderName)) and files:
                os.mkdir(os.path.join(self.path, folderName))

            for file in files:
                currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                basename = os.path.basename(file)
                dst = os.path.join(self.path, folderName, basename)
                shutil.move(file, dst)
                self.db.inputLogs(currentTime,"Moved!",basename,file,dst)