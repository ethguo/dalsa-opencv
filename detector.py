"""Note about indices/index arrays (sparse arrays):
For "private" fields, all variables meant to stay within this module, all indices are (y, x). This is for ease of processing.
For public fields (like DetectorResult.centers), those meant to be accessed outside of this module, indices are (x, y). This is to follow numpy convention.
"""

import cv2
import numpy as np
import warnings
from matplotlib.patches import Circle, Rectangle
from sklearn.cluster import MeanShift, estimate_bandwidth

color_gradient_bgr = lambda val: (0, val*2*255, 255) if val < 0.5 else (0, 255, (1-val)*2*255)
color_gradient_rgb = lambda val: (1, val*2, 0) if val < 0.5 else ((1-val)*2, 1, 0)

class CalibrationDetectorResult:
	def __init__(self, matches, match_map, pattern):
		self.matches = matches
		# self.match_map = match_map

		self.pattern_shape = np.array(pattern.shape[:2])

		centers = self.matches + self.pattern_shape // 2
		self.centers = np.flip(centers, axis=1)

		self.scores = match_map[tuple(np.transpose(matches))]

		# self.squared_errors = (1 - self.scores) ** 2
		# self.rss = np.sum(self.squared_errors)
		# self.avg_error = self.rss / len(self)
		# self.product_error = np.product(self.scores)

	def paint(self, img, line_thickness=2):
		# footer = np.zeros((100, img.shape[1], 3), dtype=np.uint8)
		# canvas = np.concatenate([img, footer])
		canvas = np.copy(img)

		pattern_h, pattern_w = self.pattern_shape

		for match, score, center in zip(self.matches, self.scores, self.centers):
			y, x = match
			color = color_gradient_bgr(score)

			cv2.rectangle(canvas, 
				(x, y), (x + pattern_w, y + pattern_h),
				color=color, thickness=line_thickness)

			cv2.circle(canvas,
				center, radius=2*line_thickness,
				color=color, thickness=-1)

		return canvas

	def axpaint(self, ax):
		pattern_h, pattern_w = self.pattern_shape

		for match, score in zip(self.matches, self.scores):
			y, x = match
			color = color_gradient_rgb(score)

			rect = Rectangle((x, y), pattern_w, pattern_h, alpha=1, fill=False, color=color)
			point = Circle((x + pattern_w//2, y + pattern_h//2), radius=2, color=color)

			ax.add_patch(rect)
			ax.add_patch(point)

	# Magic methods to allow it to behave like a sequence
	def __getitem__(self, key):
		return self.centers[key]

	def __iter__(self):
		return iter(self.centers)

	def __len__(self):
		return len(self.centers)

	def __repr__(self):
		return repr(self.centers)

	def __str__(self):
		return str(self.centers)


class SensorDetectorResult:
	def __init__(self, match, score, pattern):
		self.match = match
		self.score = score

		self.pattern_shape = np.array(pattern.shape[:2])

		center = self.match + self.pattern_shape // 2
		self.center = np.flip(center, axis=0)

	def paint(self, img, line_thickness=2):
		# footer = np.zeros((100, img.shape[1], 3), dtype=np.uint8)
		# canvas = np.concatenate([img, footer])
		canvas = np.copy(img)

		pattern_h, pattern_w = self.pattern_shape

		y, x = self.match
		color = color_gradient_bgr(self.score)

		cv2.rectangle(canvas, 
			(x, y), (x + pattern_w, y + pattern_h),
			color=color, thickness=line_thickness)

		cv2.circle(canvas,
			self.center, radius=2*line_thickness,
			color=color, thickness=-1)

		return canvas

	def axpaint(self, ax):
		pattern_h, pattern_w = self.pattern_shape

		y, x = self.match
		color = color_gradient_rgb(self.score)

		rect = Rectangle((x, y), pattern_w, pattern_h, alpha=1, fill=False, color=color)
		point = Circle((x + pattern_w//2, y + pattern_h//2), radius=2, color=color)

		ax.add_patch(rect)
		ax.add_patch(point)

	def __repr__(self):
		return repr(self.center)

	def __str__(self):
		return str(self.center)


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
		candidates = np.transpose(np.where(match_map >= self.match_threshold))

		if 0 in candidates.shape:
			warnings.warn("0 matches detected")
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

	def detect(self, img, pattern):
		match_map = cv2.matchTemplate(img, pattern, self.match_method)

		best_match_flat = np.argmax(match_map)
		best_match = np.unravel_index(best_match_flat, match_map.shape)

		score = match_map[best_match]

		if score > self.match_threshold:
			return SensorDetectorResult(best_match, score, pattern)
		else:
			return None