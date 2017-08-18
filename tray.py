import cv2
import numpy as np
from matplotlib.patches import Circle, Rectangle
from yaml import safe_load, YAMLObject

class TrayDefinition:
	def __init__(self, entry, scale=1):
		self.entry = entry
		self.scale = scale

		self.name = entry["name"]
		self.cols = entry["tray"]["cols"]
		self.rows = entry["tray"]["rows"]

		self.width = entry["tray"]["width"] * scale
		self.height = entry["tray"]["height"] * scale
		self.cell_width = entry["cell"]["width"] * scale
		self.cell_height = entry["cell"]["height"] * scale

		self.width_unscaled = entry["tray"]["width"]
		self.height_unscaled = entry["tray"]["height"]
		self.cell_width_unscaled = entry["cell"]["width"]
		self.cell_height_unscaled = entry["cell"]["height"]

def getTrayDef(name, scale=1):
	trays_file = open("trays.yml")
	trays_data = safe_load(trays_file)

	for entry in trays_data:
		if entry["name"] == name:
			return TrayDefinition(entry, scale)

	# trays = {entry["name"]: TrayDefinition(**entry) for entry in trays_data}
	# return trays[name]


def drawGrid(ax, tray):
	x0 = (tray.width - tray.cell_width * tray.cols) / 2
	y0 = (tray.height - tray.cell_height * tray.rows) / 2

	for j in range(tray.rows):
		for i in range(tray.cols):
			x = int(x0 + tray.cell_width * i)
			y = int(y0 + tray.cell_height * j)

			rect = Rectangle((x, y), tray.cell_width, tray.cell_height, alpha=1, fill=False, color=(1, 0, 1))
			ax.add_patch(rect)

def processTray(img, tray):
	pass
