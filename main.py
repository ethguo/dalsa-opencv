import cv2
import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle
from time import sleep, time

from cvutils import downscale, adaptiveThreshold, aximshow
from detector import CalibrationDetector, SensorDetector
from transform import getPerspectiveTransform
from tray import getTrayDef, drawGrid, getCells
from ui import TkUI

# PATH_IMAGE = "img/other/allsensors.png"
# PATH_PATTERN = "img/other/allsensors_pattern.png"
# DOWNSCALE = 1
# WINDOW_NAME = "tray0"

PATH_IMAGE = "img/calibration/img.png"
PATH_CALIBRATION_PATTERN = "img/calibration/img_calibration.png"
PATH_SENSOR_PATTERN = "img/calibration/img_pattern.png"
DOWNSCALE_IMAGE = 4
DOWNSCALE_CALIBRATION_PATTERN = 1
DOWNSCALE_SENSOR_PATTERN = 4
WINDOW_NAME = "calibration"

TRAY_NAME = "qvga_7x7"

def preprocess(img, block_radius=5, c=7):
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img = adaptiveThreshold(img, block_radius, c)
	return img

def main():
	img = cv2.imread(PATH_IMAGE, cv2.IMREAD_COLOR)
	calibration_pattern = cv2.imread(PATH_CALIBRATION_PATTERN, cv2.IMREAD_COLOR)
	sensor_pattern = cv2.imread(PATH_SENSOR_PATTERN, cv2.IMREAD_COLOR)

	img = downscale(img, DOWNSCALE_IMAGE)
	calibration_pattern = downscale(calibration_pattern, DOWNSCALE_CALIBRATION_PATTERN)
	sensor_pattern = downscale(sensor_pattern, DOWNSCALE_SENSOR_PATTERN)

	tray = getTrayDef(TRAY_NAME, scale=2)

	# img = img[:,200:]

	calibration_detector = CalibrationDetector(match_threshold=0.6, clustering_bandwidth=40) # Used to detect calibration points
	sensor_detector = SensorDetector(match_threshold=0.8)

	f = Figure()
	# f.set_tight_layout(True)

	ui = TkUI(f, WINDOW_NAME)
	ui.addSlider("calib_match_threshold",  0.60,   0,   1, 0.01)
	ui.addSlider("clustering_bandwidth",     40,   1, 100)
	ui.addSlider("block_radius",             50,   1, 200)
	ui.addSlider("c",                        20, -50,  50)
	ui.addSlider("sensor_match_threshold", 0.50,   0,   1, 0.01)

	# ax1 = f.add_subplot(2, 2, 1)
	# ax2 = f.add_subplot(2, 2, 2)
	# ax3 = f.add_subplot(2, 2, 3)
	# ax4 = f.add_subplot(2, 2, 4)
	ax1 = f.add_subplot(121)
	ax2 = f.add_subplot(122)

	while True:

		calibration_detector.match_threshold, changed1 = ui.getSlider("calib_match_threshold")
		calibration_detector.clustering_bandwidth, changed2 = ui.getSlider("clustering_bandwidth")
		block_radius, changed3 = ui.getSlider("block_radius")
		c, changed4 = ui.getSlider("c")

		sensor_detector.match_threshold, changed5 = ui.getSlider("sensor_match_threshold")

		if any((changed1, changed2, changed3, changed4, changed5)):
			img_proc = preprocess(img, block_radius, c)
			calibration_pattern_proc = preprocess(calibration_pattern, block_radius, c)

			# aximshow(ax3, img_proc)
			# aximshow(ax4, pattern_proc)

			# Stopwatch execution of calibration_detector.detect
			t0 = time()

			calibration_matches = calibration_detector.detect(img_proc, calibration_pattern_proc)

			if calibration_matches:
				ui.setTableRow("CalibrationDetector time", time() - t0)

				if len(calibration_matches) == 4:
					ax2.clear()

					t1 = time()

					transform = getPerspectiveTransform(img, calibration_matches, (tray.height, tray.width))

					img_transformed = transform(img)

					ui.setTableRow("Transform time", time() - t1)

					t2 = time()

					for cell, row, col, x1, y1, x2, y2 in getCells(img_transformed, tray):
						sensor_match = sensor_detector.detect(cell, sensor_pattern)
						color = (1, 0, 0)
						if sensor_match:
							ax1.clear()
							aximshow(ax1, cell)
							sensor_match.axpaint(ax1)
							color = (0, 1, 0)
						rect = Rectangle((x1+2, y1+2), tray.cell_width-4, tray.cell_height-4, alpha=1, fill=False, color=color)
						ax2.add_patch(rect)

					ui.setTableRow("SensorDetector time", time() - t2)

				aximshow(ax2, img_transformed)

				# aximshow(ax1, img)
				# calibration_matches.axpaint(ax1)
				
			ui.updateFigure()

		else:
			sleep(1/60)

		ui.update()


if __name__ == "__main__":
	main()
