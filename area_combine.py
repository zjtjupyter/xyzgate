import numpy as np


list1 = [1,3,7,15,33,60,93,210]
list2 = [4,5,18,32,66,71,230,330,420,500]
list3 = [16,17,220,225]

#判断两个有序区间片段集是否可以穿插合并，集合的k，k+1(k=0,2,...)表示一个区间，有重叠不可以合并，返回0，否则为1
def determine_combine(list_1,list_2):
    list_1_tmp = list_1.copy()
    list_1_tmp.extend(list_2)
    list_1_tmp = sorted(list_1_tmp)
    # print(list_1_tmp)
    flag = 1
    for i in range(0,len(list_1)-1,2):
        if list_1_tmp[i] in list_1 and list_1_tmp[i+1] in list_1:
            if list_1_tmp[i] in list_2 and list_1_tmp[i + 1] in list_2:
                flag = 0
                break
            else:
                continue
        elif list_1_tmp[i] in list_2 and list_1_tmp[i + 1] in list_2:
            continue
        else:
            flag = 0
            break

    return flag
#判断三个区间片段集的合并情况，返回可以合并的集合序号，对于011情况取长度更大的合并
def determine_three_file(lists):
    a = []
    b = 0
    result = [0, 1, 2]
    name = [[0,1],[0,2],[1,2]]
    for i in range(len(lists)):
        for j in range(i+1,len(lists)):
            tmp = determine_combine(lists[i],lists[j])
            b = tmp + b
            a.append(tmp)
    print(a)
    if b == 0:
        result = []
    elif b == 1:
        result = name[np.argmax(a)].copy()
    elif b == 2:
        # print(name[np.argmin(a)])
        if len(lists[name[np.argmin(a)][0]]) > len(lists[name[np.argmin(a)][1]]):
            print('length {} is bigger'.format(name[np.argmin(a)][0]))
            result.remove(name[np.argmin(a)][1])
        else:
            print('length {} is bigger'.format(name[np.argmin(a)][1]))
            result.remove(name[np.argmin(a)][0])
    else:
        pass

    return result



if __name__ == '__main__':
    lists = []
    lists.append(list1)
    lists.append(list2)
    lists.append(list3)
    print(determine_three_file(lists))
    # if determine_combine(list2,list3):
    #     print('能合并')
    # else:
    #     print('不能合并')
    # print(list2)
    # print(list3)