"""Classes that do two different use cases of template matching.

Note about indices and index arrays (sparse arrays):
In detector.py, indices are (y, x). This is for ease of processing.
In detector_result.py, indices are (x, y). This is to follow numpy convention.
The conversion happens in `CalibrationDetectorResult.__init__` and `SensorDetectorResult.__init__`.
"""

import cv2
import numpy as np
import logging
from sklearn.cluster import MeanShift, estimate_bandwidth

from detector_result import CalibrationDetectorResult, SensorDetectorResult

#TODO: Honestly, these two classes don't need to be classes, they should just be functions.
class CalibrationDetector:
	def __init__(self, params={}, **kwargs):
		# Available parameters:
		self.match_method = cv2.TM_CCOEFF_NORMED
		self.match_threshold = 0.8
		self.clustering_bandwidth = 40

		# Combine params and kwargs -- Use params dict and/or kwargs to seed parameters
		params.update(kwargs)

		for name, value in params.items():
			if name in self.__dict__:
				self.__dict__[name] = value # Set self.name to value
			else:
				raise AttributeError("Unknown parameter: " + name)

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
		match_map = cv2.matchTemplate(img, pattern, self.match_method)
		candidates = np.transpose(np.where(match_map > self.match_threshold))

		if 0 in candidates.shape:
			logging.warning("0 matches detected")
			return

		self.clusterer.set_params(bandwidth=self.clustering_bandwidth)
		self.clusterer.fit(candidates)
		labels = self.clusterer.labels_

		matches = self._bestMatches(match_map, candidates, labels)

		return CalibrationDetectorResult(matches, match_map, pattern)


class SensorDetector:
	def __init__(self, params={}, **kwargs):
		# Available parameters:
		self.match_method = cv2.TM_CCOEFF_NORMED
		self.match_threshold = 0.8

		# Combine params and kwargs -- Use params dict and/or kwargs to seed parameters
		params.update(kwargs)

		for name, value in params.items():
			if name in self.__dict__:
				self.__dict__[name] = value # Set self.name to value
			else:
				raise AttributeError("Unknown parameter: " + name)

	def detect(self, img, pattern, tray):
		offsets = np.full((tray.rows, tray.cols, 2), -1, dtype=np.int_)
		scores = np.zeros((tray.rows, tray.cols), dtype=np.float32)

		for row, col in tray:
			cell = tray.getCell(img, row, col)
			match_map = cv2.matchTemplate(cell, pattern, self.match_method)

			best_match_flat = np.argmax(match_map)
			best_match = np.unravel_index(best_match_flat, match_map.shape)

			score = match_map[best_match]
			if score > self.match_threshold:
				offsets[row, col] = best_match

				scores[row, col] = score

		return SensorDetectorResult(offsets, scores, pattern, tray)
