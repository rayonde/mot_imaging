import tkinter as tk
import tkinter.font as font
from tkinter import ttk

# import config file from parent directory for test
import sys
sys.path.append("..")
from config import config 
# import cofing file from parent directory for use 
# from ..config import config

from widgets import *
from plot import Figure

class Tab(ttk.Notebook):
    """Packed tabbed frame to choose between different modes of the application."""
    def __init__(self, master, data=None, **kwargs):
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
    def __init__(self, master, data=None,  **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.data = data
        
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
        #######################################################################
        # Mode selection frame
        self.tab = Tab(self, self.data)
        self.tab.grid(row=0, column=0, sticky="nsew")

        #######################################################################
        # Plot frame contains the orginal image and the processed image
        pad = 5
        plot_frame = ttk.Frame(self)
        plot_frame.grid(row=0, column=1, rowspan=2, padx=pad, pady=pad, sticky="nsew")
        
        # Create a frame for the raw image
        raw_frame = ttk.Labelframe(plot_frame, text="raw image")
        raw_frame.grid(row=0, column=0, padx=pad, pady=pad, sticky="nsew")
        

        # Create a frame for the processed image
        processed_frame = ttk.Labelframe(plot_frame, text="processed image")
        processed_frame.grid(row=1, column=0, padx=pad, pady=pad, sticky="nsew")
        self.plot = Figure(processed_frame)
        
        
        #######################################################################
        # Create a frame for infos and logs
        info_frame = ttk.Frame(self)
        info_frame.grid(row=1, column=0,padx=pad, pady=pad, sticky="nsew")

        # In info frame create a shot info frame
        shot_info_frame = ttk.Labelframe(info_frame, text="Shot info")
        shot_info_frame.pack(fill=tk.BOTH, expand=True)
        self.shot_info_table = ShotInfoTable(shot_info_frame, self.data)

        ## Logs
        log_frame = ttk.Labelframe(info_frame, text="Logs", relief=tk.SUNKEN)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log = LogTextBox(log_frame, self.data)


# test
if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    app.mainloop()
