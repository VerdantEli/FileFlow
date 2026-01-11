import os
import glob
import shutil
import datetime
from src.database import Database

class Organizer:
    def __init__(self,path,db):
        self.db=db
        self.path = path
        self.extensions = {
            "Images": ["jpg", "png", "jpeg"],
            "Documents": ["docx", "pptx", "xlsx", "pdf"],
            "Audio": ["mp3"],
            "Videos": ["mp4"],
            "Archives": ["zip", "rar"],
            "TextFiles": ["txt"],
            "Executables": ["exe"]
        }

    def organize(self):
        for folderName, extensions in self.extensions.items():
            for ext in extensions:
                files = glob.glob(os.path.join(self.path, f"*.{ext}"))
                if not os.path.isdir(os.path.join(self.path, folderName)) and files:
                    os.mkdir(os.path.join(self.path, folderName))

                for file in files:
                    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    basename = os.path.basename(file)
                    dst = os.path.join(self.path, folderName, basename)
                    shutil.move(file, dst)
                    self.db.inputLogs(currentTime,"Moved!",basename,file,dst)