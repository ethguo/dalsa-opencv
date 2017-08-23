import logging
from matplotlib.figure import Figure
from time import sleep, time

from config import loadYAML
from tray import getTrayDef
from ui import TkUI, axShowImage, axPaint
from utils import loadImage, calibrate, detectSensors

class Main:
	def __init__(self):
		logging.basicConfig(level=logging.DEBUG)

		self.params = loadYAML("parameters.yml")
		self.tray = getTrayDef(**self.params.tray)

		self.f = Figure()
		self.ui = TkUI(self.f, "main")
		self.ax = self.f.add_subplot(111)

		self.ui.addSlider("test", callback=self.onChange)

		self.update()
		self.ui.mainloop()

	def onChange(self, *args):
		value = self.ui.getSlider("test")
		self.ui.setTableRow("test", value)

		self.update()

	def update(self):
		img = loadImage(**self.params.image)
		self.img = calibrate(img, self.params, self.tray)
		self.results = detectSensors(self.img, self.params, self.tray)

		self.draw()

	def draw(self):
		axShowImage(self.ax, self.img)
		self.tray.drawGrid(self.ax, self.results)


if __name__ == "__main__":
	Main()
