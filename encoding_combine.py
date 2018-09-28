# -*- coding: utf-8 -*-# 
import face_recognition as fr
import cv2
import os
import numpy as np
import click
import shutil
import json
#--------preencode standard compare img----------#
# rootdir = '/home/xyzgate/cq/ttttest/'
rootdir = '/data/result-videos/'
lists = os.listdir(rootdir)

# test_dir = '/home/xyzgate/cq/ttttest/'
test_dir = '/data/result-videos/'
tests = os.listdir(test_dir)

distances_json_path = '/home/xyzgate/cq/data_process/result_distance_final.json'
encodings_json_path = "/home/xyzgate/cq/data_process/result_encoding.json"

#calculate distance
def cal_distance(encoding_x, lists, file_num, my_json):
    encodings_x = []
    known_face_names = []
    face_distance_save = {}



    for i in range(len(lists)):
        if i > file_num:
            list_2=os.listdir(test_dir + str(lists[i][1]))
            face_distances = []
            
            for pic in list_2:

                if my_json[str(lists[i][1])][str(pic)] == 0:
                    continue
                else:
                    encoding_pic = []
                    encoding_pic.append(np.array(my_json[str(lists[i][1])][str(pic)],dtype = float))
                    # print(encoding_pic)
                    face_distances_tmp = fr.face_distance(encoding_pic, encoding_x)
                    face_distances.append(face_distances_tmp)
            
            # print(face_distances)
            if face_distances == []:
                encodings_x.append(2)
            else:
                encodings_x.append(face_distances[np.argmin(face_distances)][0])
            # known_face_names.append(str(lists[i][1]))
        else:
            encodings_x.append(1)
    # final_name = known_face_names[np.argmin(encodings_x)]

    #eg.[1 1 1 0.5 0.4]
    final_distance = encodings_x
    # print(7777777)
    # print(final_name)
    return final_distance

def max_list(lt):
    temp = 0
    for i in lt:
        if lt.count(i) > temp:
            max_str = i
            temp = lt.count(i)
    return max_str

def get_pic_dot_all(lists):
    pic_dot_all = {}
    for list_1 in lists:
        # print('test picture: {}'.format(test))
        list_2=os.listdir(rootdir + str(list_1))

        pic_tmp = []
        pic_store = []
        for pic_name in list_2:
            pic_0 = pic_name.split("_")[0]
            pic_tmp.append(int(pic_0))
        pic_store = sorted(pic_tmp)

        pic_dot = []
        pic_dot.append(pic_store[0])
        for i in range(len(pic_store)-1):
            if pic_store[i+1] - pic_store[i] > 100:
                if i == 0:
                    continue
                else:
                    pic_dot.append(pic_store[i])
                    pic_dot.append(pic_store[i+1])
        pic_dot.append(pic_store[i+1])
        pic_dot_all[str(list_1.split("_")[0])] = pic_dot

    print(pic_dot_all)
    return pic_dot_all


#flag = 0 move  flag = 1 not move
#file_1 and file_2 is the number of file name      name split[0]
def compare_move_or_not(file_1,file_2,pic_dot_all):

    dot_1 = pic_dot_all[str(file_1)]
    dot_2 = pic_dot_all[str(file_2)]  

    flag = 0
    for j in range(0,len(dot_1),2):
        for i in range(len(dot_2)):
            if dot_2[i] > dot_1[j] and dot_2[i] < dot_1[j+1]:
                flag  = 1
                break
        if flag == 1:
            break
    return flag


def generate_encodings(lists,encodings_json_path):

    print('------get the encodings of known face-------')
    known_face_encodings_dict = {}
    result={}
    
    for list_1 in lists:
      list_2 = os.listdir(rootdir + str(list_1))
      encodings = []
      encodings_json = {}
      for pic_name in list_2:
          # print('picture name: {}'.format(pic_name))
          img = fr.load_image_file(rootdir + str(list_1) + '/' + str(pic_name))
          encoding = fr.face_encodings(img)
          if len(encoding) > 1:
              encodings_json[str(pic_name)] = 0
          if len(encoding) == 0:
              encodings_json[str(pic_name)] = 0
          else:
              encodings.append(encoding[0])
              # print(type(encoding[0]))
              encodings_json[str(pic_name)] = encoding[0].tolist()
      result[str(list_1)] = encodings_json
          #print(encodings)

      known_face_encodings_dict[str(list_1)] = encodings

    with open(encodings_json_path, "w") as f:
        json.dump(result, f, indent=4)
    print('Finish!')



