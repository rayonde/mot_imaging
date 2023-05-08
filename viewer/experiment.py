import tkinter as tk
from tkinter import ttk
from config import config
from .helper import FloatEntry

class ExperimentTab(ttk.Frame):
    """Tab for viewing and reconfiguring some experimental parameters"""
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        section = ("beam", "atoms")
        unit_section = "unit"
        self.exp_params = {}

        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side="left", fill="both", expand=True)
        
        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side="right", fill="both", expand=True)
        
        # Basic parameters
        section_name = "atoms"
        basic_frame = ttk.LabelFrame(self.left_frame, text=section_name)
        basic_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        row_idx = 0
        for key in config[section_name].keys():
            text = key.replace("_", " ").capitalize()
            ttk.Label(basic_frame, text=text).grid(row=row_idx, column=0)
            unit = config[unit_section].get(key) or None
            print(unit)
            if unit:
                ttk.Label(basic_frame, text=unit).grid(row=row_idx, column=2)
                entry = FloatEntry(basic_frame, state="disabled")
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].getfloat(key))
                self.exp_params[f"{section_name}.{key}"] = entry
            else:
                entry = ttk.Entry(basic_frame, state="disabled")
                entry.grid(row=row_idx, column=1)
                entry.insert(0, config[section_name].get(key))
                self.exp_params[f"{section_name}.{key}"] = entry



        save = ttk.Button(self, text="Save Experiment Config", command=self._save_config)
        save.pack(side="bottom", fill="x", padx=5, pady=5)

    def _save_config(self):
        for name, entry in self.config_params.items():
            section, key = name.split(".")
            config[section][key] = str(entry.get())
        config.save()
