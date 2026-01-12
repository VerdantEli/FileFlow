from pathlib import Path
import tkinter as tk
from tkinter import filedialog,ttk
from src.fileorganizer import Organizer
from src.database import Database

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.folder= Path.home() / "Downloads"
        self.db=Database()
        self.db.connect()
        self.db.tableCreation()
        self.mainUI()

    def selectFolder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder=folder
            self.directoryLabel.config(text=self.folder)

    def organizeFiles(self):
        inputFolder = Organizer(self.folder,self.db)
        inputFolder.organize()
        self.showLogs()

    def showLogs(self):
        self.showTable.delete(*self.showTable.get_children())
        logs = self.db.getLogs()
        for log in logs:
            self.showTable.insert("", "end", values=log)
            
    def undo(self):
        inputFolder = Organizer(self.folder,self.db)
        inputFolder.undo()
        self.showLogs()

    def mainUI(self):
        self.directoryLabel=tk.Label(self.root,text=self.folder)
        self.directoryLabel.pack()
        self.directorySelect = tk.Button(self.root,text="Change Directory", command=self.selectFolder)
        self.directorySelect.pack()

        self.organizeButton = tk.Button(self.root,text="Click to organize!",command=lambda:self.organizeFiles())
        self.organizeButton.pack()

        self.undoButton = tk.Button(self.root,text="Undo Last Action",command=lambda:self.undo())
        self.undoButton.pack()

        self.logsLabel=tk.Label(self.root,text="History Data",font=("Arial",30))
        self.logsLabel.pack()
        
        cols = ('Timestamp','Status','File Name', 'From Path', 'To Path')
        self.showTable = ttk.Treeview(self.root,columns=cols,show='headings')
        for col in cols:
            self.showTable.heading(col,text=col)
        self.showTable.pack()
