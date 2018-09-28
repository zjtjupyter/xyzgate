# -*- coding: utf-8 -*-# 
import face_recognition as fr
# 读取图像
import cv2
import os
import numpy as np
# filepath=("")
# img = face_recognition.load_image_file(filepath)
# encodings = face_recognition.face_encodings(img)

#--------preencode standard compare img----------#
rootdir = ('/home/xyzgate/cq/data/')
lists = os.listdir(rootdir)
known_face_encodings_dict = {}

print(lists)

for list_1 in lists:
    print(list_1)
    print(type(list_1))
    list_2 = os.listdir(rootdir + str(list_1))
    
    encodings = []

    for pic_name in list_2:
        print(pic_name)
        img = fr.load_image_file(rootdir + str(list_1) + '/' + str(pic_name))
        encoding = fr.face_encodings(img)[0]
        encodings.append(encoding)
        #print(encodings)

    known_face_encodings_dict[str(list_1)] = encodings
    

# print(known_face_encodings_dict)


#load test img
face_names = []
img = fr.load_image_file("/home/xyzgate/cq/00107.png")
encoding_x = fr.face_encodings(img)[0]
# 加载图片保存为numpy数组
loc = fr.face_locations(img) 


#calculate distance
encodings_x = []
known_face_names = []
face_distance_save = {}
for list_1 in lists:
    face_distances = fr.face_distance(known_face_encodings_dict[str(list_1)], encoding_x)
    encodings_x.append(face_distances[np.argmin(face_distances)])
    known_face_names.append(str(list_1))
    # face_distance_save[str(list_1)] = face_distances[index]

final_name = known_face_names[np.argmin(encodings_x)]
# face_names.append(final_name)

for i in loc:    
    # 查找人脸位置，返回位置坐标的list, 真的只有一行哦# 遍历坐标list，给每个人脸位置画上标线框
    cv2.rectangle(img, (i[3],i[0]), (i[1],i[2]), color=(0,255,255), thickness=2)
    cv2.rectangle(img, (i[3],i[2]), (i[1],i[2]+20), color=(255,0,255), thickness=cv2.FILLED)

    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(img, final_name, (i[3] + 6, i[2] + 15), font, 0.5, (255, 255, 20), thickness=1)
    # 保存标后的图片
cv2.imshow('cq_zhizhang',img[...,::-1])
cv2.waitKey(0)
# cv2.imwrite("/home/xyzgate/cq/test_result1.jpg", img[...,::-1])