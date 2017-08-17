import cv2
import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle
from time import sleep, time

from cvutil import downscale, adaptiveThreshold, aximshow
from detector import SensorDetector
from transform import getPerspectiveTransform
from ui import TkUI

# PATH_IMAGE = "img/other/allsensors.png"
# PATH_PATTERN = "img/other/allsensors_pattern.png"
# DOWNSCALE = 1
# WINDOW_NAME = "tray0"

PATH_IMAGE = "img/calibration/img.png"
PATH_PATTERN = "img/calibration/img_pattern.png"
DOWNSCALE_IMAGE = 4
DOWNSCALE_PATTERN = 1
WINDOW_NAME = "calibration"

# Pixels 2x scale
TRAY_WIDTH = 330 * 2
TRAY_HEIGHT = 200 * 2
SLOT_WIDTH = 32.3 * 2
SLOT_HEIGHT = 26.5 * 2
TRAY_ROWS = 7
TRAY_COLS = 7

def preprocess(img, block_radius=5, c=7):
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img = adaptiveThreshold(img, block_radius, c)
	return img

def segmentTray(img, ax):
	x0 = (TRAY_WIDTH - SLOT_WIDTH * TRAY_COLS) / 2
	y0 = (TRAY_HEIGHT - SLOT_HEIGHT * TRAY_ROWS) / 2

	for j in range(TRAY_ROWS):
		for i in range(TRAY_COLS):
			x = int(x0 + SLOT_WIDTH * i)
			y = int(y0 + SLOT_HEIGHT * j)

			rect = Rectangle((x, y), SLOT_WIDTH, SLOT_HEIGHT, alpha=1, fill=False, color=(1, 0, 1))
			ax.add_patch(rect)

def main():
	img = cv2.imread(PATH_IMAGE, cv2.IMREAD_COLOR)
	pattern = cv2.imread(PATH_PATTERN, cv2.IMREAD_COLOR)

	img = downscale(img, DOWNSCALE_IMAGE)
	pattern = downscale(pattern, DOWNSCALE_PATTERN)

	# img = img[:,200:]

	detector = SensorDetector()

	f = Figure()
	# f.set_tight_layout(True)

	ui = TkUI(WINDOW_NAME)
	ui.addTable()
	ui.addFigure(f)
	ui.addSlider("match_threshold",     0.60, 0,   1, 0.01)
	ui.addSlider("clustering_bandwidth", 40, 1, 100)
	ui.addSlider("block_radius", 50, 1, 200, 1, int)
	ui.addSlider("c", 20, -50, 50, 1, int)

	ax1 = f.add_subplot(2, 2, 1)
	ax2 = f.add_subplot(2, 2, 2)
	ax3 = f.add_subplot(2, 2, 3)
	ax4 = f.add_subplot(2, 2, 4)

	while True:

		detector.match_threshold, changed1 = ui.getSlider("match_threshold")
		detector.clustering_bandwidth, changed2 = ui.getSlider("clustering_bandwidth")
		block_radius, changed3 = ui.getSlider("block_radius")
		c, changed4 = ui.getSlider("c")

		if any((changed1, changed2, changed3, changed4)):
			img_proc = preprocess(img, block_radius, c)
			pattern_proc = preprocess(pattern, block_radius, c)

			aximshow(ax3, img_proc)
			aximshow(ax4, pattern_proc)

			# Stopwatch execution of detector.detect
			t0 = time()

			matches = detector.detect(img_proc, pattern_proc)

			if matches:
				ui.table.set("Detector time", time() - t0)
				ui.table.set("Matches", np.array(matches))

				if len(matches) == 4:
					t1 = time()

					transform = getPerspectiveTransform(img, matches, (TRAY_HEIGHT, TRAY_WIDTH))

					result = transform(img)

					ui.table.set("Transform time", time() - t1)
					ui.table.set("Transform matrix", transform.matrix)

					segmentTray(result, ax2)

					# p1 = (int(TRAY_WIDTH - SLOT_WIDTH * 7), int(TRAY_HEIGHT - SLOT_HEIGHT * 7))
					# p2 = (int(TRAY_WIDTH - SLOT_WIDTH * 5), int(TRAY_HEIGHT - SLOT_HEIGHT * 5))
					# cv2.rectangle(result, p1, p2, (0, 255, 0), 1)
					# cv2.rectangle(result, (136, 41), (524, 359), (0, 255, 0), 2)

					aximshow(ax2, result)

				aximshow(ax1, img)
				matches.axpaint(ax1)
				
			ui.updateFigure()

		else:
			sleep(1/60)

		ui.update()


if __name__ == '__main__':
	main()
