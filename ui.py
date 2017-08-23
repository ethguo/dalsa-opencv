"""This module includes classes which construct and manage UIs, as well as convenience functions for drawing on matplotlib `Axes`."""
import cv2
import logging
import numpy as np
import tkinter as tk
import tkinter.ttk as ttk

# These lines are required, in this order, to make matplolib not complain. Don't try moving them around.
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# Any additional imports from matplotlib should go here.

def axShowImage(ax, img, cmap="gray"):
	"""Wrapper around matplotlib's `ax.imshow`, automatically detects whether the image is color or grayscale and behaves accordingly.
	
	Args:
	    ax (matplotlib.axes.Axes): `Axes` to draw image on.
	    img (numpy.ndarray): Color or grayscale image.
	    cmap (str, optional): If image is grayscale, the matplotlib colormap to use.
	"""
	ax.clear()
	if img.ndim == 3 and img.shape[2] == 3:
		# If it's a color image, convert it from BGR (cv2) to RGB (matplotlib).
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		ax.imshow(img)
	else:
		ax.imshow(img, cmap=cmap)

def axPaint(ax, matches):
	"""Calls `matches.axPaint` or gracefully handles Nones.
	
	Args:
	    ax (matplotlib.axes.Axes): `Axes` passed to `matches.axPaint`
	    matches (detector_result.DetectorResult): `DetectorResult` object to paint. Will warn if None.
	"""
	if matches:
		matches.axPaint(ax)
	else:
		logging.warning("Cannot axPaint: No matches")

class TkUI:	
	"""Manages Tk root object, FigureCanvasTkAgg object, TkSliderManager and TkTable objects.
	
	Args:
	    figure (matplotlib.figure.Figure): Figure (can have multiple subplots) to draw on the main window.
	    title (str, optional): Window title.
	    secondary_window (bool, optional): If False, draws the Figure, sliders and TkTable on the same window. If True (default), draws the sliders and TkTable on a separate window.
	    table_show_delta (bool, optional): Passed on to TkTable.
	"""
	def __init__(self, figure, title="TkUI", secondary_window=True, table_show_delta=True):
		self.root = tk.Tk()
		self.root.wm_title(title)

		# If secondary_window, create a new window (Toplevel).
		self.secondary_window = tk.Toplevel() if secondary_window else None

		# Create the FigureCanvasTkAgg object, which draws a matplotlib figure on a tkinter canvas.
		self.canvas = FigureCanvasTkAgg(figure, master=self.root)
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

		# Creates a TkSliderManager and TkTable.
		self.sliders = TkSliderManager(self.secondary_window or self.root)
		self.table = TkTable(self.secondary_window or self.root, table_show_delta)

	# Tkinter/TkAgg wrappers
	def update(self):
		"""GUI update. If not using mainloop(), you must call this function in a loop for a responsive GUI."""
		self.root.update()

	def updateFigure(self):
		"""Redraws matplotlib figure."""
		self.canvas.show()

	def mainloop(self):
		"""Calls Tkinter's mainloop. Note: blocking. If not using this function, you must call update() in a loop for a responsive GUI."""
		self.root.mainloop()

	# TkSliderManager/TkTable wrappers
	def addSlider(self, *args, **kwargs):
		"""Creates a slider through the `TkSliderManager`. See `TkSliderManager.add` for documentation."""
		self.sliders.add(*args, **kwargs)

	def getSlider(self, name):
		"""Gets the current value of a slider. See `TkSliderManager.get` for documentation."""
		return self.sliders.get(name)

	def getSliderChanged(self, name):
		"""Gets the current value of a slider, and whether it was changed. See `TkSliderManager.getChanged` for documentation."""
		return self.sliders.getChanged(name)

	def setSlider(self, name, value):
		"""Sets the value of a slider. See `TkSliderManager.set` for documentation."""
		self.sliders.set(name, value)

	def setTableRow(self, name, value):
		"""Creates and/or sets the value of a table entry. See `TkTable.set` for documentation."""
		self.table.set(name, value)


