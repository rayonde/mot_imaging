import tkinter as tk
from tkinter import ttk
from config import config
from .helper import FloatEntry

class CameraTab(ttk.Frame):
    """Tab for viewing and reconfiguring some experimental parameters"""
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
    
        self.camera_controller = controller.camera_controller
        self.camera_config = {}
        
        ##################################
        # Left column
        ##################################
        # Update config
        self._update_config()

        # Information frame
        self._update_info_view()

        # Camera settings frame
        self._update_camera_settings()

        # Save config button
        self.save = ttk.Button(self, text="Save Config", command=self._save_config())
        self.save.grid(row=2, column=0)

       
        ##################################
        # Right column
        ##################################
        # Camera control frame
        self.right_frame = ttk.Frame(self)
        #self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.right_frame.pack(side="right", fill="both", expand=True)
        
        self.setting_frame = ttk.LabelFrame(self.right_frame, text="Test Settings")
        self.setting_frame.pack(side=tk.TOP, fill="both", padx=5, pady=5)

        self.update_button = tk.Button(self.right_frame, text="Reset Camera")
        self.update_button.pack(side=tk.TOP, fill="both", padx=5, pady=5)

        self.reset_button = tk.Button(self.right_frame, text="Update Config")
        self.reset_button.pack(side=tk.TOP, fill="both", padx=5, pady=5)

        self.start_button = tk.Button(self.right_frame, text="Start Acquisition", background="green")
        self.start_button.pack(side=tk.TOP, fill="both", padx=5, pady=5)
        
        self.stop_button = tk.Button(self.right_frame, text="Stop Acquisition")
        self.stop_button.pack(side=tk.TOP, fill="both", padx=5, pady=5)

        self.continuous_button = tk.Button(self.right_frame, text="Continuous trigger", background="yellow")
        self.continuous_button.pack(side=tk.TOP, fill="both", padx=5, pady=5)
    
    def _update_config(self):
        # Get the camera parameters from controller
        if self.camera_controller.isavailable:
            self.camera_config["AcquisitionMode"] = self.camera_controller.get_config("AcquisitionMode")
            self.camera_config["PixelFormat"] = self.camera_controller.get_config("PixelFormat")
        # Get config parameters from config.py
        section = "camera"
        for key in config[section].keys():
            text = key.replace("_", " ").capitalize()

     
    def _update_info_view(self):
        # Update the view of the camera parameters
        self.info_frame = ttk.LabelFrame(self, text="Camera Information")
        self.info_frame.pack(side="left", fill="both", padx=5, pady=5, expand=True)

        for i, key in enumerate(self.camera_config.keys()):
            ttk.Label(self.info_frame, text=key).grid(row=i, column=0, padx=5, pady=5)
            ttk.Label(self.info_frame, text=self.camera_config[key]).grid(row=i, column=1, padx=5, pady=5)
    
    def _save_config(self):
        # Save the config to config.py
        for name, entry in self.camera_config.items():
            section, key = name.split(".")
            config[section][key] = str(entry.get())
        config.save()

    def _update_camera_settings(self):
        # Update the view of the camera parameters
        self.camera_frame = ttk.LabelFrame(self, text="Camera Settings")
        self.camera_frame.grid(row=1, column=0, padx=5, pady=5)
        
        imagenumber_var = tk.StringVar(value=100)
        tk.Label(self.camera_frame, text="Image N:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(self.camera_frame, textvariable=imagenumber_var).grid(row=0, column=1, padx=5, pady=5)

        tag_var = tk.StringVar(value="background")
        tk.Label(self.camera_frame, text="Tag:").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(self.camera_frame, textvariable=tag_var).grid(row=1, column=1, padx=5, pady=5)

        exposuret_var = tk.StringVar(value=46)
        tk.Label(self.camera_frame, text="Exposure t(us):").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(self.camera_frame, textvariable=exposuret_var).grid(row=2, column=1, padx=5, pady=5)

        exposuredelay_var = tk.StringVar(value=0)
        tk.Label(self.camera_frame, text="Exposure delay(us)").grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(self.camera_frame, textvariable=exposuredelay_var).grid(row=3, column=1, padx=5, pady=5)

        waittime_var = tk.StringVar(value=0)
        tk.Label(self.camera_frame, text="Wait time(us):").grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(self.camera_frame, textvariable=waittime_var).grid(row=3, column=1, padx=5, pady=5)
