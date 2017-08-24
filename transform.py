import cv2
import numpy as np


class PerspectiveTransform:
	def __init__(self, matrix, shape):
		self.matrix = matrix
		self.shape = shape

	def transformImage(self, img):
		return cv2.warpPerspective(img, self.matrix, self.shape)

	def transformPoints(self, points):
		return cv2.perspectiveTransform(points, self.matrix)

	def __call__(self, arg):
		if arg.shape[1] == 2 and arg.ndim == 2:
			return self.transformPoints(arg)
		elif arg.ndim == 2 or arg.ndim == 3:
			return self.transformImage(arg)
		else:
			raise TypeError("Argument not recognized as an image array or points (sparse) array.")

	def __repr__(self):
		return repr(self.matrix)

	def __str__(self):
		return str(self.matrix)


def getPerspectiveTransform(src_img, src_points, output_shape):
	"""Gets the transform matrix that will map the 4 points `src_points` to the four corners of a flat plane of shape `output_shape`.
	
	Args:
	    src_img (numpy.ndarray): Image that `src_points` are from.
	    src_points (numpy.ndarray): Four points describing the four corners of the output plane (`shape=(4,2)`).
	    output_shape (tuple): `(height, width)` of the output plane.
	
	Returns:
	    PerspectiveTransform: `PerspectiveTransform` object encapsulating the resulting transform matrix.
	"""
	output_shape = (output_shape[1], output_shape[0])
	
	# Determine which input points correspond to which of the 4 corners
	img_corners = _fourCorners(src_img.shape[:2])
	dists = np.array([np.linalg.norm(img_corner - src_points, axis=1) for img_corner in img_corners])
	correspondences = np.argmin(dists, axis=1) # img_corner i corresponds to the src_point at correspondences[i]
	assert np.unique(correspondences).shape[0] == 4

	src = np.array([src_points[i] for i in correspondences], dtype=np.float32)
	dst = _fourCorners(output_shape)

	matrix = cv2.getPerspectiveTransform(src, dst)

	return PerspectiveTransform(matrix, output_shape)


def _fourCorners(*args):
	"""Returns an `numpy.ndarray` of the four corners of an axis-aligned box.
	
	Args:
	    *args: One or two iterables of length 2:
	        * If given one argument `(x, y)`, The box has one corner at `(0, 0)` and the other at `(x, y)`.
	        * If given two arguments `(x1, y1)`, `(x2, y2)`, The box has one corner at `(x1, y1)` and the other at `(x2, y2)`.
	"""
	if len(args) == 1:
		a = (0, 0)
		b = args[0]
	elif len(args) == 2:
		a = args[0]
		b = args[1]
	else:
		raise TypeError("Expected 1 or 2 arguments (%d given)" %len(args))

	return np.array((
		(a[0], a[1]),
		(a[0], b[1]),
		(b[0], b[1]),
		(b[0], a[1])
		), dtype=np.float32)
