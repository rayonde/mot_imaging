import tkinter as tk
from tkinter import ttk
from config import config
from .helper import FloatEntry
import logging

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
        
        self._display_items(label_frame, section_name)

    def _update_cooling_view(self, frame):
        # Cooling light parameters
        section_name = "cooling"
        label_name = "Cooling Light Parameters"
        label_frame = ttk.LabelFrame(frame, text=label_name)
        label_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        self._display_items(label_frame, section_name)

    def _update_repump_view(self, frame):
        # Repump light parameters
        section_name = "repump"
        label_name = "Repump Light Parameters"
        label_frame = ttk.LabelFrame(frame, text=label_name)
        label_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        self._display_items(label_frame, section_name)

    def _display_items(self, frame, section_name):
        """Display a section of the config file by enumerating"""
        row_idx = 0
        for key in config[section_name].keys():
            text = key.replace("_", " ").capitalize()
            ttk.Label(frame, text=text).grid(row=row_idx, column=0)

            unit = config[self.unit_section].get(key)
            var = config[section_name].get(key)
            has_unit = True if unit else False

            if isinstance(var, float):
                entry = FloatEntry(frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, var)
                entry.bind('<Return>', self._create_modified_handler(entry, section_name, key, float))
            elif isinstance(var, int):
                entry = ttk.Entry(frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, var)
                entry.bind('<Return>', self._create_modified_handler(entry, section_name, key, int))
            elif isinstance(var, list):
                entry = ttk.Entry(frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, self.tostring(var))
                entry.bind('<Return>', self._create_modified_handler(entry, section_name, key, self.tolist))
            else:
                entry = ttk.Entry(frame)
                entry.grid(row=row_idx, column=1)
                entry.insert(0, var)
                entry.bind('<Return>', self._create_modified_handler(entry, section_name, key, str))
            if has_unit:
                ttk.Label(frame, text=unit).grid(row=row_idx, column=2)
            row_idx += 1


    def _create_modified_handler(self, entry, section_name, key, value_type):
        """Create a modified event handler for the entry widget"""
        def handler(event):
            value = entry.get()
            if value:
                try:
                    converted_value = value_type(value.strip())
                    self.exp_params.setdefault(section_name, {})[key] = converted_value
                except ValueError:
                    logging.warning(value_type)
                    logging.warning(f" {value.strip()} cannot to be converted")
            else:
                    self.exp_params.setdefault(section_name, {})[key] = None
        return handler

        
    def _save_config(self):
        print(self.exp_params)
        for section in self.exp_params.keys():
            if isinstance(self.exp_params[section], dict):
                for key in self.exp_params[section].keys():
                    config[section][key] = self.exp_params[section][key]
        config.save()
        logging.info("Saved experiment config to config.yaml")
    
    def tostring(self, float_list):
        string = ""
        for value in float_list:
            string += f"{value},"
        return string[:-1]
    
    def tolist(self, string):
        float_list = []
        values = string.split(',')
        for value in values:
            try:
                float_value = float(value.strip())
                float_list.append(float_value)
            except ValueError:
                logging.warning(f"Could not convert {value} to float")
        return float_list
