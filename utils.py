import cv2
import numpy as np
import logging

from cvutils import scaleImage

def loadImage(path, scale=1):
	img = cv2.imread(path, cv2.IMREAD_COLOR)
	if img is None:
		raise FileNotFoundError("No such file: " + path)
	img = scaleImage(img, scale)
	return img

def calibrate(img, params, tray):
	pattern = loadImage(**params.calibration_detector.pattern)

	detector_img = adaptiveThreshold(img, **params.calibration_detector.preprocessing)
	pattern = adaptiveThreshold(pattern, **params.calibration_detector.preprocessing)

	# Detect calibration points
	detector = CalibrationDetector(pattern, **params.calibration_detector.detector)
	result = detector.detect(detector_img)

	if len(result) < 4:
		logging.error("Only found %d out of 4 required calibration points." %(len(result)))
		return

	transform = getPerspectiveTransform(img, result[:4], (tray.height, tray.width))
	img_transformed = transform(img)
	return img_transformed

def detectSensors(img, params, tray):
	results = []
	for detector_params in params.sensor_detectors:
		pattern = loadImage(**detector_params.pattern)
		detector = SensorDetector(pattern, tray, **detector_params.detector)

		result = detector.detect(img)
		results.append(result)

	best_matches = findBestMatches(results)

	return best_matches

def findBestMatches(results):
	all_scores = np.stack([result.scores for result in results])
	best_scores = np.amax(all_scores, axis=0)
	best_matches = np.argmax(all_scores, axis=0)
	best_matches = np.where(best_scores != 0, best_matches, -1)
	return best_matches
