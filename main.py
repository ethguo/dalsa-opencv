import cv2
import numpy as np
from matplotlib.figure import Figure
from time import sleep, time

from cvutil import downscale, adaptiveThreshold, aximshow
from detector import SensorDetector
from transform import getPerspectiveTransform
from ui import TkUI

def preprocess(img, block_radius=5, c=7):
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img = adaptiveThreshold(img, block_radius, c)
	return img

def main():

	# PATH_IMAGE = "img/other/allsensors.png"
	# PATH_PATTERN = "img/other/allsensors_pattern.png"
	# DOWNSCALE = 1
	# WINDOW_NAME = "tray0"

	PATH_IMAGE = "img/calibration/img.png"
	PATH_PATTERN = "img/calibration/img_pattern.png"
	DOWNSCALE = 1
	WINDOW_NAME = "calibration"

	img = cv2.imread(PATH_IMAGE, cv2.IMREAD_COLOR)
	pattern = cv2.imread(PATH_PATTERN, cv2.IMREAD_COLOR)

	img = downscale(img, DOWNSCALE)
	pattern = downscale(pattern, DOWNSCALE)

	# img = img[:,200:]

	detector = SensorDetector()

	f = Figure()
	# f.set_tight_layout(True)

	ui = TkUI(WINDOW_NAME)
	ui.addTable()
	ui.addFigure(f)
	ui.addSlider("match_threshold",     0.60, 0,   1, 0.01)
	ui.addSlider("clustering_bandwidth", 40, 1, 100)
	ui.addSlider("block_radius", 35, 1, 50, 1, int)
	ui.addSlider("c", 20, -50, 50, 1, int)

	ax1 = f.add_subplot(1, 2, 1)
	ax2 = f.add_subplot(1, 2, 2)
	# ax3 = f.add_subplot(1, 3, 3)
	# ax4 = f.add_subplot(2, 2, 4)

	while True:

		detector.match_threshold, changed1 = ui.getSlider("match_threshold")
		detector.clustering_bandwidth, changed2 = ui.getSlider("clustering_bandwidth")
		block_radius, changed3 = ui.getSlider("block_radius")
		c, changed4 = ui.getSlider("c")

		if any((changed1, changed2, changed3, changed4)):
			img_proc = preprocess(img, block_radius, c)
			pattern_proc = preprocess(pattern, block_radius, c)

			# Stopwatch execution of detector.detect
			t0 = time()

			matches = detector.detect(img_proc, pattern_proc)

			ui.table.set("Detector time", time() - t0)

			if matches:
				if len(matches) == 4:
					ui.table.set("Matches", np.array(matches))
					t1 = time()

					transform = getPerspectiveTransform(img, np.array(matches), (400, 660))

					result = transform(img)
					print(img.shape, img.dtype)

					ui.table.set("Transform matrix", transform.matrix)
					ui.table.set("Transform time", time() - t1)

					aximshow(ax1, img)
					aximshow(ax2, result)
					ui.updateFigure()

				# Display results
				img = matches.paint(img)

			# img_proc_rgb = cv2.cvtColor(img_proc, cv2.COLOR_BGR2RGB)
				# result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
			# pattern_rgb = cv2.cvtColor(pattern, cv2.COLOR_BGR2RGB)
			# pattern_proc_rgb = cv2.cvtColor(pattern_proc, cv2.COLOR_BGR2RGB)

		else:
			sleep(1/60)

		ui.update()


if __name__ == '__main__':
	main()
