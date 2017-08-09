import cv2
import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth

from preprocess import *
from hsv import *

class SensorDetectorResult:
	def __init__(self, sensorDetector, matches, match_map):
		self.matches = matches
		self.match_map = match_map

		self.scores = match_map[tuple(np.transpose(matches))]
		self.rss = np.sum(1 - self.scores)
		self.rsquared = self.rss / len(self)

		self.pattern_shape = sensorDetector.pattern.shape[:2]		
		self._color_gradient = lambda val: (0, val*2*255, 255) if val < 0.5 else (0, 255, (1-val)*2*255) #BGR

	def __len__(self):
		return len(self.matches)

	def __getitem__(self, key):
		return self.matches[key]

	def __iter__(self):
		return iter(self.matches)

	def paint(self, image):
		draw_image = np.copy(image)

		pattern_h, pattern_w = self.pattern_shape

		for match, score in zip(self.matches, self.scores):
			y, x = match

			color = self._color_gradient(score)

			cv2.rectangle(draw_image, 
				(x, y), (x + pattern_w, y + pattern_h),
				color=color, thickness=1)

			cv2.circle(draw_image,
				(x + pattern_w//2, y + pattern_h//2), radius=2,
				color=color, thickness=-1)

		text1 = "Number of sensors:%3d" %(len(self.matches))
		text2 = "Average r-squared:%9.6f" %(self.rsquared)
		text3 = "RSS:%9.6f" %(self.rss)
		cv2.putText(draw_image, text1, (10, 25), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0,0,255))
		cv2.putText(draw_image, text2, (10, 50), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0,0,255))
		cv2.putText(draw_image, text3, (10, 75), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0,0,255))

		return draw_image 	

	# def score(self, y, x):
	# 	return self.match_map[y, x]

	# def _color_gradient(self, val):
	# 	if val < 0.5:
	# 		r = 255
	# 		g = val * 2 * 255
	# 	else:
	# 		r = (1 - val) * 2 * 255
	# 		g = 255
	# 	return (0, g, r)


class SensorDetector:
	def __init__(self, pattern, params=None, **kwargs):
		# Available parameters
		self.preprocess = lambda x: x
		self.pattern = pattern
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

		# Preprocess pattern
		self.pattern_proc = self.preprocess(self.pattern)

		self.clusterer = MeanShift(self.clustering_bandwidth)

	# def preprocess(self, image):
	# 	output = image #skip

	# 	# output = canny(image, 32)
	# 	# output = sat_mask(image, self.threshold_block_radius, self.threshold_c)
	# 	# output = get_sat(image)

	# 	return output

	def detect(self, image):
		image_proc = self.preprocess(image)

		match_map = cv2.matchTemplate(image_proc, self.pattern_proc, self.match_method)

		candidate_matches = np.transpose(np.where(match_map >= self.match_threshold))

		if 0 in candidate_matches.shape:
			raise Warning("0 matches detected")
			return np.array([]), match_map

		self.clusterer.set_params(bandwidth=self.clustering_bandwidth)
		self.clusterer.fit(candidate_matches)
		labels = self.clusterer.labels_
		centers = self.clusterer.cluster_centers_

		# print(len(np.unique(labels)))

		matches = np.int_(centers)

		# cv2.imshow("pattern_proc", pattern_proc)
		# cv2.imshow("image_proc", image_proc)

		return SensorDetectorResult(self, matches, match_map)
