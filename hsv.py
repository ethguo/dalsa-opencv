import cv2
import numpy as np

def get_hsv(img):
	img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	img_hsv_channels = cv2.split(img_hsv)
	return img_hsv_channels

def get_hue(img):
	return get_hsv(img)[0]

def get_sat(img):
	return get_hsv(img)[1]

def get_val(img):
	return get_hsv(img)[2]


def sat_mask(img, block_radius=5, c=7):
	img_sat = get_sat(img)

	output = cv2.adaptiveThreshold(img_sat, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_radius*2+1, c)

	return output


# Demo
if __name__ == "__main__":

	img = cv2.imread("img/allsensors.png", cv2.IMREAD_COLOR)

	onChange = lambda x: None # Do nothing function

	cv2.namedWindow("sat_mask")
	cv2.createTrackbar("block_radius", "sat_mask", 5, 50, onChange)
	cv2.createTrackbar("c", "sat_mask", 7, 50, onChange)

	while True:

		block_radius = cv2.getTrackbarPos("block_radius", "sat_mask") or 1
		c = cv2.getTrackbarPos("c", "sat_mask")

		output = sat_mask(img, block_radius, c)

		# Display results
		# cv2.imshow("original", img)
		cv2.imshow("sat_mask", output)

		k = cv2.waitKey(1) & 0xFF
		if k == 27: # Escape key
			break

	cv2.destroyAllWindows()
