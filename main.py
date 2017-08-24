#!/usr/bin/env python3
import logging

from find_sensors import calibrate
from find_sensors import detectSensors
from find_sensors import loadImage
from tray import getTrayDef
from yaml_config import loadYAML


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