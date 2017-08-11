import tkinter as tk

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
		self.sliders_last_value[name] = None
		self.sliders[name].set(value)

	def update(self):
		self.root.update()

	def updateFigure(self):
		self.canvas.show()

	def mainloop(self):
		self.root.mainloop()
