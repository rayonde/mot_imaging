import tkinter as tk
from tkinter import ttk
from config import config
from .helper import FloatEntry

class ExperimentTab(ttk.Frame):
    """Tab for viewing and reconfiguring some experimental parameters"""
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.unit_section = "unit"
        self.exp_params = {}

        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side="left", fill="both", expand=True)
        
        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self._set_basic_frame(self.left_frame)
        self._set_cooling_frame(self.left_frame)
        
        self._set_repump_frame(self.right_frame)
        
        save = ttk.Button(self.right_frame, text="Save Experiment Config", command=self._save_config)
        save.pack(side="bottom", fill="both", padx=5, pady=5)
    
    def _set_basic_frame(self, frame):
        # Basic parameters
        section_name = "atoms"
        basic_frame = ttk.LabelFrame(frame, text="Basics")
        basic_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        row_idx = 0
        for key in config[section_name].keys():
            text = key.replace("_", " ").capitalize()
            ttk.Label(basic_frame, text=text).grid(row=row_idx, column=0)
            unit = config[self.unit_section].get(key) or None

            if unit:
                ttk.Label(basic_frame, text=unit).grid(row=row_idx, column=2)
                entry = FloatEntry(basic_frame )
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].getfloat(key))
                self.exp_params[f"{section_name}.{key}"] = entry.get()
            else:
                entry = ttk.Entry(basic_frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].get(key))
                self.exp_params[f"{section_name}.{key}"] = entry.get()
            row_idx += 1
        
    def _set_cooling_frame(self, frame):
        # Cooling light parameters
        section_name = "cooling"
        label_frame = ttk.LabelFrame(frame, text="Cooling Beam")
        label_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        row_idx = 0
        for key in config[section_name].keys():
            text = key.replace("_", " ").capitalize()
            ttk.Label(label_frame, text=text).grid(row=row_idx, column=0)
            
            unit = config[self.unit_section].get(key)
            has_unit = False if unit is None else True
            is_float = self.is_float(config[section_name].get(key))

            if has_unit and is_float:
                ttk.Label(label_frame, text=unit).grid(row=row_idx, column=2)
                entry = FloatEntry(label_frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].getfloat(key))
                self.exp_params[f"{section_name}.{key}"] = entry.get()
            else:
                entry = ttk.Entry(label_frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].get(key))
                self.exp_params[f"{section_name}.{key}"] = entry.get()
            row_idx += 1

    def _set_repump_frame(self, frame):
        # Repump light parameters
        section_name = "repump"
        label_frame = ttk.LabelFrame(frame, text="Repump Beam")
        label_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        row_idx = 0
        for key in config[section_name].keys():
            text = key.replace("_", " ").capitalize()
            ttk.Label(label_frame, text=text).grid(row=row_idx, column=0)
            
            unit = config[self.unit_section].get(key)
            has_unit = False if unit is None else True
            is_float = self.is_float(config[section_name].get(key))

            if has_unit and is_float:
                ttk.Label(label_frame, text=unit).grid(row=row_idx, column=2)
                entry = FloatEntry(label_frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].getfloat(key))
                self.exp_params[f"{section_name}.{key}"] = entry.get()
            else:
                entry = ttk.Entry(label_frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].get(key))
                self.exp_params[f"{section_name}.{key}"] = entry.get()
            row_idx += 1

    def _save_config(self):
        for name, value in self.exp_params.items():
            section, key = name.split(".")
            if value:
                config[section][key] = str(value)
        config.save()

    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False
