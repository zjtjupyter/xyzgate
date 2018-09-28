import os
import json
import base64

# rootdir = './tagpic/'
# outputdir = './orgpic/'
# list = os.listdir(rootdir) #列出文件夹下所有的目录与文件

# WEIGHT = 3840/2  
# HEIGHT = 2160/2  #new picture size
# json_save = {}

# # for dir_1 in list:
# dir_1 = '2'    #choose file name
# list_1 = os.listdir(rootdir + dir_1)        #./tagpic/1/   all name in the file
# for dir_2 in list_1:						#./tagpic/1/name
# 	file = open(rootdir + dir_1 + '/' + dir_2 + '/tag.rsl')
# 	#print(dir_2)
# 	lines = file.readlines()
# 	file.close
# 	# for s_num in range(1,int(len(lines)/5)):
# 	for s_num in range(int(2*len(lines)/5),int(3*len(lines)/5)):
# 		num_pic = lines[s_num].split(';')[0]
# 		num_state = lines[s_num].split(';')[1]
# 		num_xmin = lines[s_num].split(';')[3].split(',')[0] 
# 		num_ymin = lines[s_num].split(';')[3].split(',')[1] 
# 		num_xmax = lines[s_num].split(';')[3].split(',')[2] 
# 		num_ymax = lines[s_num].split(';')[3].split(',')[3] 
# 		#print(num_pic+'\t'+ num_state + '\t'+num_xmin+'\t'+num_ymin+'\t'+num_ymin+'\t'+num_ymax)
		
# 		s={
# 		"label": 0, 
# 		"fill_color": None,
# 		"line_color": None,
# 		"points": []
# 		}

# 		jsonfile = {
# 		"imagePath": "",
# 		"fillColor": [255,0,0,128],
# 		"flags": {},
# 		"shapes": [],
# 		"lineColor": [0,255,0,128],
# 		"imageData":""
# 		}

# 		s['label'] = num_state
# 		s['points'].append([int(float(num_xmin)*WEIGHT),int(float(num_ymin)*HEIGHT)])
# 		s['points'].append([int(float(num_xmax)*WEIGHT),int(float(num_ymin)*HEIGHT)])
# 		s['points'].append([int(float(num_xmax)*WEIGHT),int(float(num_ymax)*HEIGHT)])
# 		s['points'].append([int(float(num_xmin)*WEIGHT),int(float(num_ymax)*HEIGHT)])
		
# 		if str(num_pic) in json_save:
# 			pass
# 		else:
# 			json_save[str(num_pic)] = jsonfile
# 		if(int(num_pic)<10):
# 			picname ='0000'+num_pic+'.png'
# 		elif(int(num_pic)<100):
# 			picname ='000'+num_pic+'.png'
# 		elif(int(num_pic)<1000):
# 			picname ='00'+num_pic+'.png'
# 		else:
# 			picname ='0'+num_pic+'.png'
# 		with open(outputdir+dir_1+'/'+picname,'rb') as fpic:
# 			base64_data = base64.b64encode(fpic.read())

# 		json_save[str(num_pic)]['imagePath'] = picname      #picture name
# 		json_save[str(num_pic)]['shapes'].append(s)
# 		json_save[str(num_pic)]['imageData'] = str(base64_data,'utf8')  #need utf8 to delete b'
# 	print('Student named '+dir_2+' complete.')
# print('----------All label data saved!------------')

# for cnt_pic in json_save:
# 	#print(json_save[cnt_pic])
# 	if(int(cnt_pic)<10):
# 		jsonname ='0000'+cnt_pic+'.json'
# 	elif(int(cnt_pic)<100):
# 		jsonname ='000'+cnt_pic+'.json'
# 	elif(int(cnt_pic)<1000):
# 		jsonname ='00'+cnt_pic+'.json'
# 	else:
# 		jsonname ='0'+cnt_pic+'.json'

# 	with open(outputdir+dir_1+'/'+jsonname,"w") as f:
# 		json.dump(json_save[cnt_pic],f,sort_keys=True,indent=2,separators=(', ', ': '))

