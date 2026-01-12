from pathlib import Path
import tkinter as tk
from tkinter import filedialog,ttk,font
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
        self.headerFont = font.Font(family= "Century Gothic",size=26)
        self.textFont = font.Font(family="Century Gothic",size=12)

        self.directoryLabel=tk.Label(self.root,text=self.folder)
        self.directoryLabel.config(bg="#222222",fg="white",font=self.headerFont)
        self.directoryLabel.pack(side=tk.TOP,pady=10)
        self.directorySelect = tk.Button(self.root,text="Change Directory", bg="#222222", fg="white",font=self.textFont,command=self.selectFolder)
        self.directorySelect.pack(side=tk.TOP)

        self.buttonFrame = tk.Frame(self.root, bg="#222222")
        self.buttonFrame.pack(side=tk.TOP, pady=10)

        self.organizeButton = tk.Button(self.buttonFrame,text="Click to organize!", bg="#222222", font=self.textFont, fg="white", command=lambda:self.organizeFiles())
        self.organizeButton.pack(side=tk.LEFT, padx=5)

        self.undoButton = tk.Button(self.buttonFrame,text="Undo Last Action", bg="#222222",font=self.textFont,fg="white",command=lambda:self.undo())
        self.undoButton.pack(side=tk.LEFT, padx=5)

        self.logsLabel=tk.Label(self.root,text="History Data",bg="#222222",fg="white",font=self.headerFont)
        self.logsLabel.pack(side=tk.TOP,pady=10)
        
        cols = ('Timestamp','Status','File Name', 'From Path', 'To Path')
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#222222", foreground="white", fieldbackground="#222222")
        style.configure("Treeview.Heading", background="#222222", foreground="white",font=self.textFont)
        self.showTable = ttk.Treeview(self.root,columns=cols,show='headings', style="Treeview")
        for col in cols:
            self.showTable.heading(col,text=col)
        self.showTable.pack(side=tk.TOP,fill=tk.BOTH,expand=True)
