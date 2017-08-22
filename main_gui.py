import logging
from matplotlib.figure import Figure
from time import sleep, time

from config import loadYAML
from tray import getTrayDef
from ui import TkUI, axShowImage, axPaint
from utils import loadImage, calibrate, detectSensors

def draw(img, results, tray):
	f = Figure()
	ui = TkUI(f, "main")
	ax = f.add_subplot(111)
	axShowImage(ax, img)
	tray.drawGrid(ax, results)
	ui.mainloop()

def main():
	logging.basicConfig(level=logging.DEBUG)

	params = loadYAML("parameters.yml")
	tray = getTrayDef(**params.tray)

	img = loadImage(**params.image)
	img = calibrate(img, params, tray)
	results = detectSensors(img, params, tray)

	draw(img, results, tray)

	print(results)

if __name__ == "__main__":
	main()
