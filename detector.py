import cv2
import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth

from preprocess import *
from hsv import *

class SensorDetector:
	def __init__(self, pattern, params=None, **kwargs):
		self.pattern = pattern
		self.threshold_block_radius = 5
		self.threshold_c = 7
		self.match_method = cv2.TM_CCOEFF_NORMED
		self.match_threshold = 0.8
		self.clustering_bandwidth = 40

		# Use either params dict or kwargs to seed parameters
		if not params:
			params = kwargs

		for k,v in params.items():
			if k in self.__dict__:
				self.__dict__[k] = v
			else:
				raise AttributeError("Unknown parameter: " + k)

		self.clusterer = MeanShift(self.clustering_bandwidth)

	def preprocess(self, image):
		output = image #skip

		# output = canny(image, 32)
		# output = sat_mask(image, self.threshold_block_radius, self.threshold_c)
		# output = get_sat(image)

		return output

	def detect(self, image):
		pattern_proc = self.preprocess(self.pattern)
		image_proc = self.preprocess(image)

		match_map = cv2.matchTemplate(image_proc, pattern_proc, self.match_method)

		matches = np.transpose(np.where(match_map >= self.match_threshold))

		if 0 in matches.shape:
			raise Warning("0 matches detected")
			return np.array([]), match_map

		# print(self.clustering_bandwidth)

		self.clusterer.set_params(bandwidth=self.clustering_bandwidth)
		self.clusterer.fit(matches)
		labels = self.clusterer.labels_
		centers = self.clusterer.cluster_centers_

		# print(len(np.unique(labels)))

		points = np.int_(centers)

		# cv2.imshow("pattern_proc", pattern_proc)
		# cv2.imshow("image_proc", image_proc)

		return points, match_map

	def draw(self, image):
		matches, match_map = self.detect(image)
		draw_image = np.copy(image)

		pattern_h, pattern_w = self.pattern.shape[:2]

		color_gradient = lambda val: (0, val*510, 255) if val < 0.5 else (0, 255, (1-val)*510)

		for pt_y, pt_x in matches:
			color = color_gradient(match_map[pt_y, pt_x])
			cv2.rectangle(draw_image, 
				(pt_x, pt_y), (pt_x + pattern_w, pt_y + pattern_h),
				color, 1)

			cv2.circle(draw_image,
				(pt_x + pattern_w//2, pt_y + pattern_h//2),
				2, color, -1)

			# cv2.putText()

		return draw_image

	# def color_gradient(self, val):
	# 	if val < 0.5:
	# 		r = 255
	# 		g = val * 2 * 255
	# 	else:
	# 		r = (1 - val) * 2 * 255
	# 		g = 255
	# 	return (0, g, r)