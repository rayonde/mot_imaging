import tkinter as tk
from tkinter import ttk
from config import config
from .helper import FloatEntry
import logging

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
        self.left_frame = ttk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Information frame
        self._update_info_view(frame=self.left_frame)

        # Save config button
        self.save = ttk.Button(self.left_frame, text="Save Config", command=self._save_config())
        self.save.pack(side="bottom", fill="x", expand=True, padx=5, pady=5)

        ##################################
        # Right column
        ##################################
        
        self.right_frame = ttk.Frame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self._update_camera_setting_view(frame=self.right_frame)

    def _get_config(self):
        # Get config parameters from config.py
        section = "camera_info"
        section_unit = "unit"
        self.camera_config.update(config[section])
        self.unit_config.update(config[section_unit])
        
        # Get the camera parameters from controller
        if self.camera_controller.isavailable:
            for name in self.camera_config.keys():
                if name in self.camera_controller.device_config.keys():
                    self.camera_config[name] = self.camera_controller.device_config[name]
                
                updated_config = None
                updated_config = self.camera_controller.get_config(name)
                if updated_config is not None:
                    self.camera_config[name] = updated_config
        
        # Get the camera setting from config.py
        setting_section = "camera"
        self.exp_config.update(config[setting_section])
        
        self.exp_config["ExposureTime"] = float(self.exp_config["ExposureTime"])
        self.exp_config["TriggerDelay"] = float(self.exp_config["TriggerDelay"])
        self.exp_config["Gain"] = float(self.exp_config["Gain"])

    def _update_info_view(self, frame):
        # Update the view of the camera parameters
        self.info_frame = ttk.LabelFrame(frame, text="Camera Information")
        self.info_frame.pack(side="top", fill="both", expand=True)
        
        row_id = 0
        for name, entry in self.camera_config.items():
            ttk.Label(self.info_frame, text=name).grid(row=row_id, column=0, padx=5, pady=5)
            ttk.Label(self.info_frame, text=entry).grid(row=row_id, column=1, padx=5, pady=5)
            if name in self.unit_config.keys():
                ttk.Label(self.info_frame, text=self.unit_config[name]).grid(row=row_id, column=2, padx=5, pady=5)           
            row_id += 1

    def _update_exp_config(self, name, value):
        # Update the experimental parameters
        self.exp_config[name] = value
        logging.info("Update the experimental parameters: {} = {}".format(name, value))
    
    def _update_camera_config(self, name, value):
        # Update the experimental parameters
        self.camera_config[name] = value
        logging.info("Update the camera parameters: {} = {}".format(name, value))

    def _update_camera_setting_view(self, frame):
        # Update the view of the camera parameters
        self.camera_frame = ttk.LabelFrame(frame, text="Camera Settings")
        self.camera_frame.grid(row=0, column=0, padx=5, pady=5)

        # Image number
        image_num_default = self.exp_config["image_num"]
        image_num_var = tk.IntVar(value=image_num_default)
        tk.Label(self.camera_frame, text="Image N:").grid(row=0, column=0, padx=5, pady=5)
        image_num_entry = tk.Entry(self.camera_frame, textvariable=image_num_var)
        image_num_entry.grid(row=0, column=1, padx=5, pady=5)
        image_num_entry.bind("<Return>", self._update_exp_config("image_num", int(image_num_entry.get())))

        # Tag to represent the image type: background, beam, mot
        tag_default = tk.StringVar(value=self.exp_config["tag"])
        tk.Label(self.camera_frame, text="Tag:").grid(row=1, column=0, padx=5, pady=5)
        tage_entry = tk.Entry(self.camera_frame, textvariable=tag_default)
        tage_entry.grid(row=1, column=1, padx=5, pady=5)
        tage_entry.bind("<Return>", self._update_exp_config("tag", tage_entry.get()))
        
        # Exposure time
        exposuret_default = self.exp_config["ExposureTime"]
        exposuret_var = tk.DoubleVar(value=exposuret_default) 
        tk.Label(self.camera_frame, text="Exposure time:").grid(row=2, column=0, padx=5, pady=5)
        exposure_entry = FloatEntry(self.camera_frame, textvariable=exposuret_var)
        exposure_entry.grid(row=2, column=1, padx=5, pady=5)
        exposure_entry.bind("<Return>", self._update_exp_config("ExposureTime", float(exposure_entry.get())))
        unit_exposuret = self.unit_config["ExposureTime"]
        tk.Label(self.camera_frame, text=unit_exposuret).grid(row=2, column=2, padx=5, pady=5)

        # Trigger delay
        exposured_default = self.exp_config["TriggerDelay"]
        exposured_var = tk.DoubleVar(value=exposured_default)
        tk.Label(self.camera_frame, text="Trigger delay:").grid(row=3, column=0, padx=5, pady=5)
        exposured_entry = FloatEntry(self.camera_frame, textvariable=exposured_var)
        exposured_entry.grid(row=3, column=1, padx=5, pady=5)
        exposured_entry.bind("<Return>", self._update_exp_config("TriggerDelay", float(exposured_entry.get())))
        unit_exposured = self.unit_config["TriggerDelay"]
        tk.Label(self.camera_frame, text=unit_exposured).grid(row=3, column=2, padx=5, pady=5)

        # exposuredelay_var = tk.StringVar(value=0)
        # tk.Label(self.camera_frame, text="Exposure delay(us)").grid(row=3, column=0, padx=5, pady=5)
        # tk.Entry(self.camera_frame, textvariable=exposuredelay_var).grid(row=3, column=1, padx=5, pady=5)

        # waittime_var = tk.StringVar(value=0)
        # tk.Label(self.camera_frame, text="Wait time(us):").grid(row=3, column=0, padx=5, pady=5)
        # tk.Entry(self.camera_frame, textvariable=waittime_var).grid(row=3, column=1, padx=5, pady=5)

        
    def _save_config(self):
        # Save the config to config.py
        pass
        # for name, entry in self.camera_config.items():
        #     section, key = name.split(".")
        #     config[section][key] = str(entry.get())
        # config.save()
