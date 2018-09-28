# -*- coding:utf8 -*-

import os
import cv2
import sys
import numpy as np

class BatchRename():
    '''
    批量重命名文件夹中的图片文件

    '''
    def __init__(self):
        self.path = './'

    def rename(self): 
        filelist = os.listdir(self.path)
        for i in range(1,454):
            if(i<10):
                imgname = '0000' +str(i)
                newimgname = '0000' +str(i) + '.jpg'
            elif(i<100):
                imgname = '000' +str(i)     
                newimgname = '000' +str(i) + '.jpg'   
            elif(i<1000):
                imgname = '00' +str(i) 
                newimgname = '00' +str(i) + '.jpg'
            else:
                imgname = '0' +str(i)
                newimgname = '0' +str(i) + '.jpg'
            img = cv2.imread(self.path + imgname + '.png')
            cv2.imwrite(self.path + newimgname, img)
            print('convert %d'%i)
            
        #print('total %d to rename & converted %d jpgs' % (total_num, i))


        # filelist = os.listdir(self.path)
        # total_num = len(filelist)
        # for item in filelist:
        #     if(i<10):
        #         imgname = '0000' +str(i)
        #     elif(i<100):
        #         imgname = '000' +str(i)         
        #     elif(i<1000):
        #         imgname = '00' +str(i) 
        #     else:
        #         imgname = '0' +str(i)
        #     if item.endswith('.png'):
        #         src = os.path.join(os.path.abspath(self.path), item)
        #         dst = os.path.join(os.path.abspath(self.path), imgname + '.jpg')
        #         try:
        #             os.rename(src, dst)
        #             print('converting %s to %s ...' % (src, dst))
        #             i = i + 1
        #         except:
        #             continue
        # print('total %d to rename & converted %d jpgs' % (total_num, i))

if __name__ == '__main__':
    demo = BatchRename()
    demo.rename()
