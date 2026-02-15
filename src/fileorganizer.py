import os
import glob
import shutil
import datetime
import hashlib
import tkinter as tk
from tkinter import messagebox
import time
import sqlite3
import configparser
from pathlib import Path
from .database import Database

SETTINGS_FILE = Path.home() / ".config" / "Fileflow" / "settings.ini"

def loadExtensionsFromSettings():
    """Load extensions from settings.ini"""
    DEFAULT_EXTENSIONS = {
        "Pictures": ["jpg", "png", "jpeg"],
        "Documents": ["docx", "pptx", "xlsx", "pdf"],
        "Audio": ["mp3"],
        "Videos": ["mp4"],
        "Archives": ["zip", "rar"],
        "TextFiles": ["txt"],
        "Executables": ["exe"]
    }
    
    if os.path.exists(SETTINGS_FILE):
        config = configparser.ConfigParser()
        config.read(SETTINGS_FILE)
        if 'EXTENSIONS' in config:
            extensions = {k: v.split(', ') for k, v in config['EXTENSIONS'].items()}
            # Map lowercase keys to original case
            temp = {}
            for key_lower, value in extensions.items():
                for key_orig in DEFAULT_EXTENSIONS.keys():
                    if key_orig.lower() == key_lower:
                        temp[key_orig] = value
                        break
                else:
                    temp[key_lower] = value
            return temp
    
    return DEFAULT_EXTENSIONS

class Organizer:
    def __init__(self,path,db,status = None, duplicateCallback=None,progressCallback=None, extensions=None):
        self.db=db
        self.path = path
        self.extensions = extensions if extensions is not None else loadExtensionsFromSettings()
        self.status=status
        self.duplicateCallback=duplicateCallback
        self.progressCallback=progressCallback
    
    def isValidPath(self):
        """Check if path on C: drive is one of the allowed directories in the correct location"""
        drive = os.path.splitdrive(self.path)[0].upper()
        
        # If not on C: drive, allow it
        if drive != "C:":
            return True
        
        # If on C: drive, check if it matches C:\Users\{username}\{allowed_directory}
        allowed_dirs = {"DESKTOP", "DOWNLOADS", "DOCUMENTS", "PICTURES", "MUSIC", "VIDEOS"}
        
        # Normalize path
        normalized_path = os.path.normpath(self.path).upper()
        
        # Get the path parts
        path_parts = normalized_path.split("\\")
        
        # Should be at least: C:, Users, {username}, {directory}
        if len(path_parts) < 4:
            return False
        
        # Check if it follows C:\Users\{username}\{directory}
        if path_parts[0] != "C:" or path_parts[1] != "USERS":
            return False
        
        # Check if the directory is one of the allowed ones
        directory = path_parts[3].upper()
        return directory in allowed_dirs
        

    def organize(self):
        # Validate path restrictions on C: drive
        if not self.isValidPath():
            messagebox.showerror("Invalid Directory", "Directory on C: drive must be one of: Desktop, Downloads, Documents, Pictures, Music, or Videos")
            return
        
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
        
        if totalFiles > 0:
            cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?,?)",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Starting Move...", "", "", "", ""))
            self.connection.commit()
            self.giveStatus("Yes")
            time.sleep(1)


        for folderName, extensions in self.extensions.items():
            for ext in extensions:
                files = glob.glob(os.path.join(self.path, f"*.{ext}"))
                if not os.path.isdir(os.path.join(Path.home(), folderName)) and files:
                    os.mkdir(os.path.join(Path.home(), folderName))

                for file in files:
                    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    basename = os.path.basename(file)
                    dst = os.path.join(Path.home(), folderName, basename)
                    fileHash = self.computeHash(file)

                    #if hash exists in db
                    cursor.execute("SELECT COUNT(*) FROM hashes WHERE fileHash=?", (fileHash,))
                    exists = cursor.fetchone()[0] > 0 

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
                    time.sleep(0.2)

    def undoCounter(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
        logs = cursor.fetchall()
        
        count = 0
        for log in logs:
            status = log[1]
            if status == "Starting Move...":
                break
            if status in ("Moved!", "Moving duplicate...", "Renamed duplicate", "Deleted duplicate"):
                count += 1
        return count

    def undo(self):
        self.connection = sqlite3.connect(self.db.path)
        cursor = self.connection.cursor()
        
        cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
        logs = cursor.fetchall()

        allFiles = self.undoCounter()
        processedFiles = 0

        if allFiles >= 0:
            cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?,?)",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Starting Undo...", "", "", "", ""))
            self.connection.commit()
            self.giveStatus("Yes")
            time.sleep(1)

        for log in logs:
            timestamp, status, fileName, fromPath, toPath, fileHash = log[0], log[1], log[2], log[3], log[4], log[5]
            
            if status == "Starting Move...":
                break
            
            if status == "Moved!":
                if fromPath and toPath and os.path.exists(toPath):
                    shutil.move(toPath, fromPath)
                    cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?,?)",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Undo Move", fileName, toPath, fromPath, fileHash))
                    cursor.execute("DELETE FROM hashes WHERE fileHash=?", (fileHash,))
                    self.connection.commit()
            elif status == "Moving duplicate...":
                if fromPath and toPath and os.path.exists(toPath):
                    shutil.move(toPath, fromPath)
                    cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?,?)",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Undo Move", fileName, toPath, fromPath, fileHash))
                    cursor.execute("DELETE FROM hashes WHERE fileHash=?", (fileHash,))
                    self.connection.commit()
            elif status == "Renamed duplicate":
                if fromPath and toPath and os.path.exists(toPath):
                    shutil.move(toPath, fromPath)
                    cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?,?)",(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"Undo Rename", fileName, toPath, fromPath, fileHash))
                    cursor.execute("DELETE FROM hashes WHERE fileHash=?", (fileHash,))
                    self.connection.commit()
            
            processedFiles += 1
            if self.progressCallback:
                self.progressCallback(processedFiles, allFiles)
            if self.status:
                self.status("Yes")
            time.sleep(0.3)

    def giveStatus(self, message):
        if self.status:
            self.status(message)

    def computeHash(self, file_path):
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    