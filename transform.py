import cv2
import numpy as np

from cvutil import fourCorners

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
	"""Summary
	
	Args:
	    src_img (TYPE): Description
	    src_points (TYPE): Description
	    output_shape (tuple): (height, width) of final image.
	
	Returns:
	    TYPE: Description
	"""
	output_shape = (output_shape[1], output_shape[0])
	src_points = np.flip(src_points, axis=1)
	
	img_corners = fourCorners(src_img.shape[:2])

	sum_ = np.sum(src_points, axis=1)	
	diff = np.diff(src_points, axis=1)
	src_ordered = np.array((
		src_points[np.argmin(sum_)],
		src_points[np.argmax(diff)],
		src_points[np.argmax(sum_)],
		src_points[np.argmin(diff)]
		), dtype=np.float32)

	# dists = np.array([np.linalg.norm(img_corner - src_points, axis=1) for img_corner in img_corners])
	# correspondences = np.argmin(dists, axis=1) # img_corner i corresponds to the src_point at correspondences[i]
	# assert np.unique(correspondences).shape[0] == 4

	# src_points = np.array([src_points[i] for i in correspondences], dtype=np.float32)
	dst = fourCorners(output_shape)
	print(src_ordered)
	print(dst)
	matrix = cv2.getPerspectiveTransform(src_ordered, dst)

	return PerspectiveTransform(matrix, output_shape)