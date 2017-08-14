import cv2
import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth

from preprocess import *
from hsv import *

color_gradient = lambda val: (0, val*2*255, 255) if val < 0.5 else (0, 255, (1-val)*2*255) #BGR

class SensorDetectorResult:
	def __init__(self, detector, matches, match_map):
		self.matches = matches
		self.match_map = match_map

		self.scores = match_map[tuple(np.transpose(matches))]
		self.squared_errors = (1 - self.scores) ** 2
		self.rss = np.sum(self.squared_errors)
		self.avg_error = self.rss / len(self)
		self.product_error = np.product(self.scores)

		self.pattern_shape = detector.pattern.shape[:2]

	def paint(self, img, line_thickness=1):
		# footer = np.zeros((100, img.shape[1], 3), dtype=np.uint8)
		# canvas = np.concatenate([img, footer])
		canvas = np.copy(img)

		pattern_h, pattern_w = self.pattern_shape

		for match, score in zip(self.matches, self.scores):
			y, x = match
			color = color_gradient(score)

			cv2.rectangle(canvas, 
				(x, y), (x + pattern_w, y + pattern_h),
				color=color, thickness=line_thickness)

			cv2.circle(canvas,
				(x + pattern_w//2, y + pattern_h//2), radius=2*line_thickness,
				color=color, thickness=-1)

		return canvas 	

	# Magic methods to allow it to behave like a sequence
	def __len__(self):
		return len(self.matches)

	def __getitem__(self, key):
		return self.matches[key]

	def __iter__(self):
		return iter(self.matches)


class SensorDetector:
	def __init__(self, pattern, params={}, **kwargs):
		# Available parameters
		self.preprocess = lambda img: img
		self.pattern = pattern
		self.match_method = cv2.TM_CCOEFF_NORMED
		self.match_threshold = 0.8
		self.clustering_bandwidth = 40

		# Use params dict and/or kwargs to seed parameters
		params = {**params, **kwargs}

		for k,v in params.items():
			if k in self.__dict__:
				self.__dict__[k] = v
			else:
				raise AttributeError("Unknown parameter: " + k)

		# Preprocess pattern
		self.pattern_proc = self.preprocess(self.pattern)

		self.clusterer = MeanShift(self.clustering_bandwidth)

	# def preprocess(self, img):
	# 	output = img #skip

	# 	# output = canny(img, 32)
	# 	# output = sat_mask(img, self.threshold_block_radius, self.threshold_c)
	# 	# output = get_sat(img)

	# 	return output

	def _best_matches(self, match_map, candidates, labels):
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
		img_proc = self.preprocess(img)
		match_map = cv2.matchTemplate(img_proc, self.pattern_proc, self.match_method)
		candidates = np.transpose(np.where(match_map >= self.match_threshold))

		if 0 in candidates.shape:
			raise Warning("0 matches detected")
			return None

		self.clusterer.set_params(bandwidth=self.clustering_bandwidth)
		self.clusterer.fit(candidates)
		labels = self.clusterer.labels_
		# centers = self.clusterer.cluster_centers_

		matches = self._best_matches(match_map, candidates, labels)

		# matches = np.int_(centers)

		# cv2.imshow("pattern_proc", pattern_proc)
		# cv2.imshow("img_proc", img_proc)

		return SensorDetectorResult(self, matches, match_map), img_proc
