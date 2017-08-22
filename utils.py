import cv2
import numpy as np
import logging

from cvutils import scaleImage

def loadImage(path, scale=1):
	img = cv2.imread(path, cv2.IMREAD_COLOR)
	if img is None:
		raise FileNotFoundError("No such file: " + path)
	img = scaleImage(img, scale)
	return img

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

def findBestMatches(results):
	all_scores = np.stack([result.scores for result in results])
	best_scores = np.amax(all_scores, axis=0)
	best_matches = np.argmax(all_scores, axis=0)
	best_matches = np.where(best_scores != 0, best_matches, -1)
	return best_matches
