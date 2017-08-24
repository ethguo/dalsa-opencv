"""A collection of convenience wrappers around useful cv2 functions"""
import cv2


def scaleImage(img, scale):
	if scale < 1: # Pick the right interpolation method for scaling up or down
		interpolation = cv2.INTER_AREA
	else:
		interpolation = cv2.INTER_CUBIC

	new_size = (int(img.shape[1]*scale), int(img.shape[0]*scale))
	output = cv2.resize(img, new_size, interpolation=interpolation)
	return output

def getHsv(img):
	img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	channels = cv2.split(img_hsv)
	return channels

def getHue(img):
	return getHsv(img)[0]

def getSat(img):
	return getHsv(img)[1]

def getVal(img):
	return getHsv(img)[2]

def blur(img, kernel_size=5):
	return cv2.GaussianBlur(img, (kernel_size, kernel_size))

def canny(img, threshold_low, threshold_ratio=3, gaussian_kernel_size=5, sobel_kernel_size=3):
	img = blur(img, gaussian_kernel_size)
	img = cv2.Canny(img, threshold_low, threshold_low*threshold_ratio, sobel_kernel_size)
	return img

def colorToGrayscale(img):
	return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def adaptiveThreshold(img, block_radius=5, c=7):
	img = colorToGrayscale(img)
	img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_radius*2+1, c)
	return img
