import cv2
import numpy as np
from matplotlib.figure import Figure
from time import sleep, time

from detector import SensorDetector
from preprocess import downscale
from ui import TkUI

def preprocess(img):
	return img
	# return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

def main():

	# PATH_IMAGE = "img/other/allsensors.png"
	# PATH_PATTERN = "img/other/allsensors_pattern.png"
	# DOWNSCALE = 1
	# WINDOW_NAME = "tray0"

	PATH_IMAGE = "img/lab/tray3_square.png"
	PATH_PATTERN = "img/lab/tray3_pattern.png"
	DOWNSCALE = 4
	WINDOW_NAME = "tray3"

	img = cv2.imread(PATH_IMAGE, cv2.IMREAD_GRAYSCALE)
	pattern = cv2.imread(PATH_PATTERN, cv2.IMREAD_GRAYSCALE)

	img = downscale(img, DOWNSCALE)
	pattern = downscale(pattern, DOWNSCALE)

	# img = img[:,200:]

	detector = SensorDetector(pattern, preprocess=preprocess)

	f = Figure()
	# f.set_tight_layout(True)

	ui = TkUI(WINDOW_NAME)
	ui.addTable()
	ui.addFigure(f)
	ui.addSlider("match_threshold",     0.7, 0,   1, 0.01)
	ui.addSlider("clustering_bandwidth", 40, 1, 100)

	ax1 = f.add_subplot(1, 1, 1)
	# ax2 = f.add_subplot(1, 3, 2)
	# ax3 = f.add_subplot(1, 3, 3)
	# ax4 = f.add_subplot(2, 2, 4)

	while True:

		detector.match_threshold, changed1 = ui.getSlider("match_threshold")
		detector.clustering_bandwidth, changed2 = ui.getSlider("clustering_bandwidth")

		if changed1 or changed2:
			# Stopwatch execution of detector.detect
			start_time = time()

			matches, img_proc = detector.detect(img)

			time_elapsed = time() - start_time
			ui.table.set("Time elapsed", time_elapsed)

			ui.table.set("Number of sensors", len(matches))
			ui.table.set("RSS", matches.rss)
			ui.table.set("Avg error", matches.avg_error)
			ui.table.set("Product of scores", matches.product_error)

			# Display results
			result = matches.paint(img)

			# img_proc_rgb = cv2.cvtColor(img_proc, cv2.COLOR_GRAY2RGB)
			# result_rgb = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
			# pattern_rgb = cv2.cvtColor(pattern, cv2.COLOR_GRAY2RGB)
			# pattern_proc_rgb = cv2.cvtColor(detector.pattern_proc, cv2.COLOR_GRAY2RGB)

			ax1.imshow(result, cmap="gray")
			# ax2.imshow(img_proc_rgb)
			# ax3.imshow(pattern_rgb)
			# ax3.imshow(pattern_proc_rgb)
			ui.updateFigure()

		else:
			sleep(1/60)

		ui.update()


if __name__ == '__main__':
	main()
