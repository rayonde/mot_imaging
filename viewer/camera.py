import tkinter as tk
from tkinter import ttk

class CameraTab(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller
    
        # Create a left cloumn
        self.left_frame = ttk.LabelFrame(self, text="Camera Settings")
        self.left_frame.pack(side="left", fill="both", expand=True)
        
        blank_var1 = tk.StringVar(value="test")
        tk.Label(self.left_frame, text="Blank 1: ").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(self.left_frame, textvariable=blank_var1).grid(row=0, column=1, padx=5, pady=5)

        blank_var2 = tk.StringVar(value="test2")
        tk.Label(self.left_frame, text="Blank 2: ").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(self.left_frame, textvariable=blank_var2).grid(row=1, column=1, padx=5, pady=5)

        blank_var3 = tk.StringVar(value="test3")
        tk.Label(self.left_frame, text="Blank 3: ").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(self.left_frame, textvariable=blank_var3).grid(row=2, column=1, padx=5, pady=5)

        blank_var4 = tk.StringVar(value="test4")
        tk.Label(self.left_frame, text="Blank 4: ").grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(self.left_frame, textvariable=blank_var4).grid(row=3, column=1, padx=5, pady=5)





        # Create a right cloumn
        self.right_frame = ttk.Frame(self)
        #self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.right_frame.pack(side="right", fill="both", expand=True)
        
        self.setting_frame = ttk.LabelFrame(self.right_frame, text="Test Settings")
        self.setting_frame.pack(side=tk.TOP, fill="both", padx=5, pady=5)

        self.update_button = tk.Button(self.right_frame, text="Update Configurations")
        self.update_button.pack(side=tk.TOP, fill="both", padx=5, pady=5)

        self.reset_button = tk.Button(self.right_frame, text="Reset Camera")
        self.reset_button.pack(side=tk.TOP, fill="both", padx=5, pady=5)

        self.start_button = tk.Button(self.right_frame, text="Start Acquisition")
        self.start_button.pack(side=tk.TOP, fill="both", padx=5, pady=5)
        

    