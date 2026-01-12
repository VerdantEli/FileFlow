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

    def computeHash(self, file_path):
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
                    fileHash = self.computeHash(file)
                    if self.db.hash_exists(fileHash):
                        choice = self.duplicateWindow()
                        if choice == "keep":
                            self.db.inputLogs(currentTime, "Moving duplicate...", basename, file, "", fileHash)
                        elif choice == "delete":
                            os.remove(file)
                            self.db.inputLogs(currentTime, "Deleted duplicate", basename, file, "", fileHash)
                            continue
                        elif choice != "keep" and choice != "delete":
                            extension = os.path.splitext(file)[1]
                            basename = choice + extension
                            dst = os.path.join(self.path, folderName, basename)
                    else:
                        pass
                    shutil.move(file, dst)
                    self.db.inputLogs(currentTime,"Moved!",basename,file,dst,fileHash)

    def undo(self):
        logs = self.db.getLogs()
        for log in reversed(logs):
            timestamp, status, fileName, fromPath, toPath, fileHash = log[0], log[1], log[2], log[3], log[4], log[5]
            if status == "Moved!":
                if fromPath and toPath and os.path.exists(toPath):
                    shutil.move(toPath, fromPath)
                    self.db.inputLogs(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Undo Move", fileName, toPath, fromPath, fileHash)
            elif status == "Moving duplicate...":
                pass
            elif status == "Deleted duplicate":
                pass

    def duplicateWindow(self):
        root = tk.Toplevel()
        root.geometry("400x200")
        root.title("Duplicate Detected")
    
        label = tk.Label(root, text="Duplicate file detected. Choose an action:")
        label.pack(pady=10)
        
        choice = tk.StringVar(value="keep")
        
        def setChoice(value):
            choice.set(value)
            root.destroy()
        
        keepButton = tk.Button(root, text="Keep (skip)", command=lambda: setChoice("keep"))
        keepButton.pack(pady=5)
        
        renameButton = tk.Button(root, text="Rename", command=lambda: setChoice("rename"))
        renameButton.pack(padx=5)

        deleteButton = tk.Button(root, text="Delete", command=lambda: setChoice("delete"))
        deleteButton.pack(padx=5)

        root.grab_set()
        root.wait_window(root)

        if choice.get() == "rename":
            newName = self.renameWindow()
            choice.set(newName)
        
        return choice.get()
    
    def renameWindow(self):
        root = tk.Toplevel()
        root.geometry("300x100")
        root.title("Rename File")

        label = tk.Label(root, text="Enter new file name:")
        label.pack(pady=10)
        entry = tk.Entry(root)
        entry.pack(pady=5)
        newName = ""
        def submit():
            nonlocal newName
            newName = entry.get()
            root.destroy()
        submitButton = tk.Button(root, text="Submit", command=submit)
        submitButton.pack(pady=5)
        root.grab_set()
        root.wait_window(root)  
        return newName
