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
        
        self.camera_info = {}
        self.camera_config = {}
        self.unit_config = {}
        self.exp_config = {}
        
        # Update config
        self._get_config()
        
        # Left column
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self._update_info_view(frame=self.left_frame)
        self._camera_control_button_left(frame=self.left_frame)
       
        # Right column
        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        self._update_camera_setting_view(frame=self.right_frame)
        self._camera_control_button_right(frame=self.right_frame)
 
    def _get_config(self):
        """Initialize the configuration variables."""
        # Load all parameters from config.py
        info_section = "camera_info"
        config_section = "camera"
        unit_section = "unit"
        exp_section = "experiment"
        self.camera_info.update(config[info_section])
        self.camera_config.update(config[config_section])
        self.unit_config.update(config[unit_section])
        self.exp_config.update(config[exp_section])
        
        # Update the camera info/config from controller
        self._update_info()
        self._update_setting()
    
    def _update_info(self):
        """Update the camera information from the controller."""
        if self.camera_controller.isavailable:
            for name in self.camera_info.keys():
                if name in self.camera_controller.device_config.keys():
                    self.camera_info[name] = self.camera_controller.device_config[name]
                
                result = self.camera_controller.get_config(name)
                if result is not None:
                    self.camera_info[name] = result

    def _update_setting(self):
        """Update the camera setting from the controller."""
        if self.camera_controller.isavailable:
            for name in self.camera_config.keys():
                result = self.camera_controller.get_config(name)
                if result is not None:
                    self.exp_config[name] = result

    def _update_info_view(self, frame):
        """ Display the camera information frame."""
        self.info_frame = ttk.LabelFrame(frame, text="Camera Information")
        self.info_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        row_id = 0
        for name, value in self.camera_info.items():
            ttk.Label(self.info_frame, text=name).grid(row=row_id, column=0, padx=5, pady=5)
            ttk.Label(self.info_frame, text=value).grid(row=row_id, column=1, padx=5, pady=5)
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

    def _save_config(self):
        # Save the camera info to config.ini
        section = "camera_info"
        for key, item in self.camera_info.items():
            config[section][key] = item
            
        config.save()

    def _update_camera_setting_view(self, frame):
        # Update the view of the camera parameters
        self.camera_frame = ttk.LabelFrame(frame, text="Camera Settings")
        self.camera_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        # Image number
        image_num_default = self.exp_config["image_num"]
        image_num_var = tk.IntVar(value=image_num_default)
        tk.Label(self.camera_frame, text="Image N:").grid(row=0, column=0, padx=5, pady=5)
        image_num_entry = tk.Entry(self.camera_frame, textvariable=image_num_var)
        image_num_entry.grid(row=0, column=1, padx=5, pady=5)
        image_num_entry.bind("<Return>", lambda event: self._update_exp_config("image_num", int(image_num_entry.get())))

        # Tag to represent the image type: background, beam, mot
        tag_default = tk.StringVar(value=self.exp_config["tag"])
        tk.Label(self.camera_frame, text="Tag:").grid(row=1, column=0, padx=5, pady=5)
        tag_options = ["background", "beam", "mot"]
        tag_selection = tk.OptionMenu(self.camera_frame, tag_default, *tag_options)
        tag_selection.grid(row=1, column=1, padx=5, pady=5, sticky="snew")
        tag_default.trace_add("write", lambda *args, var=tag_default: self._update_exp_config("tag", var.get()))

        # Exposure time
        exposuret_default = self.camera_config["ExposureTime"]
        exposuret_var = tk.DoubleVar(value=exposuret_default) 
        tk.Label(self.camera_frame, text="Exposure time:").grid(row=2, column=0, padx=5, pady=5)
        exposure_entry = tk.Entry(self.camera_frame, textvariable=exposuret_var)
        exposure_entry.grid(row=2, column=1, padx=5, pady=5)
        exposure_entry.bind("<Return>", lambda event: self._update_camera_config("ExposureTime", float(exposure_entry.get())))
        unit_exposuret = self.unit_config["ExposureTime"] or ""
        tk.Label(self.camera_frame, text=unit_exposuret).grid(row=2, column=2, padx=5, pady=5)

        # Trigger delay
        exposured_default = self.exp_config["TriggerDelay"]
        exposured_var = tk.DoubleVar(value=exposured_default)
        tk.Label(self.camera_frame, text="Trigger delay:").grid(row=3, column=0, padx=5, pady=5)
        exposured_entry = tk.Entry(self.camera_frame, textvariable=exposured_var)
        exposured_entry.grid(row=3, column=1, padx=5, pady=5)
        exposured_entry.bind("<Return>", lambda event: self._update_camera_config("TriggerDelay", float(exposured_entry.get())))
        unit_exposured = self.unit_config["TriggerDelay"] or ""
        tk.Label(self.camera_frame, text=unit_exposured).grid(row=3, column=2, padx=5, pady=5)

        # Trigger source
        tag_default = tk.StringVar(value=self.exp_config["tag"])
        tk.Label(self.camera_frame, text="Tag:").grid(row=1, column=0, padx=5, pady=5)
        tag_options = ["background", "beam", "mot"]
        tag_selection = tk.OptionMenu(self.camera_frame, tag_default, *tag_options)
        tag_selection.grid(row=1, column=1, padx=5, pady=5, sticky="snew")
        tag_default.trace_add("write", lambda *args, var=tag_default: self._update_exp_config("tag", var.get()))

        # Wait time
        wait_time_default = self.exp_config["wait_time"]
        wait_time_var = tk.DoubleVar(value=wait_time_default)
        tk.Label(self.camera_frame, text="Wait time:").grid(row=4, column=0, padx=5, pady=5)
        wait_time_entry = tk.Entry(self.camera_frame, textvariable=wait_time_var)
        wait_time_entry.grid(row=4, column=1, padx=5, pady=5)
        wait_time_entry.bind("<Return>", lambda event: self._update_exp_config("wait_time", float(wait_time_entry.get())))
        unit_wait_time = self.unit_config["wait_time"] or ""
        tk.Label(self.camera_frame, text=unit_wait_time).grid(row=4, column=2, padx=5, pady=5)
        
        # File format
        fileformat_default = tk.StringVar(value=self.exp_config["fileformat"])
        tk.Label(self.camera_frame, text="File format:").grid(row=5, column=0, padx=5, pady=5)
        fileformat_entry = tk.Entry(self.camera_frame, textvariable=fileformat_default)
        fileformat_entry.grid(row=5, column=1, padx=5, pady=5)
        fileformat_entry.bind("<Return>", lambda event: self._update_exp_config("fileformat", fileformat_entry.get()))
        
        # File name 
        filename_default = tk.StringVar(value=self.exp_config["filename"])
        tk.Label(self.camera_frame, text="File name:").grid(row=6, column=0, padx=5, pady=5)
        filename_entry = tk.Entry(self.camera_frame, textvariable=filename_default)
        filename_entry.grid(row=6, column=1, padx=5, pady=5)
        filename_entry.bind("<Return>", lambda event: self._update_exp_config("filename", filename_entry.get()))
        
        # Folder name
        foldername_default = tk.StringVar(value=self.exp_config["folder"])
        tk.Label(self.camera_frame, text="Folder:").grid(row=7, column=0, padx=5, pady=5)
        foldername_entry = tk.Entry(self.camera_frame, textvariable=foldername_default)
        foldername_entry.grid(row=7, column=1, padx=5, pady=5)
        foldername_entry.bind("<Return>", lambda event: self._update_exp_config("folder", foldername_entry.get()))
    
    def _camera_control_button_left(self, frame):
        # Config the trigger setting button
        exposure_time = self.camera_config["ExposureTime"] or 'min'
        trigger_source = self.camera_config["TriggerSource"] or 'Line1'
        trigger_delay = self.camera_config["TriggerDelay"] or 0.0
        
        self.config_trigger_button = ttk.Button(
            frame, 
            text="Config Trigger", 
            command=lambda: self.camera_controller.config_trigger(exposure_time, trigger_source, trigger_delay))
        self.config_trigger_button.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        # Save config button
        self.save = ttk.Button(frame, text="Save Config", command=self._save_config())
        self.save.pack(side="top", fill="both", expand=True, padx=5, pady=5)
 
        # Reset the camera 
        self.reset_button = ttk.Button(
            frame,
            text="Reset Camera",
            command=lambda: self.camera_controller.reset_camera())
        self.reset_button.pack(side="top", fill="both", expand=True, padx=5, pady=5)
    
    def _camera_control_button_right(self, frame):
        
        # Start the acquisition
        num = self.exp_config["image_num"] or 1
        wait_time = self.exp_config["wait_time"] or 0.0

        self.acquisition_button = ttk.Button(
            frame,
            text="Start Acquisition",
            command=lambda: self.camera_controller.acquisition(num, wait_time))
        self.acquisition_button.pack(side="top", fill="both", expand=True, padx=5, pady=5)
    
    
    def _config_trigger(self):
        """Combo box for config trigger"""
        self.camera_controller.config_trigger()
        self._update_camera_config()
        
        self._get_config()
        self._update_info_view(frame=self.left_frame)