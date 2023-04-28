import tkinter as tk
import tkinter.font as font
from tkinter import ttk

# import config file from parent directory for test
import sys
sys.path.append("..")
from config import config 
from frame import SingleshotTab, RealtimeTab, AverageshotTab, TofTab, AtomnumberTab, ThreeroiTab, ExperimentalTab, SettingsTab
# import cofing file from parent directory for use 
# from ..config import config

class Tab(ttk.Notebook):
    """Packed tabbed frame to choose between different modes of the application."""
    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master)

        # Create tabs
        self.singleshot_tab = SingleshotTab(self, self.data)
        self.add(self.singleshot_tab, text="Single shot", padding=10)
        
        self.realtime_tab = RealtimeTab(self, self.data)
        self.add(self.realtime_tab, text="Real time", padding=10)

        self.averageshot_tab = AverageshotTab(self, self.data)
        self.add(self.averageshot_tab, text="Average shot", padding=10)

        self.tof_tab = TofTab(self, self.data)
        self.add(self.tof_tab, text="TOF", padding=10)

        self.atomnumber_tab = AtomnumberTab(self, self.data)
        self.add(self.atomnumber_tab, text="Atom number", padding=10)

        self.threeroi_tab = ThreeroiTab(self, self.data)   
        self.add(self.threeroi_tab, text="Three ROI", padding=10)

        self.experimental_tab = ExperimentalTab(self, self.data)
        self.add(self.experimental_tab, text="Experimental params", padding=10)

        self.settings_tab = SettingsTab(self, self.data)
        self.add(self.settings_tab, text="Settings", padding=10)
        
        self.pack(expand=True, fill=tk.BOTH)

class MainWindow(ttk.Frame):
    """Main window of the application."""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        
        try:
            self.master.title(config.name)
        except:
            self.master.title("Absorption Imaging")
        self.master.geometry("1200x1000")
        self.master.resizable(True, True)
        
        # Create a menu bar
        self.menu_bar = tk.Menu(self.master)

    
        self.path_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Image Path", menu=self.path_menu)
        # click on the menu item to open a dialog box to select the path
        self.path_menu.add_command(label="Settings", command=self.path_menu.invoke)


        self.save_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Save Path", menu=self.save_menu)
        self.save_menu.add_command(label="Settings", command=self.save_menu.invoke)
        
        self.master.config(menu=self.menu_bar)
    
        # Row 0 and column 1 expand when window is resized
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)
        self.grid_columnconfigure(1, weight=1)




# test
if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    app.mainloop()
