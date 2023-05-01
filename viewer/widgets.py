# Widget components for the viewer application

import tkinter as tk
import tkinter.ttk as ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.scrolledtext as tkst


class SingleshotTab(tk.Frame):
    """Tab for single shot mode."""

    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master)
        self.pack(expand=True, fill=tk.BOTH)

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