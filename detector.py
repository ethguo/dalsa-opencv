"""Classes that do two different use cases of template matching.

Note about indices and index arrays (sparse arrays):
In detector.py, indices are (y, x). This is for ease of processing.
In detector_result.py, indices are (x, y). This is to follow numpy convention.
The conversion happens in `CalibrationDetectorResult.__init__` and `SensorDetectorResult.__init__`.
"""
import logging

import cv2
import numpy as np
from sklearn.cluster import MeanShift

from detector_result import CalibrationDetectorResult
from detector_result import SensorDetectorResult


#TODO: Honestly, these two classes don't need to be classes, they should just be functions.
class CalibrationDetector:
	def __init__(self, params={}, **kwargs):
		# Available parameters:
		self.match_method = cv2.TM_CCOEFF_NORMED
		self.match_threshold = 0.8
		self.clustering_bandwidth = 40

		# Combine params and kwargs -- Use params dict and/or kwargs to seed parameters.
		params.update(kwargs)

		for name, value in params.items():
			if name in self.__dict__:
				self.__dict__[name] = value # self.__dict__["x"] is like self.x
			else:
				raise AttributeError("Unknown parameter: " + name)

		# Initialize a MeanShift clusterer from sklearn.
		self.clusterer = MeanShift(self.clustering_bandwidth)

	def _bestMatches(self, match_map, candidates, labels):
		num_matches = len(np.unique(labels))
		min_errors = np.zeros(num_matches, dtype=match_map.dtype)
		best_matches = np.zeros((num_matches, 2), dtype=candidates.dtype)

		for candidate, label in zip(candidates, labels):
			error = match_map[tuple(candidate)]
			if error > min_errors[label]:
				min_errors[label] = error
				best_matches[label] = candidate

		return best_matches

	def detect(self, img, pattern):
		match_map = cv2.matchTemplate(img, pattern, self.match_method) # Call the cv2 function that does the template matching.
		candidates = np.transpose(np.where(match_map > self.match_threshold)) # Get all the matched points that were above the threshold.

		# If there were no matches, warn and return None.
		if 0 in candidates.shape:
			logging.warning("0 matches detected")
			return

		# Use the MeanShift clusterer to eliminate multiple "matches" for the same object.
		self.clusterer.set_params(bandwidth=self.clustering_bandwidth)
		self.clusterer.fit(candidates)

		# Find the highest-scoring point in each cluster and treat that as the "match".
		labels = self.clusterer.labels_
		matches = self._bestMatches(match_map, candidates, labels)

		# Encapsulate and return.
		return CalibrationDetectorResult(matches, match_map, pattern)


class SensorDetector:
	def __init__(self, params={}, **kwargs):
		# Available parameters:
		self.match_method = cv2.TM_CCOEFF_NORMED
		self.match_threshold = 0.8

		# Combine params and kwargs -- Use params dict and/or kwargs to seed parameters.
		params.update(kwargs)

		for name, value in params.items():
			if name in self.__dict__:
				self.__dict__[name] = value # self.__dict__["x"] is like self.x
			else:
				raise AttributeError("Unknown parameter: " + name)

	def detect(self, img, pattern, tray):
		offsets = np.full((tray.rows, tray.cols, 2), -1, dtype=np.int_) # Offsets is how far each match is from the top-left of their tray cell (i.e. the image from tray.getCell).
		scores = np.zeros((tray.rows, tray.cols), dtype=np.float32) # Initialize the scores array with zeros.

		for row, col in tray: # For each cell in the tray:
			cell = tray.getCell(img, row, col) # Get the sub-image
			match_map = cv2.matchTemplate(cell, pattern, self.match_method) # Call the cv2 function that does the template matching.

			best_match_flat = np.argmax(match_map) # Finds the index of the highest-scoring point in the whole image (flattened).
			best_match = np.unravel_index(best_match_flat, match_map.shape) # Get the index of that point in the unflattened array.

			# If the match is above the threshold, update the corresponding spots in the offsets and scores arrays.
			score = match_map[best_match]
			if score > self.match_threshold:
				offsets[row, col] = best_match
				scores[row, col] = score

		# Encapsulate and return.
		return SensorDetectorResult(offsets, scores, pattern, tray)
