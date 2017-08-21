import cv2
import numpy as np
import logging

def loadImage(path, scale=1):
	img = cv2.imread(path, cv2.IMREAD_COLOR)
	if img is None:
		raise FileNotFoundError("No such file: " + path)
	img = scaleImage(img, scale)
	return img

def scaleImage(img, scale):
	if scale < 1:
		interpolation = cv2.INTER_AREA
	else:
		interpolation = cv2.INTER_CUBIC

	new_size = (int(img.shape[1]*scale), int(img.shape[0]*scale))
	output = cv2.resize(img, new_size, interpolation=interpolation)
	return output

def axShowImage(ax, img, cmap="gray"):
	ax.clear()
	if img.ndim == 3 and img.shape[2] == 3:
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		ax.imshow(img)
	else:
		ax.imshow(img, cmap=cmap)

def axPaint(ax, matches):
	if matches:
		matches.axPaint(ax)
	else:
		logging.warning("Cannot axPaint: No matches")

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

def fourCorners(*args):
	"""Returns an `numpy.ndarray` of the four corners of an axis-aligned box.
	
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
		(b[0], b[1]),
		(b[0], a[1])
		), dtype=np.float32)
