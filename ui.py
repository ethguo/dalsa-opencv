import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TkUI:
	def __init__(self, label="TkUI"):
		self.root = tk.Tk()
		self.canvas = None
		self.sliders = {}
		self.sliders_last_value = {}
		self.sliders_grid = tk.Frame(self.root)

		self.sliders_grid.pack(side=tk.BOTTOM, fill=tk.X)
		self.sliders_grid.grid_columnconfigure(1, weight=1)

		self.root.wm_title(label)

	def addFigure(self, figure):
		self.canvas = FigureCanvasTkAgg(figure, master=self.root)
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

	def addSlider(self, name, initial_value=0, from_=0, to=100, resolution=1, **kwargs):
		row = len(self.sliders)

		label = tk.Label(self.sliders_grid, text=name)
		label.grid(row=row, column=0)

		slider = tk.Scale(self.sliders_grid, from_=from_, to=to, resolution=resolution, orient=tk.HORIZONTAL, **kwargs)
		slider.set(initial_value)
		slider.grid(row=row, column=1, sticky=tk.W+tk.E)

		self.sliders[name] = slider
		self.sliders_last_value[name] = None

	def getSlider(self, name):
		value = self.sliders[name].get()
		changed = value != self.sliders_last_value[name]
		self.sliders_last_value[name] = value
		return value, changed

	def setSlider(self, name, value):
		self.sliders[name].set(value)
		self.sliders_last_value[name] = None

	def update(self):
		self.root.update()

	def updateFigure(self):
		self.canvas.show()

	def mainloop(self):
		self.root.mainloop()

class TkTable:
	def __init__(self, master):
		self.tree = ttk.Treeview(master)
		



# class MultiColumnListbox:
# 	def __init__(self, headers):
# 		self.tree = None
# 		self.headers = headers
# 		self._setup_widgets()
# 		self._build_tree()

# 	def _setup_widgets(self):
# 		s = "click on header to sort by that column	to change width of column drag boundary"
# 		msg = ttk.Label(wraplength="4i", justify="left", anchor="n", padding=(10, 2, 10, 6), text=s)
# 		msg.pack(fill='x')
# 		container = ttk.Frame()
# 		container.pack(fill='both', expand=True)
# 		# create a treeview with dual scrollbars
# 		self.tree = ttk.Treeview(columns=self.headers, show="headings")
# 		vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
# 		hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
# 		self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
# 		self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
# 		vsb.grid(column=1, row=0, sticky='ns', in_=container)
# 		hsb.grid(column=0, row=1, sticky='ew', in_=container)
# 		container.grid_columnconfigure(0, weight=1)
# 		container.grid_rowconfigure(0, weight=1)

# 	def _build_tree(self):
# 		for col in self.headers:
# 			self.tree.heading(col, text=col.title(), command=lambda c=col: sortby(self.tree, c, 0))
# 			# adjust the column's width to the header string
# 			self.tree.column(col, width=tkFont.Font().measure(col.title()))

# 		for item in car_list:
# 			self.tree.insert('', 'end', values=item)
# 			# adjust column's width if necessary to fit each value
# 			for index, value in enumerate(item):
# 				col_w = tkFont.Font().measure(value)
# 				if self.tree.column(self.headers[index],width=None)<col_w:
# 					self.tree.column(self.headers[index], width=col_w)