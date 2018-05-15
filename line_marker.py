import cv2
import glob
import os
import json

penSize = 2
pen_color = (100,255,100)
flag = ''
tmp_line_list = []
line = []

#把直线信息保存到json文件中
def save_line_list(json_name):
	with open(json_name, 'w') as f:
		json.dump(tmp_line_list, f)

def mouse_click_event(event,x,y,flags,param): #x从左到右增大，y从上到下增大
	global tmp_line_list
	global line
	(img,json_name) = param

	if event==cv2.EVENT_FLAG_LBUTTON: #点击鼠标左键，进行标记
		#cv2.circle(img,(x,y),circle_radius,circle_color,1) #画一个圆，作为标记
		line.append((x,y))
		if len(line)==2:
			tmp_line_list.append(line)
			cv2.line(img, line[0], line[1], pen_color, penSize) #绘制直线
			print(line)
			line = []
		
	elif event==cv2.EVENT_FLAG_RBUTTON: #点击鼠标右键，删除现有的最后一条直线
		line = []
		tmp_line_list.pop()
		save_line_list(json_name)
		global flag 
		flag = 'clear'
		print('cancle')

#寻找当前目录中的图片文件（后缀名是大写字母也能被找到）
pics = glob.glob(r'.\\*.jpg')
pics += glob.glob(r'.\\*.jpeg')
pics += glob.glob(r'.\\*.png')
pics += glob.glob(r'.\\*.bmp')

i = 0
while flag!='exit':
	if flag=='next':
		if i<len(pics)-1:
			i += 1
		else:
			break
	elif flag=='last' and i>0:
		i -= 1
	pic_name = pics[i].split('\\')[-1] #适用于Windows系统
	json_name = pic_name.split('.')[0]+'.json'
	cv2.namedWindow(pic_name)
	image = cv2.imread(pic_name, cv2.IMREAD_COLOR)
	print(pic_name)
	if os.path.exists(json_name): #如果文件已经存在，则根据文件的现有内容画线
		with open(json_name, 'r') as f:
			tmp_line_list = json.load(f)
		for l in tmp_line_list:
			cv2.line(image, (l[0][0],l[0][1]), (l[1][0],l[1][1]), pen_color, penSize)
			print(l)
	cv2.setMouseCallback(pic_name,mouse_click_event,(image,json_name)) #将窗口与鼠标回调函数绑定
	while(True):
		cv2.imshow(pic_name,image)
		if(flag=='cleared'):
			flag=''
			for l in tmp_line_list:
				cv2.line(image, (l[0][0],l[0][1]), (l[1][0],l[1][1]), pen_color, penSize) #重新绘制直线
		if(flag=='clear'):
			flag='cleared'
			break
		key = cv2.waitKey(20)&0xFF
		if key==ord('z'): #按z键前往下一张图片
			save_line_list(json_name)
			tmp_line_list = []
			cv2.destroyWindow(pic_name)
			flag = 'next'
			break
		elif key==ord('x'): #按x键返回上一张图片
			save_line_list(json_name)
			tmp_line_list = []
			cv2.destroyWindow(pic_name)
			flag = 'last'
			break
		elif key==27: #按esc键可以退出（如果直接按窗口的关闭按钮退出，不会保存json文件）
			save_line_list(json_name)
			cv2.destroyWindow(pic_name)
			flag = 'exit'
			break
cv2.destroyAllWindows()