class TkSliderManager:
	"""Manages multiple Tkinter sliders (`Scale`s).
	
	Args:
	    master (tkinter.Widget): Parent widget.
	"""
	def __init__(self, master):
		self.master = master
		self.tk_variables = {}
		self.last_values = {}

		# Create a Frame to contain all the sliders
		self.container = tk.Frame(self.master)
		self.container.pack(side=tk.BOTTOM, fill=tk.X)
		self.container.grid_columnconfigure(1, weight=1)

	def add(self, name, initial_value=0, from_=0, to=100, resolution=1, callback=None, var_type=None, **kwargs):
		"""Creates a `tkinter.Scale` slider and other supporting widgets.
		
		Args:
		    name (str): The name of the slider. This acts as both the displayed label and the dictionary key.
		    initial_value (int, optional): The initial value of the slider (Default 0).
		    from_ (int, optional): The lower bound of the slider (Default 0).
		    to (int, optional): The upper bound of the slider (Default 100).
		    resolution (int, optional): The step size of the slider (Default 1).
		    callback (callable, optional): A function to be called every time the value changes.
		    var_type (type or str, optional): If `int` or `"int"`, use a `tkinter.IntVar`. If `float` or `"float"`, use a `tkinter.DoubleVar`. If not specified, determines the type based on the types of the numerical arguments provided.
		    **kwargs: Passed on to the `tkinter.Scale` constructor.
		"""
		# Determine the correct type of tkinter Variable to use.
		if var_type:
			if var_type in (int, "int"):
				tk_variable = tk.IntVar()
			elif var_type in (float, "float"):
				tk_variable = tk.DoubleVar()
			else:
				raise ValueError("var_type " + str(var_type) + " not supported.")
		else: # If var_type not specified, if any of the numerical parameters were floats, then use a DoubleVar.
			if type(initial_value) is float \
					or type(from_) is float \
					or type(to) is float \
					or type(resolution) is float:
				tk_variable = tk.DoubleVar()
			else: # Otherwise, use an IntVar.
				tk_variable = tk.IntVar()

		tk_variable.set(initial_value)
		if callback:
			tk_variable.trace("w", callback)

		# Use the next unoccupied row.
		row = len(self.tk_variables)

		# Create a text label displaying the slider's name.
		label = tk.Label(self.container, text=name)
		label.grid(row=row, column=0, sticky=tk.N+tk.E)

		# Create the Scale widget.
		slider = tk.Scale(self.container, variable=tk_variable, from_=from_, to=to, resolution=resolution, orient=tk.HORIZONTAL, **kwargs)
		slider.grid(row=row, column=1, sticky=tk.W+tk.E)

		# Create a textbox (Entry) widget, allowing keyboard entry of values.
		entry = tk.Entry(self.container, textvariable=tk_variable, width=10)
		entry.grid(row=row, column=2)

		self.tk_variables[name] = tk_variable
		self.last_values[name] = None

	def get(self, name):
		"""Gets the current value of a slider."""
		return self.tk_variables[name].get()

	def getChanged(self, name):
		"""Gets the current value of a slider, and whether or not it was changed since the last get.
		
		Args:
		    name (str): Name of slider.
		
		Returns:
		    int or float: Value of slider.
		    boolean: Whether the value was changed since the last call to getSlider on that slider.
		"""
		value = self.tk_variables[name].get()
		if value != self.last_values[name]:
			self.last_values[name] = value
			return value, True
		return value, False

	def set(self, name, value):
		"""Sets the value of a slider. Resets the slider so that the next call to `get` will definitely return isChanged = `True`.
		
		Args:
		    name (str): Name of slider.
		    value (int or float): New value of slider.
		"""
		self.tk_variables[name].set(value)
		self.last_values[name] = None


class TkTable:
	"""A table (`ttk.Treeview`) that can be used to display any updating values.

	Args:
	    master (tkinter.Widget): Parent widget.
	    show_delta (bool, optional): If True, displays a "Delta" column that calculates how much each value changes.
	"""
	def __init__(self, master, show_delta=True):
		self.master = master
		self.show_delta = show_delta
		self.names = set()

		headings = ("Name", "Value")
		if show_delta:
			headings = ("Name", "Value", "Delta")
			self.last_values = {}

		# Create a Frame to contain everything else.
		self.container = ttk.Frame(self.master)
		self.container.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

		self.container.grid_columnconfigure(0, weight=1)
		
		# Create a Treeview to display the table.
		self.tree = ttk.Treeview(self.container, columns=headings, show="headings")
		self.tree.grid(column=0, row=0, sticky="nsew")

		# Create a vertical scrollbar.
		scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.tree.yview)
		self.tree.configure(yscrollcommand=scrollbar.set)
		scrollbar.grid(column=1, row=0, sticky="ns")
		
		for col in headings:
			self.tree.heading(col, text=col.title())

		self.tree.column("Name", stretch=False)
		if show_delta:
			self.tree.column("Delta", stretch=False)

		# Set a format tag for displaying ndarrays in a fixed-width font.
		self.tree.tag_configure("ndarray_line", font="Courier 9 bold")


	def set(self, name, value):
		"""Sets the value of an entry, creating it if it doesn't exist.
		
		Args:
		    name (str): The name of the entry. This acts as both the displayed label and the dictionary key.
		    value (any): New value for the entry. If value is an `numpy.ndarray`, will be displayed in multiple lines (collapsible).
		"""
		if isinstance(value, np.ndarray):
			self._insertArray(name, value) # ndarrays get special treatment

		else:
			if name not in self.names:
				self.tree.insert("", "end", name, values=(name, value))
				self.names.add(name)
			else:
				self.tree.set(name, "Value", value)
				if self.show_delta:
					try:
						delta = value - self.last_values[name]
						if isinstance(delta, int):
							text = "%+d" % delta
						else:
							text = "%+f" % delta
						self.tree.set(name, "Delta", text)
					except TypeError: # Probably a non-numerical type
						pass

		self.last_values[name] = value

	def _insertArray(self, name, array):
		header = "ndarray(%s, %s)" % (array.shape, array.dtype) # Text displayed on the first line

		if name not in self.names:
			# If it's a new entry, create the header line.
			self.tree.insert("", "end", name, values=(name, header), open=True)
			self.names.add(name)
		elif np.any(array != self.last_values[name]):
			# If it's an existing entry but the value has changed, delete all the old lines.
			self.tree.set(name, "Value", header)

			old_lines = self.tree.get_children(name)
			self.tree.delete(*old_lines)
		else:
			# If it hasn't been updated, skip everything else.
			return

		# Create a new lines as children of the header line.
		lines = str(array).split("\n")
		for i, line in enumerate(lines):
			self.tree.insert(name, "end", name + "~" + str(i), values=("", line), tags="ndarray_line")
