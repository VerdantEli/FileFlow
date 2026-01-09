import tkinter as tk
from gui import MainMenu

def main():
    root = tk.Tk()
    root.title("FileFlow - Lightweight File Organizer!")
    root.geometry("1200x800")
    interface = MainMenu(root)
    

    root.mainloop()

if __name__ == "__main__":
    main()
