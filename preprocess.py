import cv2
import numpy as np

def downscale(img, downscale_factor):
	img_dsize = (img.shape[1]//downscale_factor, img.shape[0]//downscale_factor)
	output = cv2.resize(img, img_dsize, interpolation=cv2.INTER_AREA)

	return output

def canny(img, threshold_low, threshold_ratio=3, aperture=3):
	return cv2.Canny(img, threshold_low, threshold_low*threshold_ratio, aperture)


# Demo
if __name__ == "__main__":
	from hsv import *

	WINDOW_NAME = "canny"

	img = cv2.imread("img/lab/tray1.png", cv2.IMREAD_COLOR)
	img = downscale(img, 4)
	img = get_val(img)

	onChange = lambda x: None # Do nothing function

	cv2.namedWindow(WINDOW_NAME)
	cv2.createTrackbar("t_low", WINDOW_NAME, 127, 255, onChange)
	cv2.createTrackbar("t_ratio", WINDOW_NAME, 3, 20, onChange)
	cv2.createTrackbar("aperture", WINDOW_NAME, 3, 20, onChange)

	while True:

		threshold_low = cv2.getTrackbarPos("t_low", WINDOW_NAME)
		threshold_ratio = cv2.getTrackbarPos("t_ratio", WINDOW_NAME)
		aperture = cv2.getTrackbarPos("aperture", WINDOW_NAME)

		output = canny(img, threshold_low, threshold_ratio, aperture)
		# output = img

		# Display results
		# cv2.imshow("original", img)
		cv2.imshow(WINDOW_NAME, output)

		k = cv2.waitKey(1) & 0xFF
		if k == 27: # Escape key
			break

	cv2.destroyAllWindows()
