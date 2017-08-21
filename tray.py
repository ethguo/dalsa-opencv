import cv2
import numpy as np
from matplotlib.patches import Circle, Rectangle
from yaml import safe_load, YAMLObject
from detector import CalibrationDetector

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

		self.x0 = (self.width - self.cell_width * self.cols) / 2
		self.y0 = (self.height - self.cell_height * self.rows) / 2

	def getPos(self, row, col):
		x1 = int(self.x0 + self.cell_width * col)
		y1 = int(self.y0 + self.cell_height * row)

		return x1, y1

	def getBounds(self, row, col):
		x1 = int(self.x0 + self.cell_width * col)
		y1 = int(self.y0 + self.cell_height * row)

		x2 = int(self.x0 + self.cell_width * (col + 1)) # Not x1 + self.cell_width because lose precision with int
		y2 = int(self.y0 + self.cell_height * (row + 1))

		return x1, y1, x2, y2

	def getCell(self, img, row, col):
		x1, y1, x2, y2 = self.getBounds(row, col)
		cell = img[y1:y2, x1:x2, :]
		return cell

	def drawGrid(self, ax):
		x0 = (self.width - self.cell_width * self.cols) / 2
		y0 = (self.height - self.cell_height * self.rows) / 2

		for row, col in self:
			x1, y1 = self.getPos(row, col)

			rect = Rectangle((x, y), self.cell_width, self.cell_height, alpha=1, fill=False, color=(1, 0, 1))
			ax.add_patch(rect)

	def __iter__(self):
		for row in range(self.rows):
			for col in range(self.cols):
				yield row, col


def getTrayDef(name, scale=1):
	trays_file = open("trays.yml")
	trays_data = safe_load(trays_file)

	for entry in trays_data:
		if entry["name"] == name:
			return TrayDefinition(entry, scale)

	# trays = {entry["name"]: TrayDefinition(**entry) for entry in trays_data}
	# return trays[name]