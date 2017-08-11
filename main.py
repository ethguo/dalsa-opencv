import cv2
import numpy as np
from matplotlib.figure import Figure
from time import sleep, time

from detector import SensorDetector
from preprocess import downscale
from ui import TkUI

def main():

	PATH_IMAGE = "img/lab/tray3.png"
	PATH_PATTERN = "img/lab/tray3_pattern.png"
	DOWNSCALE = 1
	WINDOW_NAME = "tray0"

	# PATH_IMAGE = "img/lab/tray3_square.png"
	# PATH_PATTERN = "img/lab/tray3_pattern.png"
	# DOWNSCALE = 4
	# WINDOW_NAME = "tray3"

	img = cv2.imread(PATH_IMAGE, cv2.IMREAD_COLOR)
	pattern = cv2.imread(PATH_PATTERN, cv2.IMREAD_COLOR)

	img = downscale(img, DOWNSCALE)
	pattern = downscale(pattern, DOWNSCALE)

	# img = img[:,200:]

	detector = SensorDetector(pattern)

	# onChange = lambda x: None # Do nothing function

	# cv2.namedWindow(WINDOW_NAME)
	# cv2.createTrackbar("match_threshold_percent", WINDOW_NAME, 70, 100, onChange)
	# cv2.createTrackbar("clustering_bandwidth", WINDOW_NAME, 40, 100, onChange) #permille

	f = Figure()
	# f.set_tight_layout(True)

	ui = TkUI()
	ui.addFigure(f)
	ui.addSlider("match_threshold_percent", 0.7, 0, 1, 0.01)
	ui.addSlider("clustering_bandwidth", 40, 1, 100)

	ax1 = f.add_subplot(1, 2, 1)
	ax2 = f.add_subplot(1, 2, 2)
	# ax3 = f.add_subplot(2, 2, 3)
	# ax4 = f.add_subplot(2, 2, 4)

	while True:
		# Stopwatch execution of detector.detect
		start_time = time()

		detector.match_threshold, changed1 = ui.getSlider("match_threshold_percent")
		detector.clustering_bandwidth, changed2 = ui.getSlider("clustering_bandwidth")

		if changed1 or changed2:
			matches = detector.detect(img)

			# Display results
			result = matches.paint(img)

			img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
			result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

			ax1.imshow(img_rgb)
			ax2.imshow(result_rgb)
			ui.updateFigure()

		else:
			sleep(1/60)

		ui.update()

		time_elapsed = time() - start_time
		print(time_elapsed)


if __name__ == '__main__':
	main()
