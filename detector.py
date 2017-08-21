"""Note about indices and index arrays (sparse arrays):
In detector.py, indices are (y, x). This is for ease of processing.
In detector_result.py, indices are (x, y). This is to follow numpy convention.
"""

import cv2
import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
from warnings import warn

from detector_result import CalibrationDetectorResult, SensorDetectorResult

class CalibrationDetector:
	def __init__(self, params={}, **kwargs):
		# Available parameters
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

	def detect(self, img, pattern):
		match_map = cv2.matchTemplate(img, pattern, self.match_method)
		candidates = np.transpose(np.where(match_map > self.match_threshold))

		if 0 in candidates.shape:
			warn("0 matches detected")
			return None

		self.clusterer.set_params(bandwidth=self.clustering_bandwidth)
		self.clusterer.fit(candidates)
		labels = self.clusterer.labels_

		matches = self._bestMatches(match_map, candidates, labels)

		return CalibrationDetectorResult(matches, match_map, pattern)


class SensorDetector:
	def __init__(self, params={}, **kwargs):
		# Available parameters
		self.match_method = cv2.TM_CCOEFF_NORMED
		self.match_threshold = 0.8

		# Combine params and kwargs -- Use params dict and/or kwargs to seed parameters
		params.update(kwargs)

		for k,v in params.items():
			if k in self.__dict__:
				self.__dict__[k] = v
			else:
				raise AttributeError("Unknown parameter: " + k)

	def detect(self, img, pattern, tray):
		offsets = np.empty((tray.rows, tray.cols, 2), dtype=np.int_)
		scores = np.empty((tray.rows, tray.cols), dtype=np.float32)

		for row, col in tray:
			cell = tray.getCell(img, row, col)
			match_map = cv2.matchTemplate(cell, pattern, self.match_method)

			best_match_flat = np.argmax(match_map)
			best_match = np.unravel_index(best_match_flat, match_map.shape)
			offsets[row, col] = best_match

			score = match_map[best_match]
			scores[row, col] = score

		matches = scores > self.match_threshold

		return SensorDetectorResult(offsets, scores, matches, pattern, tray)
