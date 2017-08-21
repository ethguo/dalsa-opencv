import logging
from matplotlib.figure import Figure
from time import sleep, time

from config import loadYAML
from cvutils import loadImage, adaptiveThreshold, axShowImage, axPaint
from detector import CalibrationDetector, SensorDetector
from transform import getPerspectiveTransform
from tray import getTrayDef

def main():
	params = loadYAML("parameters.yml")

	img = loadImage(**params.image)
	calibration_pattern = loadImage(**params.calibration_pattern)
	sensor_pattern = loadImage(**params.sensor_pattern)

	tray = getTrayDef(**params.tray)

	calibration_detector = CalibrationDetector(**params.calibration.detector) # Used to detect calibration points
	sensor_detector = SensorDetector(**params.sensors.detector)

	calibration_img = adaptiveThreshold(img, **params.calibration.preprocessing)
	calibration_pattern = adaptiveThreshold(calibration_pattern, **params.calibration.preprocessing)
	
	calibration_matches = calibration_detector.detect(calibration_img, calibration_pattern)
	
	if len(calibration_matches) < 4:
		logging.error("Only found %d out of 4 required calibration points." %(len(calibration_matches)))

	else:
		transform = getPerspectiveTransform(img, calibration_matches[:4], (tray.height, tray.width))

		img_transformed = transform(img)

		sensor_matches = sensor_detector.detect(img_transformed, sensor_pattern, tray)

		logging.info(str(sensor_matches.centers))
		return sensor_matches.centers


if __name__ == "__main__":
	main()
