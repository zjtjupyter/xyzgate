# -*- coding: utf-8 -*-# 
import face_recognition as fr
# 读取图像
import cv2
import numpy as np
# filepath=("")
# img = face_recognition.load_image_file(filepath)
# encodings = face_recognition.face_encodings(img)
face_locations = []
face_encodings = []
face_names = []
img = fr.load_image_file("/home/xyzgate/cq/00107.png")
encoding_x = fr.face_encodings(img)[0]
# 加载图片保存为numpy数组
loc = fr.face_locations(img)  
# 查找人脸位置，返回位置坐标的list, 真的只有一行哦# 遍历坐标list，给每个人脸位置画上标线框
img_a = fr.load_image_file("/home/xyzgate/cq/00140.png")
encoding_a = fr.face_encodings(img_a)[0]
img_b = fr.load_image_file("/home/xyzgate/cq/高一1班/标注图片/ch03/20170918073000/高一/1班/物理_20170918073000/程祖希/1/00075.png")
encoding_b = fr.face_encodings(img_b)[0]
img_c = fr.load_image_file("/home/xyzgate/cq/高一1班/标注图片/ch03/20170918073000/高一/1班/物理_20170918073000/程祖希/1/00075.png")
encoding_c = fr.face_encodings(img_c)[0]
known_face_names = [
    
    "guoshixin","chengzuxi",'123'
]
encodings = [encoding_a, encoding_b,encoding_c]
face_names = []
face_distances = fr.face_distance(encodings, encoding_x)
index=np.argmin(face_distances)
	# matches = fr.compare_faces([encoding_a, encoding_b], encoding_x)
	# name = "Unknown"
	# if True in matches:
		# first_match_index = matches.index(True)
name = known_face_names[index]
face_names.append(name)
for i in loc:    
	
	

	cv2.rectangle(img, (i[3],i[0]), (i[1],i[2]), color=(0,255,255), thickness=2)
	# cv2.rectangle(img, (i[3],i[2]-35), (i[1],i[0]), color=(0,255,255), cv2.FILLED)
	
	font = cv2.FONT_HERSHEY_DUPLEX
	cv2.putText(img, name, (i[3] + 6, i[2] + 12), font, 0.5, (255, 0, 255), 1)
	# 保存标后的图片
cv2.imwrite("/home/xyzgate/cq/test_result1.jpg", img[...,::-1])
    










# img_a = fr.load_image_file("tmp/fanbingbing.jpg")
# img_b = fr.load_image_file(tmp/fanchenchen.jpg)
# img_c = fr.load_image_file(tmp/jingtian.jpg)
# img_d = fr.load_image_file(tmp/mingrihuayiluo.jpg)
# img_x = fr.load_image_file(tmp/test01.jpg)
# # 进行特征编码
# encoding_a = fr.face_encodings(img_a)[0]
# encoding_b = fr.face_encodings(img_b)[0]
# encoding_c = fr.face_encodings(img_c)[0]
# encoding_d = fr.face_encodings(img_d)[0]
# encoding_x = fr.face_encodings(img_x)[0]
# # 将示例图片与目标人脸逐一比照，返回 list, 包含True/False, 表示能否匹配
# fr.compare_faces([encoding_a, encoding_b, encoding_c, encoding_d], encoding_x)
# # 返回 [True, True, True, False]# 我擦，不对啊，怎样第2，3张也是True。# 差值默认为0.5，越小比照越严格
# fr.compare_faces([encoding_a, encoding_b, encoding_c, encoding_d], encoding_x, tolerance=0.4)
# # 返回值[True, False, False, False]，得知目标人脸属于范爷</code>