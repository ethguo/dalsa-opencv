from matplotlib.patches import Circle, Rectangle
from detector import CalibrationDetector
from config import loadYAML

class TrayDefinition:
	def __init__(self, data, scale=1):
		self.data = data
		self.scale = scale

		self.name = data.name
		self.rows = data.tray.rows
		self.cols = data.tray.cols

		self.width = data.tray.width * scale
		self.height = data.tray.height * scale
		self.cell_width = data.cell.width * scale
		self.cell_height = data.cell.height * scale

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
	trays_data = loadYAML("trays.yml")
	
	for data in trays_data:
		if data.name == name:
			return TrayDefinition(data, scale)
