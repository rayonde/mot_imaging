import tkinter as tk
import tkinter.font as font
from tkinter import ttk
import tkinter.filedialog as fd 
import os 

from config import config 
from .logs import LogTextBox
from .settings import Settings
from .plots import MplFigure
from .shots import ShotList, ShotFit, ExperimentParams, ThreeROI
from .sequences import ToFFit, AtomNumberOptimization
from .camera import CameraTab
from .experiment import ExperimentTab
pad = 5 

class Tab(ttk.Notebook):
    """Packed tabbed frame to choose between different modes of the application."""
    def __init__(self, master, controller=None, **kwargs):
        self.master = master
        self.controller = controller
        super().__init__(self.master)
  
        # Create tabs
        self.camera = CameraTab(self, self.controller)
        self.exp = ExperimentTab(self)
        self.shot_fit = ShotFit(self, self.controller)
        self.tof_fit = ToFFit(self, self.controller)
        self.atom_number_fit = AtomNumberOptimization(self, self.controller)
        self.three_roi_atom_count = ThreeROI(self, self.controller)
        self.settings = Settings(self)
        
        self.add(self.camera, text="Camera", padding=10)
        self.add(self.exp, text="Experiment Settings", padding=10)
        self.add(self.shot_fit, text="Gaussian", padding=10)
        self.add(self.tof_fit, text="Temperature", padding=10)
        self.add(self.atom_number_fit, text="Atom # Optimization", padding=10)
        self.add(self.three_roi_atom_count, text="Three ROIs", padding=10)
        self.add(self.settings, text="Settings", padding=10)

class MainWindow(ttk.Frame):
    """Main window of the application."""
    def __init__(self,  controller=None, app=None, **kwargs):
        
        self.master = tk.Tk()
        self.controller = controller
        self.app = app 
        
        try:
            self.master.title(config.name)
        except:
            self.master.title("Absorption Imaging")
        #self.master.geometry("1200x1000")
        self.master.resizable(True, True)
        
        super().__init__(self.master, **kwargs)

        # Create a menu bar
        self.menu_bar = tk.Menu(self.master)
        self.path_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.path_menu.add_command(label="Change Path", command=self.open_directory)
        self.menu_bar.add_cascade(label="Watch Path", menu=self.path_menu)
        

        self.master.config(menu=self.menu_bar)
        
        default_font = font.nametofont("TkTextFont")
        default_font.configure(size=14)
        
        # Initialize our application window
        self.pack(fill="both", expand=True)

        # Row 0 and column 1 expand when window is resized
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)
        self.grid_columnconfigure(1, weight=1)
        #######################################################################
        # Mode selection frame
        self.tab = Tab(self, self.controller)
        self.tab.grid(row=0, column=0, sticky="nsew")

        #######################################################################
        # Create a frame for figures
        plot_frame = ttk.LabelFrame(self)
        plot_frame.grid(row=0, column=1, rowspan=2, padx=pad, pady=pad, sticky="NSEW")
        self.plot = MplFigure(plot_frame)

        #######################################################################
        # Create a frame for infos and logs
        info_frame = ttk.Frame(self)
        info_frame.grid(row=1, column=0,padx=pad, pady=pad, sticky="nsew")

        # In info frame create a shot info frame
        shot_info_frame = ttk.Labelframe(info_frame, text="Shot info")
        shot_info_frame.pack(fill=tk.BOTH, expand=True)
        self.shot_info_table = ShotList(shot_info_frame, self.controller, height=8)

        ## Logs
        log_frame = ttk.Labelframe(info_frame, text="Logs", relief=tk.SUNKEN)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log = LogTextBox(log_frame)

    def open_directory(self):
        """Open directory dialog and update watch directory"""
        folder_path = fd.askdirectory()
        if folder_path:
            # On Windows, replace backslashes with forward slashes
            if "\\" in folder_path:
                folder_path = folder_path.replace("\\", "/")
            config["watch_directory"] = folder_path
            config.save()

            self.app.update_watch_directory(folder_path)

