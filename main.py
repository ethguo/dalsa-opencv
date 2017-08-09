from time import time

import cv2
import numpy as np

from detector import SensorDetector
from preprocess import downscale

def main():

	PATH_IMAGE = "img/lab/tray3.png"
	PATH_PATTERN = "img/lab/tray3_pattern.png"
	DOWNSCALE = 4
	WINDOW_NAME = "tray3"

	# FILENAME = "img/lab/tray3.png"

	# filename_pattern = "_pattern.".join(FILENAME.rsplit(".", 1))

	image = cv2.imread(PATH_IMAGE, cv2.IMREAD_COLOR)
	pattern = cv2.imread(PATH_PATTERN, cv2.IMREAD_COLOR)

	image = downscale(image, DOWNSCALE)
	pattern = downscale(pattern, DOWNSCALE)

	image = image[:,200:]

	detector = SensorDetector(pattern)

	onChange = lambda x: None # Do nothing function

	cv2.namedWindow(WINDOW_NAME)
	cv2.createTrackbar("block_radius", WINDOW_NAME, 5, 50, onChange)
	cv2.createTrackbar("c", WINDOW_NAME, 7, 50, onChange)
	cv2.createTrackbar("match_threshold_percent", WINDOW_NAME, 70, 100, onChange)
	cv2.createTrackbar("clustering_bandwidth", WINDOW_NAME, 40, 100, onChange) #permille
	# cv2.createTrackbar("match_method", WINDOW_NAME, 5, 5, onChange)

	while True:
		start_time = time()

		detector.threshold_block_radius = cv2.getTrackbarPos("block_radius", WINDOW_NAME) or 1
		detector.threshold_c = cv2.getTrackbarPos("c", WINDOW_NAME)
		detector.match_threshold = cv2.getTrackbarPos("match_threshold_percent", WINDOW_NAME) / 100
		detector.clustering_bandwidth = cv2.getTrackbarPos("clustering_bandwidth", WINDOW_NAME)

		matches, match_map = detector.detect(image)

		time_elapsed = time() - start_time
		print(time_elapsed)
		
		# print(np.amin(match_map), np.amax(match_map))

		# Display results
		result = detector.draw(image)

		# text = "Time elapsed:%9.6f   Number of sensors:%3d" %(time_elapsed, len(matches))
		text = "Number of sensors:%3d" %(len(matches))

		cv2.putText(result, text, (10, 25), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0,0,255))

		cv2.imshow(WINDOW_NAME, result)
		
		k = cv2.waitKey(1) & 0xFF
		if k == 27: # Escape key
			break

	cv2.destroyAllWindows()

if __name__ == '__main__':
	main()
	# wrapper(main)()