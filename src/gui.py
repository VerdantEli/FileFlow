from pathlib import Path
import os
import time
import tkinter as tk
import threading
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

    def organizeFiles(self,message):
        inputFolder = Organizer(self.folder,self.db,self.onStatus,duplicateCallback=self.duplicateWindow,progressCallback=self.processCallback)
        threading.Thread(target=inputFolder.organize).start()

    def undo(self):
        inputFolder = Organizer(self.folder,self.db,self.onStatus,duplicateCallback=self.duplicateWindow,progressCallback=self.processCallback)
        threading.Thread(target=inputFolder.undo).start()

    def onStatus(self,message):
        if message == "Yes":
            self.root.after(0, self.showLogs)

    def processCallback(self, processed, total):
        self.root.after(0, self._updateProgress, processed, total)

    def showLogs(self):
        # Clear existing entries and show updated logs
        self.showTable.delete(*self.showTable.get_children())
        logs = self.db.getLogs()
        for log in logs:
            self.showTable.insert("", "end", values=log)
            

    def mainUI(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("green.Horizontal.TProgressbar", foreground="#B8FFC7", background='#B8FFC7')

        self.headerFont = font.Font(family= "Century Gothic",size=26)
        self.textFont = font.Font(family="Century Gothic",size=12)

        self.directoryLabel=tk.Label(self.root,text=self.folder)
        self.directoryLabel.config(bg="#222222",fg="white",font=self.headerFont)
        self.directoryLabel.pack(side=tk.TOP,pady=10)
        self.directorySelect = tk.Button(self.root,text="Change Directory", bg="#222222", fg="white",font=self.textFont,command=self.selectFolder)
        self.directorySelect.pack(side=tk.TOP)

        self.buttonFrame = tk.Frame(self.root, bg="#222222")
        self.buttonFrame.pack(side=tk.TOP, pady=10)

        self.organizeButton = tk.Button(self.buttonFrame,text="Click to organize!", bg="#222222", font=self.textFont, fg="white", command=lambda:self.organizeFiles(message=None))
        self.organizeButton.pack(side=tk.LEFT, padx=5)

        self.undoButton = tk.Button(self.buttonFrame,text="Undo Last Action", bg="#222222",font=self.textFont,fg="white",command=lambda:self.undo())
        self.undoButton.pack(side=tk.LEFT, padx=5)

        self.progressBar = ttk.Progressbar(self.root, mode='determinate',style="green.Horizontal.TProgressbar")
        self.progressBar.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)


        self.logsLabel=tk.Label(self.root,text="History Data",bg="#222222",fg="white",font=self.headerFont)
        self.logsLabel.pack(side=tk.TOP,pady=10)
        
        cols = ('Timestamp','Status','File Name', 'From Path', 'To Path')
        style.configure("Treeview", background="#222222", foreground="white", fieldbackground="#222222")
        style.configure("Treeview.Heading", background="#222222", foreground="white",font=self.textFont)
        self.showTable = ttk.Treeview(self.root,columns=cols,show='headings', style="Treeview")
        for col in cols:
            self.showTable.heading(col,text=col)
        self.showTable.pack(side=tk.TOP,fill=tk.BOTH,expand=True)

    def _updateProgress(self, processed, total):
        self.progressBar.config(mode='determinate', maximum=total)
        self.progressBar['value'] = processed
        if processed >= total:
            self.progressBar['value'] = 0

    def duplicateWindow(self,fileName=""):
        root = tk.Toplevel()
        root.geometry("400x200")
        root.configure(bg="#222222")
        root.title("Duplicate Detected")

        nameLabel = tk.Label(root, text=f"File: {os.path.basename(fileName)}", bg="#222222", fg="white")
        nameLabel.pack(pady=10)

        label = tk.Label(root, text="Duplicate file detected. Choose an action:",bg="#222222",fg="white")
        label.pack(pady=10)
        
        choice = tk.StringVar(value="keep")
        
        def setChoice(value):
            choice.set(value)
            root.destroy()
        
        keepButton = tk.Button(root, text="Keep (skip)", bg="#222222", fg="white", command=lambda: setChoice("keep"))
        keepButton.pack(pady=5)
        
        renameButton = tk.Button(root, text="Rename", bg="#222222", fg="white", command=lambda: setChoice("rename"))
        renameButton.pack(padx=5)

        deleteButton = tk.Button(root, text="Delete", bg="#222222", fg="white", command=lambda: setChoice("delete"))
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
        root.configure(bg="#222222")
        root.title("Rename File")

        label = tk.Label(root, text="Enter new file name:", bg="#222222", fg="white")
        label.pack(pady=10)
        entry = tk.Entry(root)
        entry.pack(pady=5)
        newName = ""
        def submit():
            nonlocal newName
            newName = entry.get()
            root.destroy()
        submitButton = tk.Button(root, text="Submit", bg="#222222", fg="white", command=submit)
        submitButton.pack(pady=5)
        root.grab_set()
        root.wait_window(root)  
        return newName
