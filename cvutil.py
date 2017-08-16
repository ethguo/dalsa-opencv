import cv2
import numpy as np

def aximshow(ax, img, cmap="gray"):
	if img.ndim == 3 and img.shape[2] == 3:
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		ax.imshow(img)
	else:
		ax.imshow(img, cmap=cmap)

def getHsv(img):
	img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	img_hsv_channels = cv2.split(img_hsv)
	return img_hsv_channels

def getHue(img):
	return getHsv(img)[0]

def getSat(img):
	return getHsv(img)[1]

def getVal(img):
	return getHsv(img)[2]

def downscale(img, downscale_factor):
	img_dsize = (img.shape[1]//downscale_factor, img.shape[0]//downscale_factor)
	output = cv2.resize(img, img_dsize, interpolation=cv2.INTER_AREA)
	return output

def canny(img, threshold_low, threshold_ratio=3, gaussian_kernel_size=5, sobel_kernel_size=3):
	img = cv2.GaussianBlur(img, (gaussian_kernel_size, gaussian_kernel_size))
	img = cv2.Canny(img, threshold_low, threshold_low*threshold_ratio, sobel_kernel_size)
	return img

def adaptiveThreshold(img, block_radius=5, c=7):
	return cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_radius*2+1, c)


def fourCorners(*args):
	"""Returns an `np.ndarray` of the four corners of an axis-aligned box.
	
	Args:
	    *args: One or two iterables of length 2:
	        * If given one argument `(x, y)`, The box has one corner at `(0, 0)` and the other at `(x, y)`.
	        * If given two arguments `(x1, y1)`, `(x2, y2)`, The box has one corner at `(x1, y1)` and the other at `(x2, y2)`.
	"""
	if len(args) == 1:
		a = (0, 0)
		b = args[0]
	elif len(args) == 2:
		a = args[0]
		b = args[1]
	else:
		raise TypeError("Expected 1 or 2 arguments (%d given)" %len(args))

	return np.array((
		(a[0], a[1]),
		(a[0], b[1]),
		(b[0], a[1]),
		(b[0], b[1])
		), dtype=np.float32)
