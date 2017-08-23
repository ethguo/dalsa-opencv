"""Please note that this file is 'deprecated', in that it still works, but the code isn't up to par with main.py and main_gui.py."""
import cv2
import numpy as np
from matplotlib.figure import Figure
from time import sleep, time

from cvutils import adaptiveThreshold
from detector import CalibrationDetector, SensorDetector
from transform import getPerspectiveTransform
from tray import getTrayDef
from ui import TkUI, axShowImage, axPaint
from utils import loadImage

PATH_IMAGE = "img/calibration/img1.png"
PATH_CALIBRATION_PATTERN = "img/calibration/calibration_320.png"
PATH_SENSOR_PATTERN = "img/calibration/pattern2.png"
SCALE_IMAGE = 1/4
SCALE_CALIBRATION_PATTERN = 1/4
SCALE_SENSOR_PATTERN = 1/4

TRAY_NAME = "qvga_7x7"
TRAY_SCALE = 2

WINDOW_NAME = "calibration"

def main():
	img = loadImage(PATH_IMAGE, scale=SCALE_IMAGE)
	calibration_pattern = loadImage(PATH_CALIBRATION_PATTERN, scale=SCALE_CALIBRATION_PATTERN)
	sensor_pattern = loadImage(PATH_SENSOR_PATTERN, scale=SCALE_SENSOR_PATTERN)

	tray = getTrayDef(TRAY_NAME, scale=TRAY_SCALE)

	calibration_detector = CalibrationDetector(match_threshold=0.6, clustering_bandwidth=40) # Used to detect calibration points
	sensor_detector = SensorDetector(match_threshold=0.8)

	f = Figure()

	ui = TkUI(f, WINDOW_NAME)
	ui.addSlider("calib_match_threshold",  0.50,   0,   1, 0.01)
	ui.addSlider("clustering_bandwidth",     40,   1, 100)
	ui.addSlider("block_radius",             50,   1, 200)
	ui.addSlider("c",                        20, -50,  50)
	ui.addSlider("sensor_match_threshold", 0.25,   0,   1, 0.01)

	ax1 = f.add_subplot(121)
	ax2 = f.add_subplot(122)

	while True:

		calibration_detector.match_threshold, changed1 = ui.getSliderChanged("calib_match_threshold")
		calibration_detector.clustering_bandwidth, changed2 = ui.getSliderChanged("clustering_bandwidth")
		block_radius, changed3 = ui.getSliderChanged("block_radius")
		c, changed4 = ui.getSliderChanged("c")
		sensor_detector.match_threshold, changed5 = ui.getSliderChanged("sensor_match_threshold")

		if any((changed1, changed2, changed3, changed4, changed5)):
			img_proc = adaptiveThreshold(img, block_radius, c)
			calibration_pattern_proc = adaptiveThreshold(calibration_pattern, block_radius, c)

			# Stopwatch execution of calibration_detector.detect
			t0 = time()
			
			calibration_matches = calibration_detector.detect(img_proc, calibration_pattern_proc)
			
			ui.setTableRow("CalibrationDetector time", time() - t0)

			axShowImage(ax1, img)
			axPaint(ax1, calibration_matches)

			if len(calibration_matches) >= 4:
				t1 = time()

				transform = getPerspectiveTransform(img, calibration_matches[:4], (tray.height, tray.width))

				img_transformed = transform(img)

				ui.setTableRow("Transform time", time() - t1)

				t2 = time()

				# for cell, row, col, x1, y1, x2, y2 in getCells(img_transformed, tray):
				sensor_matches = sensor_detector.detect(img_transformed, sensor_pattern, tray)

				ui.setTableRow("SensorDetector time", time() - t2)

				axShowImage(ax2, img_transformed)
				axPaint(ax2, sensor_matches)

			ui.updateFigure()

		else:
			sleep(1/60)

		ui.update()


if __name__ == "__main__":
	main()
