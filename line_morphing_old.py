import json
import numpy as np
import cv2
import math

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

#把点的坐标从line_list[index]坐标系转换到直线B坐标系，然后计算含权重的偏移值
def get_delta(col,row,direction,index,line_B):
	if direction == 0:
		u = u_map_dest[row][col]
		v = v_map_dest[row][col]
		weight = weight_map_dest[row][col]
	else:
		u = u_map_source[row][col]
		v = v_map_source[row][col]
		weight = weight_map_source[row][col]

	(B_from,B_to) = line_B
	new_point = B_from + u*(B_to-B_from) + v*perpendicular(B_to-B_from)/len_of_line(line_B)
	delta = (new_point-np.array([col,row]))*weight
	return (delta,weight)

#把图像从对应直线组A的形状变换到对应直线组B的形状
def pic_deformation(image,direction,line_list_B):
	line_num = len(line_list_B)
	height,width,color_num = image.shape
	new_image = np.array( [ [ [0,0,0] for row in range(width) ] for col in range(height)], np.uint8 )
	for row in range(height):
		print(row)
		for col in range(width): #col对应x，row对应y
			delta_sum = np.array([0.0,0.0])
			weight_sum = 0
			for i in range(line_num):
				delta,weight = get_delta(col,row,direction,i,line_list_B[i])
				delta_sum += delta
				weight_sum += weight
			old_col = (int)(delta_sum[0]/weight_sum) + col
			old_row = (int)(delta_sum[1]/weight_sum) + row
			if old_row>=0 and old_row<=width-1 and old_col>=0 and old_col<=height-1:
				new_image[row][col] = image[old_row][old_col]

#对直线组进行插值
def line_list_interpolation(line_list_A,line_list_B,k):
	result = (1-k)*line_list_A + k*line_list_B
	'''for i in range(len(line_list_A)):
		line_A = line_list_A[i]
		line_B = line_list_B[i]
		(A_from,A_to) = line_A
		(B_from,B_to) = line_B
		new_center = ( (A_from+A_to)*0.5 + (B_from+B_to)*0.5 )*0.5
		new_len = ( len_of_line(line_A) + len_of_line(line_B) )*0.5
		result.append(line)'''
	result = np.array(result,int)
	return result

####################################################################################################

img_source = cv2.imread('wolf.jpg', cv2.IMREAD_COLOR)
line_list_source = read_lines('wolf.json')
len_list_source = []
perpendicular_list_source = []
square_list_source = []
for line in line_list_source:
	len_list_source.append(len_of_line(line))
	perpendicular_list_source.append(perpendicular(line[1]-line[0]))
	square_list_source.append(square_len_of_line(line))

img_dest = cv2.imread('dog.jpg', cv2.IMREAD_COLOR)
line_list_dest = read_lines('dog.json')
len_list_dest = []
perpendicular_list_dest = []
square_list_dest = []
for line in line_list_dest:
	len_list_dest.append(len_of_line(line))
	perpendicular_list_dest.append(perpendicular(line[1]-line[0]))
	square_list_dest.append(square_len_of_line(line))

height,width,color_num = img_source.shape
u_map_source = np.zeros(height,width)
v_map_source = np.zeros(height,width)
weight_map_source = np.zeros(height,width)
u_map_dest = np.zeros(height,width)
v_map_dest = np.zeros(height,width)
weight_map_dest = np.zeros(height,width)

for row in range(height):
	for col in range(row):
		point = np.array([col,row])

		(A_from,A_to) = line_list_dest[index]
		u = np.dot(point-A_from,A_to-A_from) / square_list_dest[index]
		u_map_dest[row][col] = u
		v = np.dot(point-A_from,perpendicular_list_dest[index]) / len_list_dest[index]
		v_map_dest[row][col] = v
		if u<0:
			dist = distance(point,A_from)
		elif u>1:
			dist = distance(point,A_to)
		else:
			dist = abs(v)
		weight = (len_of_line(line_list_dest[index])**0.1/(1+dist))**2
		#weight = (len_of_line[line_A]**p/(a+dist))**b
		#若a接近于0，直线对上的像素可精确映射，当a取较大值时，映射将变得光滑，但控制精度变差
		#b决定了随着距离dist的变大不同直线相对强度的减弱程度，若b等于0，则每个像素受所有直线同等的影响
		#p决定了直线的长度对映射的影响
		weight_map_dest[row][col] = weight

		(A_from,A_to) = line_list_source[index]
		u = np.dot(point-A_from,A_to-A_from) / square_list_source[index]
		u_map_source[row][col] = u
		v = np.dot(point-A_from,perpendicular_list_source[index]) / len_list_source[index]
		v_map_source[row][col] = v
		if u<0:
			dist = distance(point,A_from)
		elif u>1:
			dist = distance(point,A_to)
		else:
			dist = abs(v)
		weight = (len_of_line(line_list_source[index])**0.1/(1+dist))**2 #注意：这里也有weight的公式
		weight_map_source[row][col] = weight

####################################################################################################

pic_num = 3 #生成插值图片的数量
for p in range(1,pic_num+1):
	print(p,"/",pic_num)
	k = p/(pic_num+1)
	name_part = "_"+str(p)+"_"+str(pic_num)+".png"
	line_list_new = line_list_interpolation(line_list_source, line_list_dest, k)
	print(line_list_new)
	new_source = pic_deformation(img_source,1,line_list_new) #1代表line_list_source
	cv2.imwrite("source"+name_part, new_source)
	new_dest = pic_deformation(img_dest,0,line_list_new) #0代表line_list_dest
	cv2.imwrite("dest"+name_part, new_dest)
	new_image = (1-k)*new_source + k*new_dest
	cv2.imwrite("output"+name_part, new_image)

cv2.waitKey(0)
cv2.destroyAllWindows()