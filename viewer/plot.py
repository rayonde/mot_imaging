import tkinter as tk

class ImageTab(tk.Frame):
    """Tab for matplotlib figure."""

    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master)
        self.pack(expand=True, fill=tk.BOTH)

class SweepFigureTab(tk.Frame):
    """Tab for matplotlib figure."""

    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master)
        self.pack(expand=True, fill=tk.BOTH)

class Figure(tk.Frame):
    """Frame for matplotlib figure."""

    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master)
        self.pack(expand=True, fill=tk.BOTH)

class RawFigure(Figure):
    """Figure for raw data."""

    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master, self.data)
        self.pack(expand=True, fill=tk.BOTH)

class SweepFigure(Figure):
    """Figure for sweep data."""

    def __init__(self, master, data, **kwargs):
        self.master = master
        self.data = data
        super().__init__(self.master, self.data)
        self.pack(expand=True, fill=tk.BOTH)