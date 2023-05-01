import logging
import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config import config

class MplFigure(ttk.Frame):
    """Main frame for plots"""

    def __init__(self, master):
        super().__init__(master)
        self.pack()

        self.figure = Figure(figsize=(8, 5))  # dummy figure for init
        self.canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        # self.toolbar = NavigationToolbar2Tk(canvas, master)
        # self.toolbar.update()

    def display(self, obj):
        obj.plot(self.figure)
        self.canvas.draw()
