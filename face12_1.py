# -*- coding: utf-8 -*-# 
import face_recognition as fr
# 读取图像
import cv2
import os
import numpy as np
import click
# filepath=("")
# img = face_recognition.load_image_file(filepath)
# encodings = face_recognition.face_encodings(img)

#--------preencode standard compare img----------#
rootdir = '/home/xyzgate/cq/data/'
lists = os.listdir(rootdir)

test_dir = '/home/xyzgate/cq/data_test/'
tests = os.listdir(test_dir)


student_name = {
	'1':['程祖希','Cheng zuxi'],
	'2':['郭仕鑫','Guo shixin'],
	'3':['贺子豪','He zihao'],
	'4':['金景浩','Jin jinghao'],
	'5':['李佳润','Li jiarun']
}


#calculate distance
def cal_distance(encoding_x, lists):
	encodings_x = []
	known_face_names = []
	face_distance_save = {}
	for list_1 in lists:
		face_distances = fr.face_distance(known_face_encodings_dict[str(list_1)], encoding_x)
		encodings_x.append(face_distances[np.argmin(face_distances)])
		known_face_names.append(str(list_1))

	final_name = known_face_names[np.argmin(encodings_x)]

	return final_name

if __name__ == '__main__':

	#get the encodings of known face
	print('------get the encodings of known face-------')
	known_face_encodings_dict = {}

	for list_1 in lists:
	    print('student name: {}'.format(student_name[list_1][0]))

	    list_2 = os.listdir(rootdir + str(list_1))
	    encodings = []
	    for pic_name in list_2:
	    	print('picture name: {}'.format(pic_name))
	    	img = fr.load_image_file(rootdir + str(list_1) + '/' + str(pic_name))
	    	encoding = fr.face_encodings(img)
	    	if len(encoding) > 1:
	    		click.echo("WARNING: More than one face found in {}. Only considering the first face.".format(rootdir + str(list_1)))
	    	if len(encoding) == 0:
	    		click.echo("WARNING: No faces found in {}. Ignoring file.".format(rootdir + str(list_1)))
	    		continue
	    	else:
	    		encodings.append(encoding[0])
	    	#print(encodings)

	    known_face_encodings_dict[str(list_1)] = encodings
	print('Finish!')
	
	#load test img
	print('-------------test-------------')
	for test in tests:
		print('test picture: {}'.format(test))

		img = fr.load_image_file(test_dir + str(test))
		encoding_x = fr.face_encodings(img)
		loc = fr.face_locations(img) 

		if len(encoding_x) > 1:
			click.echo("WARNING: More than one face found in {}. Only considering the first face.".format(test_dir + str(test)))
		if len(encoding_x) == 0:
			click.echo("WARNING: No faces found in {}. Ignoring file.".format(test_dir + str(test)))
			continue
		else:
			final_name = cal_distance(encoding_x[0], lists)

		for i in loc:    
			# 查找人脸位置，返回位置坐标的list, 真的只有一行哦# 遍历坐标list，给每个人脸位置画上标线框
			cv2.rectangle(img, (i[3],i[0]), (i[1],i[2]), color=(0,255,255), thickness=2)
			cv2.rectangle(img, (i[3],i[2]), (i[1],i[2]+20), color=(255,0,255), thickness=cv2.FILLED)

			font = cv2.FONT_HERSHEY_DUPLEX
			cv2.putText(img, student_name[final_name][0].encode('utf-8'), (i[3] + 6, i[2] + 15), font, 0.5, (255, 255, 20), thickness=1)
			# 保存标后的图片
		#cv2.imshow('cq_zhizhang',img[...,::-1])
		#cv2.waitKey(0)
	 	cv2.imwrite("/home/xyzgate/cq/data_result/" + str(test), img[...,::-1])
	 	print('finish write')