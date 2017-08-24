#!/usr/bin/env python3
import logging

from matplotlib.figure import Figure

from find_sensors import calibrate
from find_sensors import detectSensors
from find_sensors import loadImage
from tray import getTrayDef
from ui import axPaint
from ui import axShowImage
from ui import TkUI
from yaml_config import loadYAML


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
