import cv2
import numpy as np
from matplotlib.figure import Figure
from time import sleep, time

from cvutils import downscale, adaptiveThreshold, aximshow
from detector import CalibrationDetector
from transform import getPerspectiveTransform
from tray import getTrayDef, processTray, drawGrid
from ui import TkUI

# PATH_IMAGE = "img/other/allsensors.png"
# PATH_PATTERN = "img/other/allsensors_pattern.png"
# DOWNSCALE = 1
# WINDOW_NAME = "tray0"

PATH_IMAGE = "img/calibration/img.png"
PATH_PATTERN = "img/calibration/img_calibration.png"
DOWNSCALE_IMAGE = 4
DOWNSCALE_PATTERN = 1
WINDOW_NAME = "calibration"

TRAY_NAME = "qvga_7x7"

def preprocess(img, block_radius=5, c=7):
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img = adaptiveThreshold(img, block_radius, c)
	return img

def main():
	img = cv2.imread(PATH_IMAGE, cv2.IMREAD_COLOR)
	pattern = cv2.imread(PATH_PATTERN, cv2.IMREAD_COLOR)

	img = downscale(img, DOWNSCALE_IMAGE)
	pattern = downscale(pattern, DOWNSCALE_PATTERN)

	tray = getTrayDef(TRAY_NAME, scale=2)

	# img = img[:,200:]

	calibration_detector = CalibrationDetector(match_threshold=0.6, clustering_bandwidth=40) # Used to detect calibration points

	f = Figure()
	# f.set_tight_layout(True)

	ui = TkUI(WINDOW_NAME)
	ui.addTable()
	ui.addFigure(f)
	ui.addSlider("match_threshold",     0.60,   0,   1, 0.01, float)
	ui.addSlider("clustering_bandwidth",  40,   1, 100)
	ui.addSlider("block_radius",          50,   1, 200)
	ui.addSlider("c",                     20, -50,  50)

	# ax1 = f.add_subplot(2, 2, 1)
	# ax2 = f.add_subplot(2, 2, 2)
	# ax3 = f.add_subplot(2, 2, 3)
	# ax4 = f.add_subplot(2, 2, 4)
	ax1 = f.add_subplot(121)
	ax2 = f.add_subplot(122)

	while True:

		calibration_detector.match_threshold, changed1 = ui.getSlider("match_threshold")
		calibration_detector.clustering_bandwidth, changed2 = ui.getSlider("clustering_bandwidth")
		block_radius, changed3 = ui.getSlider("block_radius")
		c, changed4 = ui.getSlider("c")

		if any((changed1, changed2, changed3, changed4)):
			img_proc = preprocess(img, block_radius, c)
			pattern_proc = preprocess(pattern, block_radius, c)

			# aximshow(ax3, img_proc)
			# aximshow(ax4, pattern_proc)

			# Stopwatch execution of calibration_detector.detect
			t0 = time()

			matches = calibration_detector.detect(img_proc, pattern_proc)

			if matches:
				ui.table.set("Detector time", time() - t0)
				ui.table.set("Matches", np.array(matches))

				if len(matches) == 4:
					t1 = time()

					transform = getPerspectiveTransform(img, matches, (tray.height, tray.width))

					img_transformed = transform(img)

					ui.table.set("Transform time", time() - t1)
					ui.table.set("Transform matrix", transform.matrix)

					result = processTray(img_transformed, tray)
					aximshow(ax1, result)
					drawGrid(ax2, tray)

					# p1 = (int(TRAY_WIDTH - SLOT_WIDTH * 7), int(TRAY_HEIGHT - SLOT_HEIGHT * 7))
					# p2 = (int(TRAY_WIDTH - SLOT_WIDTH * 5), int(TRAY_HEIGHT - SLOT_HEIGHT * 5))
					# cv2.rectangle(img_transformed, p1, p2, (0, 255, 0), 1)
					# cv2.rectangle(img_transformed, (136, 41), (524, 359), (0, 255, 0), 2)

					aximshow(ax2, img_transformed)

				# aximshow(ax1, img)
				# matches.axpaint(ax1)
				
			ui.updateFigure()

		else:
			sleep(1/60)

		ui.update()


if __name__ == '__main__':
	main()
