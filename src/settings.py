import os
import tkinter as tk
from tkinter import filedialog,ttk,font, messagebox
from pathlib import Path
import configparser
import copy

SETTINGS_FILE = Path.home() / ".config" / "Fileflow" / "settings.ini"

class Settings:
    DEFAULT_EXTENSIONS = {
            "Images": ["jpg", "png", "jpeg"],
            "Documents": ["docx", "pptx", "xlsx", "pdf"],
            "Audio": ["mp3"],
            "Videos": ["mp4"],
            "Archives": ["zip", "rar"],
            "TextFiles": ["txt"],
            "Executables": ["exe"]
        }
    extensions = copy.deepcopy(DEFAULT_EXTENSIONS)

    def __init__(self, root):
        self.root = root
        self.loadSettings()

    def loadSettings(self):
        if os.path.exists(SETTINGS_FILE):
            config = configparser.ConfigParser()
            config.read(SETTINGS_FILE)
            if 'EXTENSIONS' in config:
                # ConfigParser converts keys to lowercase, so we need to preserve original case
                self.extensions = {k: v.split(', ') for k, v in config['EXTENSIONS'].items()}
                # Ensure keys match the DEFAULT_EXTENSIONS keys
                self.extensions = {self.DEFAULT_EXTENSIONS.get(k_lower, {}).__class__.__name__ == 'dict' and next((k for k in self.DEFAULT_EXTENSIONS if k.lower() == k_lower), k_lower): v for k_lower, v in self.extensions.items()}
                # Simpler approach: rebuild with correct case from DEFAULT_EXTENSIONS
                temp = {}
                for key_lower, value in self.extensions.items():
                    for key_orig in self.DEFAULT_EXTENSIONS.keys():
                        if key_orig.lower() == key_lower:
                            temp[key_orig] = value
                            break
                    else:
                        temp[key_lower] = value
                self.extensions = temp
            else:
                self.extensions = copy.deepcopy(self.DEFAULT_EXTENSIONS)
        else:
            self.extensions = copy.deepcopy(self.DEFAULT_EXTENSIONS)
        
        # Refresh UI labels if settings window is open
        if hasattr(self, 'entries'):
            for name, label in self.entries.items():
                label.config(text=", ".join(self.extensions.get(name, [])))

    def openSettings(self):
        settingsWindow = tk.Toplevel(self.root)
        settingsWindow.title("Settings")
        settingsWindow.geometry("800x600")
        settingsWindow.configure(bg="#222222")

        label = tk.Label(settingsWindow, text="File Extensions Configuration", bg="#222222", fg="white", font=self.guiFont(size=14, weight="bold"))
        label.pack(pady=20)

        # Create a scrollable frame for extensions
        canvas = tk.Canvas(settingsWindow, bg="#222222", highlightthickness=0)
        scrollbar = ttk.Scrollbar(settingsWindow, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#222222")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.entries = {}
        self.extension_frames = {}
        
        for extName, extList in self.extensions.items():
            frame = tk.Frame(scrollable_frame, bg="#333333", relief=tk.RIDGE, bd=1)
            frame.pack(pady=10, padx=10, fill=tk.X)
            self.extension_frames[extName] = frame

            # Extension name label
            extLabel = tk.Label(frame, text=f"{extName}:", bg="#333333", fg="#B8FFC7", font=self.guiFont(size=11, weight="bold"))
            extLabel.pack(side=tk.LEFT, padx=10, pady=8)

            # Label field for extensions (read-only)
            extDisplay = tk.Label(frame, text=", ".join(self.extensions.get(extName, extList)), bg="#222222", fg="white", width=35, justify=tk.LEFT, wraplength=300)
            extDisplay.pack(side=tk.LEFT, padx=5, pady=8)
            self.entries[extName] = extDisplay

            # Add button for this extension
            addButton = tk.Button(frame, text="Add", bg="#222222", fg="white", font=self.guiFont(size=10),
                                 command=lambda name=extName: self.addExtensionToList(name))
            addButton.pack(side=tk.LEFT, padx=5, pady=8)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Button frame at bottom
        buttonFrame = tk.Frame(settingsWindow, bg="#222222")
        buttonFrame.pack(side=tk.BOTTOM, pady=15)

        saveButton = tk.Button(buttonFrame, text="Save", bg="#222222", fg="white", font=self.textFont, command=self.saveSettings)
        saveButton.pack(side=tk.LEFT, padx=5)

        resetButton = tk.Button(buttonFrame, text="Reset to Default", bg="#222222", fg="white", font=self.textFont, command=self.resetExtensions)
        resetButton.pack(side=tk.LEFT, padx=5)

        closeButton = tk.Button(buttonFrame, text="Close", bg="#222222", fg="white", font=self.textFont, command=settingsWindow.destroy)
        closeButton.pack(side=tk.LEFT, padx=5)

    def addExtensionToList(self, extensionName):
        """Opens a dialog to add a new extension to the list"""
        addWindow = tk.Toplevel(self.root)
        addWindow.title(f"Add Extension to {extensionName}")
        addWindow.geometry("300x150")
        addWindow.configure(bg="#222222")

        label = tk.Label(addWindow, text=f"Add new extension to '{extensionName}':", bg="#222222", fg="white", font=self.textFont)
        label.pack(pady=10)

        entry = tk.Entry(addWindow, width=25)
        entry.pack(pady=10)
        entry.focus()

        def addToEntry():
            newExt = entry.get().strip()
            if newExt:
                if newExt not in self.extensions[extensionName]:
                    self.extensions[extensionName].append(newExt)
                    self.entries[extensionName].config(text=", ".join(self.extensions[extensionName]))
                self.saveSettings()
                addWindow.destroy()

        addButton = tk.Button(addWindow, text="Add", bg="#222222", fg="white", command=addToEntry)
        addButton.pack(pady=5)

        cancelButton = tk.Button(addWindow, text="Cancel", bg="#222222", fg="white", command=addWindow.destroy)
        cancelButton.pack(pady=5)

        addWindow.grab_set()
        addWindow.wait_window(addWindow)

    
    def saveSettings(self):
        # Create directory if it doesn't exist
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        config = configparser.ConfigParser()
        config['EXTENSIONS'] = {k: ', '.join(str(ext) for ext in v) for k, v in self.extensions.items()}
        with open(SETTINGS_FILE, 'w') as configfile:
            config.write(configfile)
            
    def resetExtensions(self):
        self.extensions = copy.deepcopy(self.DEFAULT_EXTENSIONS)
        if hasattr(self, 'entries'):
            for name, label in self.entries.items():
                label.config(text=", ".join(self.extensions[name]))
        
        self.saveSettings()

    def guiFont(self,size=12,weight="normal"):
        return font.Font(family="Helvetica", size=size, weight=weight)
    
    @property
    def textFont(self):
        return self.guiFont(size=12)