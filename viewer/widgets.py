# Widget components for the viewer application

import tkinter as tk
import tkinter.ttk as ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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