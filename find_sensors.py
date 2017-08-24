"""In theory, all other python modules in this package (other than the `main` files of course) are general enough to be useful for any CV project.
This module steps down one level of generalization, and provides functions that each perform one step of the specific task of finding sensors on a calibrated tray."""
import logging

import cv2
import numpy as np

from cvutils import adaptiveThreshold
from cvutils import scaleImage
from detector import CalibrationDetector
from detector import SensorDetector
from transform import getPerspectiveTransform


def loadImage(path, scale=1):
	"""Loads an image by path at a specified scale."""
	img = cv2.imread(path, cv2.IMREAD_COLOR)
	if img is None:
		raise FileNotFoundError("No such file: " + path)
	img = scaleImage(img, scale)
	return img


def calibrate(img, params, tray):
	"""Given an uncalibrated image (with 4 calibration points visible), finds the 4 calibration points and transforms the image into a calibrated image.
	
	Args:
	    img (numpy.ndarray): Image to be transformed.
	    params (yaml_config.YAMLDict): Data loaded from `parameters.yml`.
	    tray (tray.TrayDefinition): `TrayDefinition` object which determines the height/width of the output image.
	
	Returns:
	    numpy.ndarray: Transformed image, of the shape (tray.height, tray.width, 3) for color images, or (tray.height, tray.width) for grayscale images.
	"""
	pattern = loadImage(**params.calibration_detector.pattern)

	# First, pass both the image and the pattern through an adaptiveThreshold filter.
	detector_img = adaptiveThreshold(img, **params.calibration_detector.preprocessing)
	pattern = adaptiveThreshold(pattern, **params.calibration_detector.preprocessing)

	# Detect calibration points.
	detector = CalibrationDetector(**params.calibration_detector.detector)
	result = detector.detect(detector_img, pattern)

	# Assuming at least 4 calibration points found...
	if len(result) < 4:
		logging.error("Only found %d out of 4 required calibration points." %(len(result)))
		return

	# PerspectiveTransform the image and return.
	transform = getPerspectiveTransform(img, result[:4], (tray.height, tray.width))
	img_transformed = transform(img)
	
	return img_transformed


def detectSensors(img, params, tray):
	"""Given a calibrated image and tray specification, finds which tray cells contain sensors.
	
	Args:
	    img (numpy.ndarray): Transformed image of the tray.
	    params (yaml_config.YAMLDict): Data loaded from `parameters.yml`.
	    tray (tray.TrayDefinition): `TrayDefinition` object which determines the number and size of cells in the tray.
	
	Returns:
	    numpy.ndarray: An array of shape (tray.rows, tray.cols), where each cell is an index representing the type of sensor in that cell
	        (0 for the first sensor defined in the config file, 1 for the second, etc.), or -1 if no match detected.
	"""

	# For each type of sensor, detect matches using SensorDetector.
	results = []
	for detector_params in params.sensor_detectors:
		pattern = loadImage(**detector_params.pattern)
		detector = SensorDetector(**detector_params.detector)

		result = detector.detect(img, pattern, tray)
		results.append(result)

	# Creates an array combining the detector scores for each type of sensor.
	all_scores = np.stack([result.scores for result in results])

	best_scores = np.amax(all_scores, axis=0) # Determine the highest score in each cell.
	best_sensor_type = np.argmax(all_scores, axis=0) # Determine the highest-scoring sensor type in each cell.

	# As long as there was a non-zero score in the cell, put in the index of the highest-scoring sensor type.
	# But if none of them matched (i.e. if none of the scores were > 0), put in -1.
	best_matches = np.where(best_scores > 0, best_sensor_type, -1)

	return best_matches, results
