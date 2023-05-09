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
        
        self._update_info_view(self.left_frame)
        self._update_cooling_view(self.left_frame)

        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side="right", fill="both", expand=True)
         
        self._update_repump_view(self.right_frame)

        self.save = ttk.Button(self.right_frame, text="Save Experiment Config", command=self._save_config)
        self.save.pack(side="bottom", fill="x", expand=True, padx=5, pady=5)
    
    def _update_info_view(self, frame):
        # Basic parameters
        section_name = "atoms"
        label_name = "Basic Parameters"
        label_frame = ttk.LabelFrame(frame, text=label_name)
        label_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        row_idx = 0
        for key in config[section_name].keys():
            text = key.replace("_", " ").capitalize()
            ttk.Label(label_frame, text=text).grid(row=row_idx, column=0)
            unit = config[self.unit_section].get(key) 
            has_unit = True if unit else False
            is_float = self.is_float(config[section_name].get(key))

            if has_unit and is_float:
                ttk.Label(label_frame, text=unit).grid(row=row_idx, column=2)
                entry = FloatEntry(label_frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].getfloat(key))
                self.exp_params[f"{section_name}.{key}"] = entry.get()
            elif has_unit and not is_float:
                ttk.Label(label_frame, text=unit).grid(row=row_idx, column=2)
                entry = ttk.Entry(label_frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].get(key))
                self.exp_params[f"{section_name}.{key}"] = entry.get()
            else:
                entry = ttk.Entry(label_frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].get(key))
                self.exp_params[f"{section_name}.{key}"] = entry.get()
            row_idx += 1

    def _update_cooling_view(self, frame):
        # Cooling light parameters
        section_name = "cooling"
        label_name = "Cooling Light Parameters"
        label_frame = ttk.LabelFrame(frame, text=label_name)
        label_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        row_idx = 0
        for key in config[section_name].keys():
            text = key.replace("_", " ").capitalize()
            ttk.Label(label_frame, text=text).grid(row=row_idx, column=0)
            unit = config[self.unit_section].get(key) 
            has_unit = True if unit else False
            is_float = self.is_float(config[section_name].get(key))

            if has_unit and is_float:
                ttk.Label(label_frame, text=unit).grid(row=row_idx, column=2)
                entry = FloatEntry(label_frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].getfloat(key))
                self.exp_params[f"{section_name}.{key}"] = entry.get()
            elif has_unit and not is_float:
                ttk.Label(label_frame, text=unit).grid(row=row_idx, column=2)
                entry = ttk.Entry(label_frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].get(key))
                self.exp_params[f"{section_name}.{key}"] = entry.get()
            else:
                entry = ttk.Entry(label_frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].get(key))
                self.exp_params[f"{section_name}.{key}"] = entry.get()
            row_idx += 1

    def _update_repump_view(self, frame):
        # Repump light parameters
        section_name = "repump"
        label_name = "Repump Light Parameters"
        label_frame = ttk.LabelFrame(frame, text=label_name)
        label_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        row_idx = 0
        for key in config[section_name].keys():
            text = key.replace("_", " ").capitalize()
            ttk.Label(label_frame, text=text).grid(row=row_idx, column=0)
            unit = config[self.unit_section].get(key) 
            has_unit = True if unit else False
            is_float = self.is_float(config[section_name].get(key))

            if has_unit and is_float:
                ttk.Label(label_frame, text=unit).grid(row=row_idx, column=2)
                entry = FloatEntry(label_frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].getfloat(key))
                self.exp_params[f"{section_name}.{key}"] = entry.get()
            elif has_unit and not is_float:
                ttk.Label(label_frame, text=unit).grid(row=row_idx, column=2)
                entry = ttk.Entry(label_frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].get(key))
                self.exp_params[f"{section_name}.{key}"] = entry.get()
            else:
                entry = ttk.Entry(label_frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].get(key))
                self.exp_params[f"{section_name}.{key}"] = entry.get()
            row_idx += 1

    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False
        
    def _save_config(self):
        for name, item in self.exp_params.items():
            section, key = name.split(".")
            if item:
                config[section][key] = str(item)
        config.save()