# 	print(cnt_pic+'json file finished.')
a=1
print("--------All %d Finished!-------------"%(a))


# file = open("tag.rsl")
# lines = file.readlines()
# print(lines[0][7]+'\n'+lines[0])
# print(lines[0].split(';'))

# for s_num in range(1,len(lines),20):
# 	num_pic = lines[s_num].split(';')[0]
# 	num_state = lines[s_num].split(';')[1]
# 	num_xmin = lines[s_num].split(';')[3].split(',')[0]
# 	num_ymin = lines[s_num].split(';')[3].split(',')[1]
# 	num_xmax = lines[s_num].split(';')[3].split(',')[2]
# 	num_ymax = lines[s_num].split(';')[3].split(',')[3]
# 	print(num_pic+'\t'+ num_state + '\t'+num_xmin+'\t'+num_ymin+'\t'+num_ymin+'\t'+num_ymax)


# file = open('tag.rsl')
# lines = file.readlines()
# file.close
# s_num = 1



# WEIGHT = 3840
# HEIGHT = 2160
# json = {}


# for s_num in range(1,len(lines),400):
# 	num_pic = lines[s_num].split(';')[0]
# 	num_state = lines[s_num].split(';')[1]
# 	num_xmin = lines[s_num].split(';')[3].split(',')[0] 
# 	num_ymin = lines[s_num].split(';')[3].split(',')[1] 
# 	num_xmax = lines[s_num].split(';')[3].split(',')[2] 
# 	num_ymax = lines[s_num].split(';')[3].split(',')[3] 
# 	#print(num_pic+'\t'+ num_state + '\t'+num_xmin+'\t'+num_ymin+'\t'+num_ymin+'\t'+num_ymax)
	
# 	s={"label": 0, "fill_color": 'null',"line_color": 'null',"points": []}
# 	jsonfile = {"imagePath": str(num_pic)+".jpg","fillColor": [255,0,0,128],"flags": {},"shapes": [],"lineColor": [0,255,0,128]}

# 	s['label'] = num_state
# 	s['points'].append([int(float(num_xmin)*WEIGHT),int(float(num_ymin)*HEIGHT)])
# 	s['points'].append([int(float(num_xmax)*WEIGHT),int(float(num_ymin)*HEIGHT)])
# 	s['points'].append([int(float(num_xmax)*WEIGHT),int(float(num_ymax)*HEIGHT)])
# 	s['points'].append([int(float(num_xmin)*WEIGHT),int(float(num_ymax)*HEIGHT)])
	
# 	if str(num_pic) in json:
# 		continue
# 	else:
# 		json[str(num_pic)] = jsonfile
	
# 	json[str(num_pic)]['shapes'].append(s)
# 	print(json)

# if json[str(pic)] is None:
# 	json[str(pic)] = jsonfile


# num_pic = lines[s_num].split(';')[0]
# num_state = lines[s_num].split(';')[1]
# num_xmin = lines[s_num].split(';')[3].split(',')[0] 
# num_ymin = lines[s_num].split(';')[3].split(',')[1] 
# num_xmax = lines[s_num].split(';')[3].split(',')[2] 
# num_ymax = lines[s_num].split(';')[3].split(',')[3] 

# #print(num_pic+'\t'+ num_state + '\t'+num_xmin+'\t'+num_ymin+'\t'+num_ymin+'\t'+num_ymax)
# s['label'] = num_state
# s['points'].append([int(float(num_xmin)*WEIGHT),int(float(num_ymin)*HEIGHT)])
# s['points'].append([int(float(num_xmax)*WEIGHT),int(float(num_ymin)*HEIGHT)])
# s['points'].append([int(float(num_xmax)*WEIGHT),int(float(num_ymax)*HEIGHT)])
# s['points'].append([int(float(num_xmin)*WEIGHT),int(float(num_ymax)*HEIGHT)])

# #jsonfile['shapes'].append(s)
# json[str(pic)]['shapes'].append(s)
# print(json)