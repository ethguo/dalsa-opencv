import logging
from matplotlib.figure import Figure
from time import sleep, time

from config import loadYAML
from cvutils import adaptiveThreshold
from detector import CalibrationDetector, SensorDetector
from transform import getPerspectiveTransform
from tray import getTrayDef
from utils import loadImage, calibrate, detectSensors

def main():
	logging.basicConfig(level=logging.INFO)

	params = loadYAML("parameters.yml")
	tray = getTrayDef(**params.tray)

	img = loadImage(**params.image)
	img = calibrate(img, params, tray)
	results = detectSensors(img, params, tray)

	print(results)

if __name__ == "__main__":
	main()