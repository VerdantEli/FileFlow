import tkinter as tk
from tkinter import filedialog
from fileorganizer import Organizer

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.folder= "None"
        self.mainUI()

    def selectFolder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder=folder
            self.directoryLabel.config(text=self.folder)

    def organizeFiles(self):
        inputFolder = Organizer(self.folder)
        inputFolder.organize()

    def mainUI(self):
        self.directoryLabel=tk.Label(self.root,text=self.folder)
        self.directoryLabel.pack()
        self.directorySelect = tk.Button(self.root,text="Change Directory", command=self.selectFolder)
        self.directorySelect.pack()

        self.organizeButton = tk.Button(self.root,text="Click to organize!",command=self.organizeFiles)
        self.organizeButton.pack()