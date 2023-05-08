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
        self.unit_config = {}
        self.exp_config = {"image_num": 10, 
                                "tag": "background"}
        
        # Update config
        self._get_config()

        ##################################
        # Left column
        ##################################
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
    
    def _set_camera_config(self):
        """According to the camera_config distionary, set the parameters to the camera controller"""

        for name, entry in self.camera_config.items():
            self.camera_controller.set_config(name, entry.get())

    def _update_exp_config(self, name, value):
        """Update the experiment config"""
        self.exp_config[name] = value


    def _get_config(self):

        # Get config parameters from config.py
        section = "camera"
        section_unit = "unit"
        self.camera_config.update(config[section])
        self.unit_config.update(config[section_unit])
        
        # Get the camera parameters from controller
        if self.camera_controller.isavailable:
            self.camera_config["AcquisitionMode"] = self.camera_controller.get_config("AcquisitionMode")
            self.camera_config["PixelFormat"] = self.camera_controller.get_config("PixelFormat")
        
 
    def _update_info_view(self):
        # Update the view of the camera parameters
        self.info_frame = ttk.LabelFrame(self, text="Camera Information")
        self.info_frame.pack(side="left", fill="both", padx=5, pady=5, expand=True)

        for name, entry in self.camera_config.items():
            text = name.replace("_", " ").capitalize()
            ttk.Label(self.info_frame, text=text).grid(row=0, column=0, padx=5, pady=5)
            ttk.Label(self.info_frame, text=entry).grid(row=0, column=1, padx=5, pady=5)
            if name in self.unit_config.keys():
                ttk.Label(self.info_frame, text=self.unit_config[name]).grid(row=0, column=2, padx=5, pady=5)           

    def _save_config(self):
        # Save the config to config.py
        for name, entry in self.camera_config.items():
            section, key = name.split(".")
            config[section][key] = str(entry.get())
        config.save()

    def _update_settings_view(self):
        # Update the view of the camera parameters
        self.camera_frame = ttk.LabelFrame(self, text="Camera Settings")
        self.camera_frame.grid(row=1, column=0, padx=5, pady=5)
    
        # Image number
        image_num_default = tk.StringVar(value=self.camera_settings["image_num"])
        tk.Label(self.camera_frame, text="Image N:").grid(row=0, column=0, padx=5, pady=5)
        image_num_entry = tk.Entry(self.camera_frame, textvariable=image_num_default)
        image_num_entry.grid(row=0, column=1, padx=5, pady=5)
        image_num_entry.bind("<Return>", self._update_exp_config("image_num", image_num_default.get()))
        
        # Tag to represent the image type: background, beam, mot
        tag_var = tk.StringVar(value="background")
        tk.Label(self.camera_frame, text="Tag:").grid(row=1, column=0, padx=5, pady=5)
        tage_entry = tk.Entry(self.camera_frame, textvariable=tag_var)
        tage_entry.grid(row=1, column=1, padx=5, pady=5)
        tage_entry.bind("<Return>", self._update_exp_config("tag", tag_var.get()))
        
        # Exposure time
        exposuret_var = tk.StringVar(value=self.camera_config["ExposureTime"])
        tk.Label(self.camera_frame, text="Exposure t(us):").grid(row=2, column=0, padx=5, pady=5)
        exposure_entry = tk.Entry(self.camera_frame, textvariable=exposuret_var)
        exposure_entry.grid(row=2, column=1, padx=5, pady=5)
        exposure_entry.bind("<Return>", self._update_exposuret)


        exposuredelay_var = tk.StringVar(value=0)
        tk.Label(self.camera_frame, text="Exposure delay(us)").grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(self.camera_frame, textvariable=exposuredelay_var).grid(row=3, column=1, padx=5, pady=5)

        waittime_var = tk.StringVar(value=0)
        tk.Label(self.camera_frame, text="Wait time(us):").grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(self.camera_frame, textvariable=waittime_var).grid(row=3, column=1, padx=5, pady=5)
