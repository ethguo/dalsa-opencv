#!/usr/bin/env python3
"""Minimum code for full functionality (no GUI). Use this file as a starting point for integrating with ROS."""
import logging

from find_sensors import calibrate
from find_sensors import detectSensors
from find_sensors import loadImage
from tray import getTrayDef
from yaml_config import loadYAML


def main():
	# Set up logging.
	logging.basicConfig(level=logging.DEBUG)

	# Load parameters, tray definition, and image.
	params = loadYAML("parameters.yml")
	tray = getTrayDef(**params.tray)
	img = loadImage(**params.image)

	# Calibrate image and detect sensors.
	img = calibrate(img, params, tray)
	matches, _ = detectSensors(img, params, tray)

	print(matches)


if __name__ == "__main__":
	main()