import os
import glob
import shutil
import datetime
import hashlib
import tkinter as tk
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

    def compute_hash(self, file_path):
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

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
                    file_hash = self.compute_hash(file)
                    if self.db.hash_exists(file_hash):
                        choice = self.duplicateWindow()
                        if choice == "keep":
                            self.db.inputLogs(currentTime, "Moving duplicate...", basename, file, "", file_hash)
                        elif choice == "delete":
                            os.remove(file)
                            self.db.inputLogs(currentTime, "Deleted duplicate", basename, file, "", file_hash)
                            continue
                        else: #rename
                            pass
                    shutil.move(file, dst)
                    self.db.inputLogs(currentTime,"Moved!",basename,file,dst,file_hash)

    def duplicateWindow(self):
        root = tk.Toplevel()
        root.geometry("1000x800")
        root.title("Duplicate Detected")
        
        label = tk.Label(root, text="Duplicate file detected. Choose an action:")
        label.pack(pady=10)
        
        # Variables to track user choice
        choice = tk.StringVar(value="keep")  # Default to keep
        
        def set_choice(c):
            choice.set(c)
            root.destroy()
        
        keep_btn = tk.Button(root, text="Keep (skip)", command=lambda: set_choice("keep"))
        keep_btn.pack(pady=5)
        
        rename_btn = tk.Button(root, text="Rename", command=lambda: set_choice("rename"))
        rename_btn.pack(pady=5)
        
        delete_btn = tk.Button(root, text="Delete", command=lambda: set_choice("delete"))
        delete_btn.pack(pady=5)
        
        # Make it modal
        root.grab_set()
        root.wait_window(root)
        
        return choice.get()