import tkinter as tk
from tkinter import ttk
from config import config
from .helper import FloatEntry

class ExperimentTab(ttk.Frame):
    """Tab for viewing and reconfiguring some experimental parameters"""
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.config_params = {}

        frame = ttk.LabelFrame(self)
        frame.pack(expand=True)

        p_idx = 0
        for section in ("camera", "beam"):
            for key in config[section].keys():
                text = key.replace("_", " ").capitalize()
                ttk.Label(frame, text=text).grid(row=p_idx, column=0)

                units = type(config).units.get(section, {}).get(key)
                if units:
                    ttk.Label(frame, text=units).grid(row=p_idx, column=2)

                entry = FloatEntry(frame, state="normal")
                entry.grid(row=p_idx, column=1)
                entry.insert(0, config[section].getfloat(key))
                self.config_params[f"{section}.{key}"] = entry

                p_idx += 1

        save = ttk.Button(frame, text="Save", command=self._save_config)
        save.grid(row=p_idx, column=1)

    def _save_config(self):
        for name, entry in self.config_params.items():
            section, key = name.split(".")
            config[section][key] = str(entry.get())
        config.save()
