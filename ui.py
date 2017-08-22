import numpy as np
import tkinter as tk
import tkinter.ttk as ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def axShowImage(ax, img, cmap="gray"):
	ax.clear()
	if img.ndim == 3 and img.shape[2] == 3:
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		ax.imshow(img)
	else:
		ax.imshow(img, cmap=cmap)

def axPaint(ax, matches):
	if matches:
		matches.axPaint(ax)
	else:
		logging.warning("Cannot axPaint: No matches")

class TkUI:
	def __init__(self, figure, label="TkUI", secondary_window=True, table_show_delta=True):
		self.root = tk.Tk()
		self.root.wm_title(label)
		self.canvas = None
		self.table = None

		self.secondary_window = None
		if secondary_window:
			self.secondary_window = tk.Toplevel()

		self.canvas = FigureCanvasTkAgg(figure, master=self.root)
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

		self.sliders = TkSliderManager(self.secondary_window or self.root)
		self.table = TkTable(self.secondary_window or self.root, table_show_delta)

	# Tkinter/TkAgg wrappers
	def update(self):
		self.root.update()

	def updateFigure(self):
		self.canvas.show()

	def mainloop(self):
		windows = int(secondary_window)
		self.root.mainloop(windows)

	# TkSliderManager/TkTable wrappers
	def addSlider(self, *args, **kwargs):
		self.sliders.add(*args, **kwargs)

	def getSlider(self, name):
		return self.sliders.get(name)

	def setSlider(self, name, value):
		self.sliders.set(name, value)

	def setTableRow(self, name, value):
		self.table.set(name, value)


class TkSliderManager:
	def __init__(self, master):
		self.master = master
		self.tk_variables = {}
		self.last_values = {}

		self.container = tk.Frame(self.master)
		self.container.pack(side=tk.BOTTOM, fill=tk.X)
		self.container.grid_columnconfigure(1, weight=1)

	# var_type is int or float
	def add(self, name, initial_value=0, from_=0, to=100, resolution=1, var_type=None, **kwargs):
		if var_type:
			if var_type in (int, "int"):
				tk_variable = tk.IntVar()
			elif var_type in (float, "float"):
				tk_variable = tk.DoubleVar()
			else:
				raise ValueError("var_type " + str(var_type) + " not supported.")
		else:
			if type(initial_value) is float \
					or type(from_) is float \
					or type(to) is float \
					or type(resolution) is float:
				tk_variable = tk.DoubleVar()
			else:
				tk_variable = tk.IntVar()

		tk_variable.set(initial_value)

		row = len(self.tk_variables)

		label = tk.Label(self.container, text=name)
		label.grid(row=row, column=0, sticky=tk.N+tk.E)

		slider = tk.Scale(self.container, variable=tk_variable, from_=from_, to=to, resolution=resolution, orient=tk.HORIZONTAL, **kwargs)
		slider.grid(row=row, column=1, sticky=tk.W+tk.E)

		entry = tk.Entry(self.container, textvariable=tk_variable, width=10)
		entry.grid(row=row, column=2)

		self.tk_variables[name] = tk_variable
		self.last_values[name] = None

	def get(self, name):
		"""Returns value, and whether or not it was changed since last get."""
		value = self.tk_variables[name].get()
		if value != self.last_values[name]:
			self.last_values[name] = value
			return value, True
		return value, False

	def set(self, name, value):
		self.tk_variables[name].set(value)
		self.last_values[name] = None


class TkTable:
	def __init__(self, master, show_delta=True):
		self.master = master
		self.show_delta = show_delta
		self.names = set()

		headings = ("Name", "Value")
		if show_delta:
			headings = ("Name", "Value", "Delta")
			self.last_values = {}

		self.container = ttk.Frame(self.master)
		self.container.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
		
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

		self.tree.column("Name", stretch=False)
		if show_delta:
			self.tree.column("Delta", stretch=False)

		self.tree.tag_configure("ndarray_line", font="Courier 9 bold")


	def set(self, name, value):
		if isinstance(value, np.ndarray):
			self._insertArray(name, value)

		else:
			if name not in self.names:
				self.tree.insert("", "end", name, values=(name, value))
				self.names.add(name)
			else:
				self.tree.set(name, "Value", value)
				if self.show_delta:
					delta = value - self.last_values[name]
					text = "%+d"%delta if type(delta) is int else "%+f"%delta
					self.tree.set(name, "Delta", text)

		self.last_values[name] = value

	def _insertArray(self, name, array):
		value0 = "ndarray(%s, %s)" % (array.shape, array.dtype)

		if name not in self.names:
			self.tree.insert("", "end", name, values=(name, value0), open=True)
			self.names.add(name)
		elif np.any(array != self.last_values[name]):
			self.tree.set(name, "Value", value0)

			old_lines = self.tree.get_children(name)
			self.tree.delete(*old_lines)
		else:
			return

		lines = str(array).split("\n")
		for i, line in enumerate(lines):
			self.tree.insert(name, "end", name + "~" + str(i), values=("", line), tags="ndarray_line")
