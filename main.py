import logging
from matplotlib.figure import Figure
from time import sleep, time

from config import loadYAML
from cvutils import adaptiveThreshold
from detector import CalibrationDetector, SensorDetector
from transform import getPerspectiveTransform
from tray import getTrayDef
from utils import loadImage, axShowImage, axPaint, findBestMatches

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

def main():
	logging.basicConfig(level=logging.DEBUG)

	params = loadYAML("parameters.yml")
	tray = getTrayDef(**params.tray)

	img = loadImage(**params.image)
	img = calibrate(img, params, tray)
	results = detectSensors(img, params, tray)

	print(results)

if __name__ == "__main__":
	main()