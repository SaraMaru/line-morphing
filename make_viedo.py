import cv2
import glob

pics = glob.glob(r'.\\*.png')
print(pics)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter("out.avi",fourcc, 20, (128,128))
for i in range(10):
	img = cv2.imread(pics[0], cv2.IMREAD_COLOR)
	out.write(img)
for pic in pics:
	img = cv2.imread(pic, cv2.IMREAD_COLOR)
	out.write(img)
	out.write(img)
for i in range(10):
	img = cv2.imread(pics[-1], cv2.IMREAD_COLOR)
	out.write(img)
out.release()