def generate_result_json(lists, tests,encodings_json_path, distances_json_path, encodings_flag = 0):

    # get the encodings of known face
    if encodings_flag:
        generate_encodings(lists,encodings_json_path)

    print('-------------test-------------')
    with open(encodings_json_path) as f:
        my_json = json.load(f)


    test1 = {}
    for test_1 in tests:
        test1[test_1.split("_")[0]] = test_1
    test_final = sorted(test1.items(),key=lambda  item:int(item[0]))
    print(test_final)
    dis = {}
    for i in range(len(test_final)):
        print(i)
        final_distances = []
        test_2=os.listdir(test_dir + str(test_final[i][1]))
        cnt = 0
        for test in test_2:
            cnt += 1
            encoding_x = my_json[str(test_final[i][1])][str(test)]
            # print(encoding_x)
            if encoding_x == 0:
                pass
            else:
                encoding_x_array = np.array(encoding_x,dtype = float)
                # print(encoding_x_array)
                final_distance = cal_distance(encoding_x_array, test_final, i, my_json)
                final_distances.append(final_distance)
        #eg.[[1 1 1 0.5 0.4]
        #    [1 1 1 1 0.3]]
                # if not cnt%200:
                #   print(final_distance)
        # print(final_distances)
        if final_distances == []:
            final_distance_mean = [0]
            print('1111111111111111111111111111111')
        else:
            final_distance_mean = np.mean(np.array(final_distances),axis = 0)
        print(final_distance_mean)
        # print(len(final_distance_mean))

        file_distance = {}
        for j in range(len(final_distance_mean)):
            file_distance[test_final[j][1]] = final_distance_mean[j]
        dis[test_final[i][1]] = file_distance
        # print(final_distance_mean)
        # print('{} finish'.format(i))
    with open(distances_json_path, "w") as f:
        json.dump(dis, f, indent=4)
    print('Finish!')


def get_changelayer(lists):
    dict_result = {}
    for i in range(len(lists)):
        #remove items that len < 2, means only itself no combine information
        if len(lists[i]) < 2:
            lists[i] = []
            continue

        for j in lists[i]:
            # print(j)
            if j in dict_result:
                dict_result[j].append(i)
            else:
                dict_result[j] = [i]
    # print(dict_result)

    list_result = []
    # dict_out = []
    for list_1 in dict_result:
        # print(list_1)
        
        if len(dict_result[list_1]) > 1:
            # dict_out.append(dict_result[list_1])
            # print(dict_result[list_1])
            list_tmp = []
            for k in range(len(dict_result[list_1])):
                if len(lists[dict_result[list_1][k]]) == 0:
                    continue
                else:
                    list_tmp = np.hstack((lists[dict_result[list_1][k]],list_tmp))
                    lists[dict_result[list_1][k]] = []
            list_result = map(int,list(set(list_tmp)))
            lists[dict_result[list_1][0]] = list_result

    while [] in lists:
        lists.remove([])


    # print(dict_out)
    return lists

def get_final_list(lists):
    # list_save = []
    # list_save.append(get_changelayer(list_test))
    # layer_num = 0
    # while(len(list_save[layer_num])):
    #     print(list_save)
    #     list_save.append(get_changelayer(list_save[layer_num]))
    #     layer_num += 1
    result = get_changelayer(lists)
    print(result)
    len_result_1 = len(result)

    flag = 1
    while(flag):
        result = get_changelayer(result)
        len_result_2  = len(result)
        print(result)
        if len_result_1 - len_result_2:
            len_result_1 = len_result_2
        else:
            flag = 0

    return result

def get_json_result(json_file_path):

    with open(json_file_path) as f:
        my_json = json.load(f)
    # print(my_json)
    tmp_i = []
    for test_1 in my_json:
        tmp_i.append(test_1)
    file_i = sorted(tmp_i,key = lambda x: int(x.split("_")[0]))
    print(file_i)

    list_result = []
    for i in range(len(file_i)):
        tmp_j = []
        file_j = []
        for j in my_json[file_i[i]]:
            tmp_j.append(j)
        file_j = sorted(tmp_j,key = lambda x: int(x.split("_")[0]))

        list_result_tmp = []
        list_result_tmp.append(i)
        for k in range(len(file_j)):
            # print(my_json[dd[i]][j])
            if my_json[file_i[i]][file_j[k]] < 0.3 and my_json[file_i[i]][file_j[k]] > 0:
                list_result_tmp.append(k)
        list_result.append(list_result_tmp)
    print(list_result)
    return list_result

if __name__ == '__main__':
    generate_result_json(lists, tests, encodings_json_path, distances_json_path, encodings_flag = 0)
    result_1 = get_json_result(distances_json_path)
    get_final_list(result_1)

