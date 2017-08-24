"""This module includes a class and a public function for loading trays from config files and working with them."""
import numpy as np
from matplotlib.patches import Circle, Rectangle

from detector import CalibrationDetector
from yaml_config import loadYAML


_trays_data = None


class TrayDefinition:
	"""Represents a tray spec loaded from a YAML config file. Provides convenience methods for working with the tray's rows/cols and x/y positions.
	
	Note:
	    `height` doesn't have to equal `cell_height * rows`, if `height` > `cell_height * rows`, the cells will be centered within the larger plane.
	    Likewise for `width` and `cell_width * cols`.
	
	Attributes:
	    cell_height (float): The height of each cell in the tray, i.e. the vertical distance from the center of one cell to the next.
	    cell_width (float): The width of each cell in the tray, i.e. the horizontal distance from the center of one cell to the next.
	    cols (int): Number of columns.
	    height (float): Height of entire tray, including all space outside of the cells; i.e. the vertical distance between calibration points.
	    name (str): Name of tray.
	    rows (int): Number of rows.
	    scale (float): Factor by which to scale all heights and widths.
	    width (float): Width of entire tray, including all space outside of the cells; i.e. the horizontal distance between calibration points.
	
	Args:
	    data (yaml_config.YAMLDict): Data loaded from YAML config file.
	    scale (float, optional): Factor by which to scale all heights and widths.
	"""
	def __init__(self, data, scale=1):
		self.scale = scale

		self.name = data.name
		self.rows = data.tray.rows
		self.cols = data.tray.cols

		self.width = data.tray.width * scale
		self.height = data.tray.height * scale
		self.cell_width = data.cell.width * scale
		self.cell_height = data.cell.height * scale

		self._x0 = (self.width - self.cell_width * self.cols) / 2
		self._y0 = (self.height - self.cell_height * self.rows) / 2

	def getPos(self, row, col):
		"""Gets the top-left corner of the tray cell at (row, col).
		
		Args:
		    row (int): The row of the cell.
		    col (int): The column of the cell.
		
		Returns:
		    (int, int): (x, y) of top-left corner.
		"""
		x1 = int(self._x0 + self.cell_width * col)
		y1 = int(self._y0 + self.cell_height * row)
		return x1, y1

	def getBounds(self, row, col):
		"""Gets the top-left and bottom-right corners of the tray cell at (row, col).
		
		Args:
		    row (int): The row of the cell.
		    col (int): The column of the cell.
		
		Returns:
		    (int, int, int, int): (x1, y1, x2, y2), where (x1, y1) is the top-left corner and (x2, y2) is the bottom-right corner of the cell.
		"""
		x1, y1 = self.getPos(row, col)
		x2, y2 = self.getPos(row + 1, col + 1) # You can't use (x2, y2) = (x1 + self.cell_width, y1 + self.cell_height) because it is converted to an int in getPos.
		return x1, y1, x2, y2

	def getCell(self, img, row, col):
		"""Given the image of the tray, extracts the sub-image of a single cell at (row, col).
		
		Args:
		    img (numpy.ndarray): The calibrated/transformed image of the tray.
		    row (int): The row of the cell.
		    col (int): The column of the cell.
		
		Returns:
		    numpy.ndarray: The image of the specified cell.
		"""
		x1, y1, x2, y2 = self.getBounds(row, col)
		cell = img[y1:y2, x1:x2, :]
		return cell

	def drawGrid(self, ax, labels=None):
		"""Display each cell's location on the given `ax` using matplotlib patches.
		
		Args:
		    ax (matplotlib.axes.Axes): `Axes` to paint onto.
		    labels (numpy.ndarray, optional): If provided, use a different color for each distinct value. Must match the shape (tray.row, tray.col). 
		"""
		x0 = (self.width - self.cell_width * self.cols) / 2
		y0 = (self.height - self.cell_height * self.rows) / 2

		colors = {}
		if labels is not None:
			for index, label in enumerate(np.unique(labels)):
				colors[label] = "C" + str(index)

		color = "b"
		for row, col in self:
			x1, y1 = self.getPos(row, col)
			if labels is not None:
				label = labels[row, col]
				color = colors[label]
			rect = Rectangle((x1+1, y1+1), self.cell_width-2, self.cell_height-2, alpha=1, fill=False, color=color)
			ax.add_patch(rect)

	def __iter__(self):
		"""Allows the pattern::

		    for row, col in tray:
		        ...

		Where `tray` is an instance of TrayDefinition, i.e. from `getTrayDef`.
		"""
		for row in range(self.rows):
			for col in range(self.cols):
				yield row, col


def getTrayDef(name, scale=1):
	global _trays_data
	"""Loads a tray by name from the YAML config file.
	
	Args:
	    name (str): The name of the tray in the config file.
	    scale (float, optional): The factor by which to scale all heights and widths.
	
	Returns:
	    TrayDefinition: Creates a TrayDefinition object with the appropriate scale.
	"""
	if _trays_data is None:
		_trays_data = loadYAML("trays.yml")
	
	for data in _trays_data:
		if data.name == name:
			return TrayDefinition(data, scale)
