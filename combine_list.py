import numpy as np
import json

# a = ['1_2','4_3','3_1','2_4']
# b = np.zeros(len(a)+1)
# ls2 = [str(i) for i in b]
# print(ls2)
# for i in a:
#     n = i.split('_')[0]
#     print(n)
#     ls2[int(n)] = i
#     print(ls2)
# lists={'0':[1,3],'1':[2],'2':[4,5],'3':[5,11],'4':[11,13,15]}
list_test=[[1,2,3],[2,3,4],[3,4,5],[6,8],[5,7,11],[11,13,15]]
json_file_path = "/home/xyzgate/cq/data_process/distance_ttttest.json"

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
            if my_json[file_i[i]][file_j[k]] < 0.3:
                list_result_tmp.append(k)
        list_result.append(list_result_tmp)
    print(list_result)
    return list_result

if __name__ == '__main__':
    result_1 = get_json_result(json_file_path)
    get_final_list(result_1)

