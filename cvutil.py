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

def downscale(img, downscale_factor):
	img_dsize = (img.shape[1]//downscale_factor, img.shape[0]//downscale_factor)
	output = cv2.resize(img, img_dsize, interpolation=cv2.INTER_AREA)
	return output

def canny(img, threshold_low, threshold_ratio=3, gaussian_kernel_size=5, sobel_kernel_size=3):
	img = cv2.GaussianBlur(img, (gaussian_kernel_size, gaussian_kernel_size))
	img = cv2.Canny(img, threshold_low, threshold_low*threshold_ratio, sobel_kernel_size)
	return img

def adaptive_threshold(img, block_radius=5, c=7):
	return cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_radius*2+1, c)


def get_transform_matrix(img):
	pass