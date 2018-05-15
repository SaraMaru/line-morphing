import json
import numpy as np
import cv2
import math

#为提高速度而使用的全局变量，实际上是当作临时变量使用的
len_list_source = []
perpendicular_list_source = []
len_list_dest = []
perpendicular_list_dest = []
square_list_dest = []

#从json文件中读取特征线
def read_lines(json_name):
	with open(json_name,'r') as f:
		lines = json.load(f)
	print(json_name)
	print(len(lines),'lines')
	print(lines)
	return np.array(lines)

#两点间的距离
def distance(pointA,pointB):
	vector = pointB - pointA
	return (vector[0]**2+vector[1]**2)**0.5

#返回一长度与输入的矢量相等且与输入矢量垂直的矢量
def perpendicular(vector): #vector是二维矢量
	return np.array([vector[1],-vector[0]])
	#return np.array(-vector[1],vector[0])

#直线的长度
def len_of_line(line):
	vector = line[1]-line[0]
	len = 0
	for i in vector:
		len += i**2
	len = len**0.5
	return len

#直线的长度的平方
def square_len_of_line(line):
	vector = line[1]-line[0]
	result = 0
	for i in vector:
		result += i**2
	return result

#把点的坐标从直线A坐标系转换到直线B坐标系
def get_new_pos(point,line_A,line_B):
	(A_from,A_to) = line_A
	(B_from,B_to) = line_B
	u = np.dot(point-A_from,A_to-A_from) / square_len_of_line(line_A)
	v = np.dot(point-A_from,perpendicular(A_to-A_from)) / len_of_line(line_A)
	new_point = B_from + u*(B_to-B_from) + v*perpendicular(B_to-B_from)/len_of_line(line_B)
	return new_point

#把点的坐标从目标直线坐标系转换到源直线坐标系，然后计算含权重的偏移值
def get_delta(point,index):
	global len_list_source
	global perpendicular_list_source
	global len_list_dest
	global perpendicular_list_dest
	global square_list_dest
	(A_from,A_to) = line_list_dest[index]
	(B_from,B_to) = line_list_source[index]
	u = np.dot(point-A_from,A_to-A_from) / square_list_dest[index]
	v = np.dot(point-A_from,perpendicular_list_dest[index]) / len_list_dest[index]
	new_point = B_from + u*(B_to-B_from) + v*perpendicular_list_source[index]/len_list_source[index]
	if u<0:
		dist = distance(point,A_from)
	elif u>1:
		dist = distance(point,A_to)
	else:
		dist = abs(v)
	weight = (len_list_dest[index]**0.05/(2+dist))**1.5
	#weight = (len_list_dest[index]**p/(a+dist))**b
	#若a接近于0，直线对上的像素可精确映射，当a取较大值时，映射将变得光滑，但控制精度变差
	#b决定了随着距离dist的变大不同直线相对强度的减弱程度，若b等于0，则每个像素受所有直线同等的影响
	#p决定了直线的长度对映射的影响
	delta = (new_point-point)*weight
	return (delta,weight)

#把图像中的每一点从对应直线组A（目标）的坐标变换到对应直线组B（源）的坐标
def pic_deformation(image,line_list_A,line_list_B):
	global len_list_source
	global perpendicular_list_source
	global len_list_dest
	global perpendicular_list_dest
	global square_list_dest
	height,width,color_num = image.shape
	len_list_source = []
	perpendicular_list_source = []
	for line in line_list_B:
		len_list_source.append(len_of_line(line))
		perpendicular_list_source.append(perpendicular(line[1]-line[0]))
	len_list_dest = []
	perpendicular_list_dest = []
	square_list_dest = []
	for line in line_list_A:
		len_list_dest.append(len_of_line(line))
		perpendicular_list_dest.append(perpendicular(line[1]-line[0]))
		square_list_dest.append(square_len_of_line(line))

	line_num = len(line_list_A)
	new_image = np.array( [ [ [0,0,0] for row in range(width) ] for col in range(height)], np.uint8 )
	for row in range(height):
		print(row)
		for col in range(width): #col对应x，row对应y
			delta_sum = np.array([0.0,0.0])
			weight_sum = 0
			for i in range(line_num):
				delta,weight = get_delta(np.array([col,row]),i) #delta已经带有权重，不用再乘
				delta_sum += delta
				weight_sum += weight
			old_col = (int)(delta_sum[0]/weight_sum) + col
			old_row = (int)(delta_sum[1]/weight_sum) + row
			if old_row>=0 and old_row<=width-1 and old_col>=0 and old_col<=height-1:
				new_image[row][col] = image[old_row][old_col]
	return new_image

#对直线组进行插值
#直接对端点进行插值，如果不怕麻烦，使用矢量线性插值效果更好
def line_list_interpolation(line_list_A,line_list_B,k):
	result = (1-k)*line_list_A + k*line_list_B
	result = np.array(result,int)
	return result

####################################################################################################

img_source = cv2.imread('now.png', cv2.IMREAD_COLOR)
line_list_source = read_lines('now.json')

img_dest = cv2.imread('then.png', cv2.IMREAD_COLOR)
line_list_dest = read_lines('then.json')

pic_num = 18 #生成插值图片的数量
for p in range(1,pic_num+1):
	name_part = "_"+str(p)+"_"+str(pic_num)+".png"
	k = p/(pic_num+1)
	line_list_new = line_list_interpolation(line_list_source, line_list_dest, k)
	new_source = pic_deformation(img_source,line_list_new,line_list_source)
	cv2.imwrite("source"+name_part, new_source)
	new_dest = pic_deformation(img_dest,line_list_new,line_list_dest)
	cv2.imwrite("dest"+name_part, new_dest)
	new_image = (1-k)*new_source + k*new_dest
	cv2.imwrite("output"+name_part, new_image)

'''new_image = pic_deformation(img_source,line_list_dest,line_list_source)
cv2.imshow("Result", new_image)'''
cv2.waitKey(0)
cv2.destroyAllWindows()