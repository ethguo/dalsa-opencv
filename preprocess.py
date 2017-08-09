import cv2
import numpy as np

def downscale(image, downscale_factor):
	image_dsize = (image.shape[1]//downscale_factor, image.shape[0]//downscale_factor)
	output = cv2.resize(image, image_dsize, interpolation=cv2.INTER_AREA)

	return output

def canny(image, threshold_low, threshold_ratio=3, aperture=3):
	return cv2.Canny(image, threshold_low, threshold_low*threshold_ratio, aperture)


# Demo
if __name__ == "__main__":
	from hsv import *

	WINDOW_NAME = "canny"

	image = cv2.imread("img/lab/tray1.png", cv2.IMREAD_COLOR)
	image = downscale(image, 4)
	image = get_val(image)

	onChange = lambda x: None # Do nothing function

	cv2.namedWindow(WINDOW_NAME)
	cv2.createTrackbar("t_low", WINDOW_NAME, 127, 255, onChange)
	cv2.createTrackbar("t_ratio", WINDOW_NAME, 3, 20, onChange)
	cv2.createTrackbar("aperture", WINDOW_NAME, 3, 20, onChange)

	while True:

		threshold_low = cv2.getTrackbarPos("t_low", WINDOW_NAME)
		threshold_ratio = cv2.getTrackbarPos("t_ratio", WINDOW_NAME)
		aperture = cv2.getTrackbarPos("aperture", WINDOW_NAME)

		output = canny(image, threshold_low, threshold_ratio, aperture)
		# output = image

		# Display results
		# cv2.imshow("original", image)
		cv2.imshow(WINDOW_NAME, output)

		k = cv2.waitKey(1) & 0xFF
		if k == 27: # Escape key
			break

	cv2.destroyAllWindows()
