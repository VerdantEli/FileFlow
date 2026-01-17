import os
import glob
import shutil
import datetime
import hashlib
import tkinter as tk
import time
import sqlite3
from src.database import Database

class Organizer:
    def __init__(self,path,db,status = None, duplicateCallback=None,progressCallback=None):
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
        self.status=status
        self.duplicateCallback=duplicateCallback
        self.progressCallback=progressCallback
        

    def organize(self):
        self.connection = sqlite3.connect(self.db.path)
        cursor = self.connection.cursor()

        allFiles = []
        for folderName, extensions in self.extensions.items():
            for ext in extensions:
                files = glob.glob(os.path.join(self.path, f"*.{ext}"))
                for file in files:
                    allFiles.append(file)

        totalFiles = len(allFiles)
        processedFiles = 0
        
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
                    cursor.execute("SELECT COUNT(*) FROM hashes WHERE fileHash=?", (fileHash,))
                    exists = cursor.fetchone()[0] > 0 #if hash exists in db

                    # Move file if not duplicate
                    if not exists:
                        cursor.execute("INSERT OR IGNORE INTO hashes VALUES (?)", (fileHash,))
                        shutil.move(file, dst)
                        cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?,?)",(currentTime,"Moved!",basename,file,dst,fileHash))
                        self.connection.commit()
                    else:
                        # Handle duplicates
                        choice = self.duplicateCallback(file)

                        if choice == "keep":
                            shutil.move(file, dst)
                            cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?,?)",(currentTime,"Moving duplicate...",basename,file,dst,fileHash))
                            self.connection.commit()
                        elif choice == "delete":
                            os.remove(file)
                            cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?,?)",(currentTime,"Deleted duplicate",basename,file,"",fileHash))
                            self.connection.commit()
                        else: # rename
                            extension = os.path.splitext(file)[1]
                            basename = choice + extension
                            dst = os.path.join(self.path, folderName, basename)

                            shutil.move(file, dst)
                            cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?,?)",(currentTime,"Renamed duplicate",basename,file,dst,fileHash))                        
                    processedFiles += 1
                    if self.progressCallback:
                        self.progressCallback(processedFiles, totalFiles)
                    self.connection.commit()
                    self.giveStatus("Yes")
                    time.sleep(0.3)

    def undo(self):
        self.connection = sqlite3.connect(self.db.path)
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
        logs = cursor.fetchall()

        allFiles = len(logs)
        processedFiles = 0

        for log in reversed(logs):
            timestamp, status, fileName, fromPath, toPath, fileHash = log[0], log[1], log[2], log[3], log[4], log[5]
            if status == "Moved!":
                if fromPath and toPath and os.path.exists(toPath):
                    shutil.move(toPath, fromPath)
                    cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?,?)",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Undo Move", fileName, toPath, fromPath, fileHash))
                    self.connection.commit()
            elif status == "Moving duplicate...":
                if fromPath and toPath and os.path.exists(toPath):
                    shutil.move(toPath, fromPath)
                    cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?,?)",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Undo Move", fileName, toPath, fromPath, fileHash))
                    self.connection.commit()
            elif status == "Renamed duplicate":
                if fromPath and toPath and os.path.exists(toPath):
                    shutil.move(toPath, fromPath)
                    cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?,?)",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"Undo Rename", fileName, toPath, fromPath, fileHash))
                    self.connection.commit()
            elif status == "Deleted duplicate":
                pass

            cursor.execute("DELETE FROM hashes WHERE fileHash=?", (fileHash,))
            self.connection.commit()
            processedFiles += 1
            if self.progressCallback:
                self.progressCallback(processedFiles, allFiles)
        
            if self.status:
                self.status("Yes")
            time.sleep(0.3)

    # Helper to give status updates
    def giveStatus(self, message):
        if self.status:
            self.status(message)


    def computeHash(self, file_path):
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
