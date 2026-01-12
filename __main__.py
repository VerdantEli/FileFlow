import tkinter as tk
from src.gui import MainMenu

def main():
    root = tk.Tk()
    root.title("FileFlow - Lightweight File Organizer!")
    root.geometry("1000x500")
    root.configure(bg="#222222")
    interface = MainMenu(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()

