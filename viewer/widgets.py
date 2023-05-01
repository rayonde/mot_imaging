# Widget components for the viewer application

import tkinter as tk
import tkinter.ttk as ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.scrolledtext as tkst


class SingleshotTab(tk.Frame):
    """Tab for single shot mode."""

    def __init__(self, master, presenter):
        self.master = master
        self.presenter = presenter

        self.fit_params = {}
        self.config_params = {}

        super().__init__(self.master)

        # Fit Parameters (uneditable)
        params_frame = ttk.Frame(self)
        params_frame.pack(side="left", expand=True, pady=15)
        keys = ["N", "A", "x0", "y0", "sx", "sy", "theta", "z0"]
        labels = ["N", "A", "x_0", "y_0", "σ_x", "σ_y", "θ", "z_0"]
        for l_idx, lbl in enumerate(labels):
            ttk.Label(params_frame, text=lbl).grid(row=l_idx, column=0)

        for f_idx in range(8):
            entry = ttk.Entry(params_frame, state="readonly")
            entry.grid(row=f_idx, column=1)
            self.fit_params[keys[f_idx]] = entry

        options_frame = ttk.Frame(self)
        options_frame.pack(side="left", expand=True, pady=15)

        roi_control = RegionOfInterestControl(options_frame)
        roi_control.pack(fill="x", expand=True)

        center_control = CenterControl(options_frame, self.presenter)
        center_control.pack(fill="x", expand=True)

        fit_frame = FitControl(options_frame)
        fit_frame.pack(fill="x", expand=True)

        rerun_fit_btn = ttk.Button(
            options_frame, text="Rerun Fit", command=self._rerun_fit
        )
        rerun_fit_btn.pack(fill="x", expand=True, padx=10, pady=5)

    @property
    def keys(self):
        return ["N", "A", "x0", "y0", "sx", "sy", "theta", "z0"]

    def display(self, fit_params):
        for k, v in fit_params.items():
            if k in ["x0", "y0", "sx", "sy"]:
                v *= config.pixel_size
            elif k == "theta":
                v = np.degrees(v)
            entry = self.fit_params[k]
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, "{:.4g}".format(v))
            entry.configure(state="readonly")

    def clear(self):
        for entry in self.fit_params.values():
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.configure(state="readonly")

    def _rerun_fit(self):
        self.presenter.shot_presenter.refit_current_shot()

        
class RealtimeTab(tk.Frame):
    """Tab for real time mode."""

    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master)
        self.pack(expand=True, fill=tk.BOTH)

class AverageshotTab(tk.Frame):
    """Tab for average shot mode."""

    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master)
        self.pack(expand=True, fill=tk.BOTH)

class TofTab(tk.Frame):
    """Tab for TOF mode."""

    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master)
        self.pack(expand=True, fill=tk.BOTH)

class AtomnumberTab(tk.Frame):
    """Tab for atom number mode."""

    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master)
        self.pack(expand=True, fill=tk.BOTH)

class ThreeroiTab(tk.Frame):
    """Tab for three ROI mode."""

    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master)
        self.pack(expand=True, fill=tk.BOTH)

class ExperimentalTab(tk.Frame):
    """Tab for experimental parameters."""

    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master)
        self.pack(expand=True, fill=tk.BOTH)

class SettingsTab(tk.Frame):
    """Tab for settings."""

    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master)
        self.pack(expand=True, fill=tk.BOTH)


class LogTextBox(tk.Text):
    """Text widget for logging messages."""

    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master, **kwargs)
        self.pack(expand=True, fill=tk.BOTH)
    
class ShotInfoTable(ttk.Treeview):
    """Table for shot information."""

    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master, **kwargs)
        self.pack(expand=True, fill=tk.BOTH)

#####################################################
"""
Tkinter ScrolledText widget to pull from logging.
Quote from the below repo:
https://github.com/beenje/tkinter-logging-text-widget
https://github.com/ColumbiaWillLab/AbsorptionImaging
"""

class LogTextBox(tkst.ScrolledText):
    """Poll messages from a logging queue and display them in a scrolled text widget"""

    def __init__(self, master):
        self.master = master
        super().__init__(master, state="disabled", height=12)

        self.tag_config("INFO", foreground="black")
        self.tag_config("DEBUG", foreground="gray")
        self.tag_config("WARNING", foreground="orange")
        self.tag_config("ERROR", foreground="red")
        self.tag_config("CRITICAL", foreground="red", underline=1)
        self.pack(fill="both", expand=True)

    def display(self, msg, levelname):
        """Append log message to end of text block."""
        self.configure(state="normal")
        self.insert("end", msg + "\n", levelname)
        self.configure(state="disabled")
        self.see("end")

    def trim_log(self, num):
        """Trim log to MAX_LINES."""
        idx = float(self.index("end-1c"))
        if idx > num:
            self.configure(state="normal")
            self.delete("1.0", idx - num)
            self.configure(state="disabled")