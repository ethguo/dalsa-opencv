"""Note about indices and index arrays (sparse arrays):
In detector.py, indices are (y, x). This is for ease of processing.
In detector_result.py, indices are (x, y). This is to follow numpy convention.
"""

import numpy as np
from matplotlib.patches import Circle, Rectangle

_color_gradient_bgr = lambda val: (0, val*2*255, 255) if val < 0.5 else (0, 255, (1-val)*2*255)
_color_gradient_rgb = lambda val: (1, val*2, 0) if val < 0.5 else ((1-val)*2, 1, 0)

class DetectorResult:
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


class CalibrationDetectorResult (DetectorResult):
	def __init__(self, matches, match_map, pattern):
		self.positions = np.flip(matches, axis=1)

		self.scores = match_map[tuple(np.transpose(matches))]

		self.pattern_shape = np.array(pattern.shape[:2])

		centers = matches + self.pattern_shape // 2
		self.centers = np.flip(centers, axis=1)

	def axPaint(self, ax):
		pattern_h, pattern_w = self.pattern_shape

		for pos, score, center in zip(self.positions, self.scores, self.centers):
			color = _color_gradient_rgb(score)

			rect = Rectangle(pos, pattern_w, pattern_h, alpha=1, fill=False, color=color)
			point = Circle(center, radius=2, color=color)

			ax.add_patch(rect)
			ax.add_patch(point)


class SensorDetectorResult (DetectorResult):
	def __init__(self, offsets, scores, pattern, tray):
		self.offsets = np.flip(offsets, axis=2)
		self.scores = scores
		self.matches = scores > 0
		self.tray = tray

		self.pattern_shape = np.array(pattern.shape[:2])

		centers = offsets + self.pattern_shape // 2
		centers = np.where(offsets != -1, centers, -1)
		self.centers = np.flip(centers, axis=2)

	def axPaint(self, ax):
		pattern_h, pattern_w = self.pattern_shape

		for row, col in self.tray:
			if self.matches[row, col]:
				pos = self.tray.getPos(row, col)
				offset = self.offsets[row, col]
				score = self.scores[row, col]
				center = self.centers[row, col]
				color = _color_gradient_rgb(score)

				rect = Rectangle(pos + offset, pattern_w, pattern_h, alpha=1, fill=False, color=color)
				point = Circle(pos + center, radius=2, color=color)

				ax.add_patch(rect)
				ax.add_patch(point)
