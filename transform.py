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


def getPerspectiveTransform(src_img, src_points, output_size=(500, 500)):
	img_corners = fourCorners(src_img.shape[:2])

	dists = np.array([np.linalg.norm(img_corner - src_points, axis=1) for img_corner in img_corners])
	correspondences = np.argmin(dists, axis=1) # img_corner i corresponds to the src_point at correspondences[i]
	assert np.unique(correspondences).shape[0] == 4

	src_points = np.array([src_points[i][::-1] for i in correspondences], dtype=np.float32)
	dst_points = fourCorners(output_size)
	print(src_points, dst_points)
	matrix = cv2.getPerspectiveTransform(src_points, dst_points)

	return PerspectiveTransform(matrix, output_size)