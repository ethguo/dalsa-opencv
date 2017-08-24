"""Objects that are returned by `detector.CalibrationDetector.detect` and `detector.SensorDetector.detect`.

Note about indices and index arrays (sparse arrays):
In detector.py, indices are (y, x). This is for ease of processing.
In detector_result.py, indices are (x, y). This is to follow numpy convention.
The conversion happens in `CalibrationDetectorResult.__init__` and `SensorDetectorResult.__init__`.
"""

import numpy as np
from matplotlib.patches import Circle, Rectangle

"""Given a float value in [0..1], returns a RGB or BGR 3-tuple mapping the input to a color between 0=red and 1=green"""
_color_gradient_bgr = lambda val: (0, val*2*255, 255) if val < 0.5 else (0, 255, (1-val)*2*255) # Currently unused; useful for working with cv2 draw functions
_color_gradient_rgb = lambda val: (1, val*2, 0) if val < 0.5 else ((1-val)*2, 1, 0)

class DetectorResult:
	"""Base class for CalibrationDetectorResult and SensorDetectorResult."""
	
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
	"""Result of `CalibrationDetector.detect`.
	
	Attributes:
	    centers (numpy.ndarray): Center point of each matched object.
	    scores (numpy.ndarray): The quality of match ([0..1]).

	Args:
	    Passed from CalibrationDetector.
	"""
	def __init__(self, matches, match_map, pattern):
		self._positions = np.flip(matches, axis=1)

		self.scores = match_map[tuple(np.transpose(matches))]

		self._pattern_shape = np.array(pattern.shape[:2])

		centers = matches + self._pattern_shape // 2
		self.centers = np.flip(centers, axis=1)

	def axPaint(self, ax):
		"""Display the matches' locations on the given `ax` using matplotlib patches.
		
		Args:
		    ax (matplotlib.axes.Axes): The `Axes` to paint onto.
		"""
		pattern_h, pattern_w = self._pattern_shape

		for pos, score, center in zip(self._positions, self.scores, self.centers):
			color = _color_gradient_rgb(score)

			rect = Rectangle(pos, pattern_w, pattern_h, alpha=1, fill=False, color=color)
			point = Circle(center, radius=2, color=color)

			ax.add_patch(rect)
			ax.add_patch(point)


class SensorDetectorResult (DetectorResult):
	"""Result of `SensorDetector.detect`.

	Note: These attributes are structured differently from `CalibrationDetectorResult` attributes. 
	`matches` and `scores` are 2D arrays which correspond with the rows and cols of the tray.
	
	Attributes:
	    centers (numpy.ndarray): Center point of each matched object.
	    matches (numpy.ndarray): Whether or not each cell is a valid match.
	    scores (numpy.ndarray): The quality of match ([0..1]).

	Args:
	    Passed from SensorDetector.
	"""
	def __init__(self, offsets, scores, pattern, tray):
		self._offsets = np.flip(offsets, axis=2)
		self.scores = scores
		self.matches = scores > 0
		self._tray = tray

		self._pattern_shape = np.array(pattern.shape[:2])

		centers = offsets + self._pattern_shape // 2
		centers = np.where(offsets != -1, centers, -1)
		self.centers = np.flip(centers, axis=2)

	def axPaint(self, ax):
		"""Display the matches' locations on the given `ax` using matplotlib patches.
		
		Args:
		    ax (matplotlib.axes.Axes): The `Axes` to paint onto.
		"""
		pattern_h, pattern_w = self._pattern_shape

		for row, col in self._tray:
			if self.matches[row, col]:
				pos = self._tray.getPos(row, col)
				offset = self._offsets[row, col]
				score = self.scores[row, col]
				center = self.centers[row, col]
				color = _color_gradient_rgb(score)

				rect = Rectangle(pos + offset, pattern_w, pattern_h, alpha=1, fill=False, color=color)
				point = Circle(pos + center, radius=2, color=color)

				ax.add_patch(rect)
				ax.add_patch(point)
