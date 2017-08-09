import cv2
import numpy as np

def get_hsv(image):
	image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	image_hsv_channels = cv2.split(image_hsv)
	return image_hsv_channels

def get_hue(image):
	return get_hsv(image)[0]

def get_sat(image):
	return get_hsv(image)[1]

def get_val(image):
	return get_hsv(image)[2]


def sat_mask(image, block_radius=5, c=7):
	image_sat = get_sat(image)

	output = cv2.adaptiveThreshold(image_sat, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_radius*2+1, c)

	return output


# Demo
if __name__ == "__main__":

	image = cv2.imread("img/allsensors.png", cv2.IMREAD_COLOR)

	onChange = lambda x: None # Do nothing function

	cv2.namedWindow("sat_mask")
	cv2.createTrackbar("block_radius", "sat_mask", 5, 50, onChange)
	cv2.createTrackbar("c", "sat_mask", 7, 50, onChange)

	while True:

		block_radius = cv2.getTrackbarPos("block_radius", "sat_mask") or 1
		c = cv2.getTrackbarPos("c", "sat_mask")

		output = sat_mask(image, block_radius, c)

		# Display results
		# cv2.imshow("original", image)
		cv2.imshow("sat_mask", output)

		k = cv2.waitKey(1) & 0xFF
		if k == 27: # Escape key
			break

	cv2.destroyAllWindows()
