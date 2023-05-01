import tkinter as tk
from tkinter import ttk

# create the main window
root = tk.Tk()
root.geometry('400x300')
root.title('Tabbed Interface')

# create the Notebook widget
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# create the first tab page
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text='Tab 1')

# add content to the first tab page
# label1 = tk.Label(tab1, text='This is the first tab page')
# label1.pack(pady=10, padx=10)

# create a second tab page
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text='Tab 2')

# add content to the second tab page
# label2 = tk.Label(tab2, text='This is the second tab page')
# label2.pack(pady=10, padx=10)

# create a third tab page
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text='Tab 3')

# add content to the third tab page
# label3 = tk.Label(tab3, text='This is the third tab page')
# label3.pack(pady=10, padx=10)

# start the main event loop
root.mainloop()

