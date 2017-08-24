#!/usr/bin/env python3
import logging

from yaml_config import loadYAML
from tray import getTrayDef
from find_sensors import loadImage, calibrate, detectSensors

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