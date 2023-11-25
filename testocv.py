import cv2

cam = cv2.VideoCapture(0)

while True:
	ret, image = cam.read()
	cv2.imwrite('./Imagetest.jpg',image)
	break
cv2.imwrite('testimage.jpg', image)
cam.release()
cv2.destroyAllWindows()
