"""Summary
"""
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TkUI:

	"""Manages Tk root and provides an interface to create sliders, 
	
	Attributes:
	    canvas (FigureCanvasTkAgg): `matplotlib.backends.backend_tkagg.FigureCanvasTkAgg` object, which draws matplotlib figures on a tkinter canvas.
	    last_values (dict): Description
	    root (tk.Tk): `Tk` root object.
	    secondary_window (tk.Toplevel): Description
	    sliders (list): Description
	    sliders_grid (TYPE): Description
	    table (TkTable): Description
	    tk_variables (dict): Description
	"""
	
	def __init__(self, label="TkUI", secondary_window=True):
		"""Summary
		
		Args:
		    label (str, optional): The window title.
		    secondary_window (bool, optional): If True, draws the table and sliders on a separate window. If False, draws the Figure, table and sliders on the same window.
		"""
		self.root = tk.Tk()
		self.root.wm_title(label)
		self.canvas = None
		self.table = None
		self.sliders = []
		self.last_values = {}
		self.tk_variables = {}

		self.secondary_window = None
		if secondary_window:
			self.secondary_window = tk.Toplevel()

		self.sliders_grid = tk.Frame(self.secondary_window or self.root)
		self.sliders_grid.pack(side=tk.BOTTOM, fill=tk.X)
		self.sliders_grid.grid_columnconfigure(1, weight=1)

	def setFigure(self, figure):
		"""Sets the matplotlib Figure to be drawn. Calling this function again will replace the figure.
		
		Args:
		    figure (matplotlib.figure.Figure): Matplotlib Figure to draw.
		"""
		self.canvas = FigureCanvasTkAgg(figure, master=self.root)
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

	def addTable(self, show_delta=True):
		"""Summary
		
		Args:
		    show_delta (bool, optional): Description
		"""
		self.table = TkTable(self.secondary_window or self.root, show_delta)

	def addSlider(self, name, initial_value=0, from_=0, to=100, resolution=1, var_type=float, **kwargs):
		"""Summary
		
		Args:
		    name (TYPE): Description
		    initial_value (int, optional): Description
		    from_ (int, optional): Description
		    to (int, optional): Description
		    resolution (int, optional): Description
		    var_type (type or str, optional): If "float" or the type float, 
		    **kwargs: Description
		
		Raises:
		    ValueError: Description
		"""
		if var_type in (int, "int"):
			tk_variable = tk.IntVar()
		elif var_type in (float, "float"):
			tk_variable = tk.DoubleVar()
		else:
			raise ValueError("var_type " + str(var_type) + " not supported.")

		tk_variable.set(initial_value)

		row = len(self.sliders)

		label = tk.Label(self.sliders_grid, text=name)
		label.grid(row=row, column=0)

		slider = tk.Scale(self.sliders_grid, variable=tk_variable, from_=from_, to=to, resolution=resolution, orient=tk.HORIZONTAL, **kwargs)
		slider.grid(row=row, column=1, sticky=tk.W+tk.E)

		entry = tk.Entry(self.sliders_grid, textvariable=tk_variable, width=10)
		entry.grid(row=row, column=2)

		self.sliders.append(slider)
		self.tk_variables[name] = tk_variable
		self.last_values[name] = None

	def getSlider(self, name):
		"""Returns value of a specified slider, and whether or not it was changed since the last call to getSlider on that slider.
		
		Args:
		    name (str or hashable): Name of slider, as defined when creating the slider.
		
		Returns:
		    TYPE: Description
		"""
		value = self.tk_variables[name].get()
		if value != self.last_values[name]:
			self.last_values[name] = value
			return value, True
		return value, False

	def setSlider(self, name, value):
		"""Summary
		
		Args:
		    name (TYPE): Description
		    value (TYPE): Description
		"""
		self.tk_variables[name].set(value)
		self.last_values[name] = None

	def update(self):
		"""GUI update. If not using mainloop(), you must call this function in a loop for a responsive GUI."""
		self.root.update()

	def updateFigure(self):
		"""Redraws matplotlib figure."""
		self.canvas.show()

	def mainloop(self):
		"""Calls Tk mainloop. Note: blocking. If not using this function, you must call update() in a loop for a responsive GUI."""
		self.root.mainloop()


class TkTable:

	"""Summary
	
	Attributes:
	    container (TYPE): Description
	    last_values (dict): Description
	    master (TYPE): Description
	    names (list): Description
	    show_delta (TYPE): Description
	    tree (TYPE): Description
	"""
	
	def __init__(self, master, show_delta=True):
		"""Summary
		
		Args:
		    master (TYPE): Description
		    show_delta (bool, optional): Description
		"""
		self.master = master
		self.show_delta = show_delta
		self.names = []

		headings = ("Name", "Value")
		if show_delta:
			headings = ("Name", "Value", "Delta")
			self.last_values = {}

		self.container = ttk.Frame(self.master)
		self.container.pack(side=tk.TOP, fill=tk.X)
		
		self.tree = ttk.Treeview(self.container, columns=headings, show="headings")
		vsb = ttk.Scrollbar(self.container, orient="vertical", command=self.tree.yview)
		hsb = ttk.Scrollbar(self.container, orient="horizontal", command=self.tree.xview)
		self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
		self.tree.grid(column=0, row=0, sticky="nsew")
		vsb.grid(column=1, row=0, sticky="ns")
		hsb.grid(column=0, row=1, sticky="ew")
		self.container.grid_columnconfigure(0, weight=1)
		self.container.grid_rowconfigure(0, weight=1)

		for col in headings:
			self.tree.heading(col, text=col.title())

	def set(self, name, value):
		"""Summary
		
		Args:
		    name (TYPE): Description
		    value (TYPE): Description
		"""
		if name not in self.names:
			self.tree.insert("", "end", name, values=(name, value))
			self.names.append(name)
			if self.show_delta:
				self.last_values[name] = value
		else:
			self.tree.set(name, "Value", value)
			if self.show_delta:
				delta = value - self.last_values[name]
				self.last_values[name] = value
				text = "%+d"%delta if type(delta) == int else "%+f"%delta
				self.tree.set(name, "Delta", text)