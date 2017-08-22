"""Note about indices and index arrays (sparse arrays):
In detector.py, indices are (y, x). This is for ease of processing.
In detector_result.py, indices are (x, y). This is to follow numpy convention.
"""

import cv2
import numpy as np
import logging
from sklearn.cluster import MeanShift, estimate_bandwidth

from detector_result import CalibrationDetectorResult, SensorDetectorResult

class CalibrationDetector:
	def __init__(self, pattern, params={}, **kwargs):
		self.pattern = pattern
		# Available parameters:
		self.match_method = cv2.TM_CCOEFF_NORMED
		self.match_threshold = 0.8
		self.clustering_bandwidth = 40

		# Combine params and kwargs -- Use params dict and/or kwargs to seed parameters
		params.update(kwargs)

		for k,v in params.items():
			if k in self.__dict__:
				self.__dict__[k] = v
			else:
				raise AttributeError("Unknown parameter: " + k)

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

	def detect(self, img):
		match_map = cv2.matchTemplate(img, self.pattern, self.match_method)
		candidates = np.transpose(np.where(match_map > self.match_threshold))

		if 0 in candidates.shape:
			logging.warning("0 matches detected")
			return

		self.clusterer.set_params(bandwidth=self.clustering_bandwidth)
		self.clusterer.fit(candidates)
		labels = self.clusterer.labels_

		matches = self._bestMatches(match_map, candidates, labels)

		return CalibrationDetectorResult(matches, match_map, self.pattern)


class SensorDetector:
	def __init__(self, pattern, tray, params={}, **kwargs):
		self.pattern = pattern
		self.tray = tray
		# Available parameters:
		self.match_method = cv2.TM_CCOEFF_NORMED
		self.match_threshold = 0.8

		# Combine params and kwargs -- Use params dict and/or kwargs to seed parameters
		params.update(kwargs)

		for k,v in params.items():
			if k in self.__dict__:
				self.__dict__[k] = v
			else:
				raise AttributeError("Unknown parameter: " + k)

	def detect(self, img):
		offsets = np.full((self.tray.rows, self.tray.cols, 2), -1, dtype=np.int_)
		scores = np.zeros((self.tray.rows, self.tray.cols), dtype=np.float32)

		for row, col in self.tray:
			cell = self.tray.getCell(img, row, col)
			match_map = cv2.matchTemplate(cell, self.pattern, self.match_method)

			best_match_flat = np.argmax(match_map)
			best_match = np.unravel_index(best_match_flat, match_map.shape)

			score = match_map[best_match]
			if score > self.match_threshold:
				offsets[row, col] = best_match

				scores[row, col] = score

		return SensorDetectorResult(offsets, scores, self.pattern, self.tray)
