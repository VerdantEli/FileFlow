import tkinter as tk
from tkinter import filedialog,ttk
from fileorganizer import Organizer
from database import Database

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.folder= "None"
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
        inputFolder = Organizer(self.folder)
        inputFolder.organize()

    def showLogs(self):
        for item in self.showTable.get_children():
            self.showTable.delete(item)
        logs = self.db.getLogs()
        for log in logs:
            self.showTable.insert("", "end", values=log)
            

    def mainUI(self):
        self.directoryLabel=tk.Label(self.root,text=self.folder)
        self.directoryLabel.pack()
        self.directorySelect = tk.Button(self.root,text="Change Directory", command=self.selectFolder)
        self.directorySelect.pack()

        self.organizeButton = tk.Button(self.root,text="Click to organize!",command=self.organizeFiles)
        self.organizeButton.pack()

        self.logsLabel=tk.Label(self.root,text="History Data",font=("Arial",30))
        self.logsLabel.pack()
        
        cols = ('Timestamp','Status','File Name', 'From Path', 'To Path')
        self.showTable = ttk.Treeview(self.root,columns=cols,show='headings')
        for col in cols:
            self.showTable.heading(col,text=col)
        self.showTable.pack()

        self.refreshButton = tk.Button(self.root, text="Refresh History", command=self.showLogs)
        self.refreshButton.pack()