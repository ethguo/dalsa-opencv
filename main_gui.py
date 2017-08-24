#!/usr/bin/env python3
"""This file performs all the `find_sensors` operations and also includes an example of how to integrate UI elements (sliders and table entries)."""
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
		# Set up logging.
		logging.basicConfig(level=logging.DEBUG)

		self.params = loadYAML("parameters.yml")
		self.tray = getTrayDef(**self.params.tray)

		# Create matplotlib figure and Axes.
		self.f = Figure()
		self.ax = self.f.add_subplot(111)

		self.ui = TkUI(self.f, "main") # Create TkUI.

		self.ui.addSlider("test", callback=self.onChange) # Add an example slider.

		self.update() # Run all the important stuff.

		self.ui.mainloop() # Allow the UI to do it's thing and listen for events (like the slider's onChange).

	def onChange(self, *args):
		# When the slider is changed, write the new value to a table entry.
		value = self.ui.getSlider("test")
		self.ui.setTableRow("test", value)

		self.update() # In theory, updating the slider would update parameters which would require re-running calibrate and/or detectSensors.

	def update(self):
		# Do all the important stuff.
		img = loadImage(**self.params.image)
		self.img = calibrate(img, self.params, self.tray)
		self.matches, self.results = detectSensors(self.img, self.params, self.tray)

		self.draw() # Redraw the matplotlib display, because (in theory) the results may have changed.

	def draw(self):
		# Redraw the image and results on the matplotlib Axes.
		axShowImage(self.ax, self.img)
		self.tray.drawGrid(self.ax, self.matches)
		for result in self.results:
			axPaint(self.ax, result)


if __name__ == "__main__":
	Main()
