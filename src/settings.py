import os
import tkinter as tk
from tkinter import font,ttk,font, messagebox
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

        self.headerFont = font.Font(family= "Century Gothic",size=22)
        self.textFont = font.Font(family="Century Gothic",size=14)
        
        # Store reference to settings window for updates
        self.settingsWindow = settingsWindow

        label = tk.Label(settingsWindow, text="File Extensions Configuration", bg="#222222", fg="white", font=self.headerFont)
        label.pack(pady=20, anchor="center")

        # Create a frame to hold canvas and scrollbar together
        canvasFrame = tk.Frame(settingsWindow, bg="#222222")
        canvasFrame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create a scrollable frame for extensions
        canvas = tk.Canvas(canvasFrame, bg="#222222", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvasFrame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#222222")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((400, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Store references for refresh
        self.canvas = canvas
        self.scrollable_frame = scrollable_frame

        self.entries = {}
        self.extension_frames = {}
        
        self.populateExtensionsList()

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add Folder button above bottom buttons
        addFolderButton = tk.Button(settingsWindow, text="Add New Folder", bg="#222222", fg="white", font=self.textFont, command=self.addNewFolder)
        addFolderButton.pack(side=tk.TOP, pady=10)

        # Button frame at bottom
        buttonFrame = tk.Frame(settingsWindow, bg="#222222")
        buttonFrame.pack(side=tk.BOTTOM, pady=15, anchor="center")

        saveButton = tk.Button(buttonFrame, text="Save", bg="#222222", fg="white", font=self.textFont, command=self.saveSettings)
        saveButton.pack(side=tk.LEFT, padx=5)

        resetButton = tk.Button(buttonFrame, text="Reset to Default", bg="#222222", fg="white", font=self.textFont, command=self.resetExtensions)
        resetButton.pack(side=tk.LEFT, padx=5)

        closeButton = tk.Button(buttonFrame, text="Close", bg="#222222", fg="white", font=self.textFont, command=settingsWindow.destroy)
        closeButton.pack(side=tk.LEFT, padx=5)

    def populateExtensionsList(self):
        """Populates the extensions list in the scrollable frame"""
        # Clear existing frames
        for frame in self.extension_frames.values():
            frame.destroy()
        
        self.entries = {}
        self.extension_frames = {}
        
        for extName, extList in self.extensions.items():
            frame = tk.Frame(self.scrollable_frame, bg="#333333", relief=tk.RIDGE, bd=1, width=700)
            frame.pack(pady=10, padx=10, anchor="center")
            self.extension_frames[extName] = frame

            # Extension name label
            extLabel = tk.Label(frame, text=f"{extName}:", bg="#333333", fg="#B8FFC7", font=self.textFont)
            extLabel.pack(side=tk.LEFT, padx=10, pady=8)

            # Label field for extensions (read-only)
            extDisplay = tk.Label(frame, text=", ".join(self.extensions.get(extName, extList)), bg="#222222", fg="white", width=35, justify=tk.LEFT, wraplength=300)
            extDisplay.pack(side=tk.LEFT, padx=5, pady=8)
            self.entries[extName] = extDisplay

            # Add button for this extension
            addButton = tk.Button(frame, text="Add", bg="#222222", fg="white", font=self.textFont,
                                 command=lambda name=extName: self.addExtensionToList(name))
            addButton.pack(side=tk.LEFT, padx=5, pady=8)

            # Remove button for this extension
            removeButton = tk.Button(frame, text="Remove", bg="#222222", fg="white", font=self.textFont,
                                    command=lambda name=extName: self.removeExtensionFromList(name))
            removeButton.pack(side=tk.LEFT, padx=5, pady=8)

            # Remove folder button (only for non-default folders)
            if extName not in self.DEFAULT_EXTENSIONS:
                removeFolderButton = tk.Button(frame, text="Delete Folder", bg="#8B0000", fg="white", font=self.textFont,
                                              command=lambda name=extName: self.removeFolder(name))
                removeFolderButton.pack(side=tk.LEFT, padx=5, pady=8)

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

    def removeExtensionFromList(self, extensionName):
        """Opens a dialog to remove an extension from the list"""
        if not self.extensions[extensionName]:
            messagebox.showwarning("No Extensions", f"There are no extensions in '{extensionName}' to remove.")
            return

        removeWindow = tk.Toplevel(self.root)
        removeWindow.title(f"Remove Extension from {extensionName}")
        removeWindow.geometry("350x300")
        removeWindow.configure(bg="#222222")

        label = tk.Label(removeWindow, text=f"Select extension to remove from '{extensionName}':", bg="#222222", fg="white", font=self.textFont)
        label.pack(pady=10)

        # Create a listbox with scrollbar for extension selection
        scrollFrame = tk.Frame(removeWindow, bg="#222222")
        scrollFrame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(scrollFrame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(scrollFrame, bg="#333333", fg="white", yscrollcommand=scrollbar.set, height=8)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # Populate listbox with current extensions
        for ext in self.extensions[extensionName]:
            listbox.insert(tk.END, ext)

        def removeSelected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an extension to remove.")
                return
            
            selectedExt = listbox.get(selection[0])
            self.extensions[extensionName].remove(selectedExt)
            self.entries[extensionName].config(text=", ".join(self.extensions[extensionName]))
            self.saveSettings()
            removeWindow.destroy()

        removeButton = tk.Button(removeWindow, text="Remove", bg="#222222", fg="white", command=removeSelected)
        removeButton.pack(pady=5)

        cancelButton = tk.Button(removeWindow, text="Cancel", bg="#222222", fg="white", command=removeWindow.destroy)
        cancelButton.pack(pady=5)

        removeWindow.grab_set()
        removeWindow.wait_window(removeWindow)

    def addNewFolder(self):
        """Opens a dialog to add a new folder category"""
        addFolderWindow = tk.Toplevel(self.root)
        addFolderWindow.title("Add New Folder")
        addFolderWindow.geometry("300x150")
        addFolderWindow.configure(bg="#222222")

        label = tk.Label(addFolderWindow, text="Enter folder name:", bg="#222222", fg="white", font=self.textFont)
        label.pack(pady=10)

        entry = tk.Entry(addFolderWindow, width=25)
        entry.pack(pady=10)
        entry.focus()

        def addFolder():
            folderName = entry.get().strip()
            if not folderName:
                messagebox.showwarning("Invalid Input", "Please enter a folder name.")
                return
            
            if folderName in self.extensions:
                messagebox.showwarning("Duplicate", f"Folder '{folderName}' already exists.")
                return
            
            # Add the new folder with an empty extension list
            self.extensions[folderName] = []
            self.saveSettings()
            messagebox.showinfo("Success", f"Folder '{folderName}' added successfully!")
            
            # Refresh the list if the settings window is still open
            if hasattr(self, 'scrollable_frame') and self.settingsWindow.winfo_exists():
                self.populateExtensionsList()
            
            addFolderWindow.destroy()

        addButton = tk.Button(addFolderWindow, text="Add", bg="#222222", fg="white", command=addFolder)
        addButton.pack(pady=5)

        cancelButton = tk.Button(addFolderWindow, text="Cancel", bg="#222222", fg="white", command=addFolderWindow.destroy)
        cancelButton.pack(pady=5)

        addFolderWindow.grab_set()
        addFolderWindow.wait_window(addFolderWindow)

    def removeFolder(self, folderName):
        """Removes a custom folder category"""
        response = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the '{folderName}' folder and all its associations?")
        if response:
            del self.extensions[folderName]
            self.saveSettings()
            messagebox.showinfo("Success", f"Folder '{folderName}' deleted successfully!")
            
            # Refresh the list if the settings window is still open
            if hasattr(self, 'scrollable_frame') and self.settingsWindow.winfo_exists():
                self.populateExtensionsList()

        
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
    
    def textFont(self):
        return self.guiFont(size=12)