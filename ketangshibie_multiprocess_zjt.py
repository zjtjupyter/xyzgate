# -*- coding=utf-8 -*-
#!/usr/bin/env python2

# Copyright (c) 2017-present, Facebook, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##############################################################################

"""Perform inference on a single video or all images with a certain extension
(e.g., .jpg) in a folder.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
import numpy as np
import argparse
import cv2 as cv2  # NOQA (Must import before importing caffe2 due to bug in cv2)
import json
import glob
import logging
import base64
import os
import sys
import time
import math
import multiprocessing

from caffe2.python import workspace

from detectron.core.config import assert_and_infer_cfg
from detectron.core.config import cfg
from detectron.core.config import merge_cfg_from_file
from detectron.utils.io import cache_url
from detectron.utils.logging import setup_logging
from detectron.utils.timer import Timer
import detectron.core.test_engine as infer_engine
import detectron.datasets.dummy_datasets as dummy_datasets
import detectron.utils.c2 as c2_utils
import detectron.utils.vis as vis_utils

c2_utils.import_detectron_ops()

# OpenCL may be enabled by default in OpenCV3; disable it because it's not
# thread safe and causes unwanted GPU memory allocations.
cv2.ocl.setUseOpenCL(False)


def parse_args():
    parser = argparse.ArgumentParser(description='End-to-end inference')
    parser.add_argument(
        '--cfg',
        dest='cfg',
        help='cfg model file (/path/to/model_config.yaml)',
        default=None,
        type=str
    )
    parser.add_argument(
        '--wts',
        dest='weights',
        help='weights model file (/path/to/model_weights.pkl)',
        default=None,
        type=str
    )
    parser.add_argument(
        '--output-image-dir',
        dest='output_image_dir',
        help='directory for video2pictures (default: /data/video_pictures)',
        default='/data/video_pictures',
        type=str
    )
    parser.add_argument(
        '--always-out',
        dest='out_when_no_box',
        help='output image even when no object is found',
        action='store_true'
    )
    parser.add_argument(
        '--thresh',
        dest='thresh',
        help='thresh value',
        default=0.7,
        type=float
    )
    parser.add_argument(
        '--fps',
        dest='fps',
        help='每多少帧截一张图',
        default=2,
        type=int
    )
    parser.add_argument(
        '--intersection',
        dest='intersection',
        help='intersection value',
        default=0.6,
        type=float
    )
    parser.add_argument(
        '--videos-path',
        dest='videos_path',
        help='生成视频路径',
        default="/data/result-videos",
        type=str
    )
    parser.add_argument(
        '--iters',
        dest='iters',
        help='iters',
        default=250,
        type=int
    )
    parser.add_argument(
        '--min-number-percent',
        dest='min_number_percent',
        help='文件夹内图片最小数量',
        default=0.01,
        type=float
    )
    parser.add_argument(
        '--max-distance',
        dest='max_distance',
        help='聚类最大距离',
        default=250,
        type=int
    )
    parser.add_argument(
        '--step-length',
        dest='step_length',
        help='每步增加的允许误差范围',
        default=1,
        type=int
    )
    parser.add_argument(
        '--frame-gap',
        dest='frame_gap',
        help='丢帧的数量',
        default=100,
        type=int
    )
    parser.add_argument(
        '--min-filepercent',
        dest='min_filepercent',
        help='最后一步最小聚类数量',
        default=0.7,
        type=float
    )
    parser.add_argument(
        '--min-clusterpercent',
        dest='min_clusterpercent',
        help='聚类center',
        default=0.3,
        type=float
    )
    parser.add_argument(
        '--multiprocess-num',
        dest='multiprocess_num',
        help='xianchengshu',
        default=8,
        type=int
    )
    parser.add_argument(
        'video_or_folder', help='video or folder', default=None
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()

def sameperson(cur_box, all_boxes, frame_num, cur_frame_num, intersection):
    arr = []
    for i, b in enumerate(all_boxes):
        max_score = {"id": 0, "score": 0, "frame": 0}
        if cur_box[0] >= b[2]:
            continue
        elif cur_box[2] <= b[0]:
            continue
        elif cur_box[3] <= b[1]:
            continue
        elif cur_box[1] >= b[3]:
            continue
        else:
            xmin = cur_box[0] if cur_box[0] > b[0] else b[0]
            xmax = cur_box[2] if cur_box[2] < b[2] else b[2]
            ymax = cur_box[3] if cur_box[3] < b[3] else b[3]
            ymin = cur_box[1] if cur_box[1] > b[1] else b[1]
            b_area = (b[2] - b[0]) * (b[3] - b[1])
            cur_box_area = (cur_box[2] - cur_box[0]) * (cur_box[3] - cur_box[1]) 
            cross_area = (xmax - xmin) * (ymax - ymin)
            cross_1 = float(cross_area)/float(cur_box_area)
            cross_2 = float(cross_area)/float(b_area)
            if cross_1 > intersection and cross_2 > intersection:
                score = cross_1 if cross_1 < cross_2 else cross_2
                max_score["id"] = i
                max_score["score"] = score
                max_score["frame"] = frame_num[i]
                arr.append(max_score)
            elif (cross_1 > 0.9 and cross_2 > 0.3) or ( cross_2 > 0.9 and cross_1 > 0.3 ):
                if abs(b[3] - cur_box[3]) < 20 or ( abs(b[0] - cur_box[0]) < 20 and abs(b[2] - cur_box[2]) < 20 ):
                    score = cross_2 if cross_1 > cross_2 else cross_1
                    max_score["id"] = i
                    max_score["score"] = score 
                    max_score["frame"] = frame_num[i]
                    arr.append(max_score) 
    arr.sort(key=lambda student: (student["frame"], student["score"]),  reverse=True)
    if len(arr) > 1:
        print(arr)   
    if len(arr) == 0:
        return "not_find"
    else:
        return arr

def if_exist(cur_box, all_boxes):
    if len(all_boxes) == 0:
        return "not_find"
    else:
        if_find = 0
        for i, b in enumerate(all_boxes):
            if cur_box[0] >= b[2]:
                continue
            elif cur_box[2] <= b[0]:
                continue
            elif cur_box[3] <= b[1]:
                continue
            elif cur_box[1] >= b[3]:
                continue
            else:
                xmin = cur_box[0] if cur_box[0] > b[0] else b[0]
                xmax = cur_box[2] if cur_box[2] < b[2] else b[2]
                ymax = cur_box[3] if cur_box[3] < b[3] else b[3]
                ymin = cur_box[1] if cur_box[1] > b[1] else b[1]
                b_area = (b[2] - b[0]) * (b[3] - b[1])            
                cur_box_area = (cur_box[2] - cur_box[0]) * (cur_box[3] - cur_box[1]) 
                cross_area = (xmax - xmin) * (ymax - ymin)
                if float(cross_area)/float(cur_box_area) > 0.8 and float(cross_area)/float(b_area) > 0.8:
                    if_find =1
                    return i
                    break
                elif float(cross_area)/float(cur_box_area) > 0.9 or float(cross_area)/float(b_area) > 0.9:
                    if_find = 1
                    return i
                    break
        if if_find == 0:
            return "not_find"

def duplicate_removal(sorted_inds, boxes, thresh, classes):
    cur_boxes = []
    states = []
    each_score = []
    for j in sorted_inds:
        bbox = boxes[j, :4]
        score = boxes[j, -1]
        if score < thresh:
            continue
        if (int(bbox[2]) - int(bbox[0])) > 2000 or (int(bbox[3]) - int(bbox[1])) > 1000:
            continue
        find_exist = if_exist([int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])], cur_boxes)
        if find_exist  == "not_find":
            cur_boxes.append([int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])])
            each_score.append(score)
        elif score > each_score[find_exist]:
            cur_boxes[find_exist] = [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])]
            each_score[find_exist] = score
        states.append(classes[j])
    return cur_boxes, states

def cut_picture(cur_boxes, states, pre_persons_position, pre_frame_num, i, intersection, segs_array):
    if i == 1:
        for j, b in enumerate(cur_boxes):
            segs_array.append([[b[0], b[1], b[2], b[3], i, states[j]]])

            pre_persons_position.append(b)
            pre_frame_num.append(1)
    else:
        cur_persons_position = [[0, 0, 0, 0] for j in range(len(pre_persons_position))]
        cur_frame_num = [0 for j in range(len(pre_frame_num))]
        results = []
        for j, b in enumerate(cur_boxes):
            results.append(sameperson(b, pre_persons_position, pre_frame_num, i, intersection))

        iters_num = 3    
        while iters_num > 0:
            iters_num = iters_num - 1
            repeat_nums = []
            for j,r in enumerate(results):
                if_exist = 0
                for rn in repeat_nums:
                    if j in rn:
                        if_exist = 1
                        break
                if r != "not_find" and if_exist == 0 and len(r) != 0:
                    repeat_num = [j]
                    for j1,r2 in enumerate(results):
                        if r2 != "not_find" and r2 != r and len(r2) != 0:
                            if r[0]["id"] == r2[0]["id"]:
                                repeat_num.append(j1)
                    if len(repeat_num) > 1:
                        repeat_nums.append(repeat_num)
            for r in repeat_nums:
                max_score = results[r[0]][0]["score"]
                max_id = r[0]
                for j in range(1,len(r)):
                    if results[r[j]][0]["score"] < max_score:
                        results[r[j]].pop(0)
                    elif results[r[j]][0]["score"] >= max_score:
                        results[max_id].pop(0)
                        max_score = results[r[j]][0]["score"]
                        max_id = r[j]
        final_result = []
        for r in results:
            if r == "not_find" or len(r) == 0:
                final_result.append("not_find")
            else:
                final_result.append(r[0])
        for j,result in enumerate(final_result):
            b = cur_boxes[j]
            if result == "not_find":
                segs_array.append([[b[0], b[1], b[2], b[3], i, states[j]]])

                cur_persons_position.append(b)
                cur_frame_num.append(i)
            else:
                segs_array[result["id"]].append([b[0], b[1], b[2], b[3], i, states[j]])
                
                cur_persons_position[result["id"]] = b
                cur_frame_num[result["id"]] = i
        for j in range(len(cur_persons_position)):
            if j >= len(pre_persons_position):
                pre_persons_position.append(cur_persons_position[j])
                pre_frame_num.append(cur_frame_num[j])
            elif cur_persons_position[j] != [0, 0, 0, 0]:
                pre_persons_position[j] = cur_persons_position[j]
                pre_frame_num[j] = cur_frame_num[j]

def generate_json(segs_array, frame_gap):
    my_json = {"result": []}

    logger = logging.getLogger(__name__)
    logger.info("文件夹数量为： {}".format(len(segs_array)))
    for i,fs in enumerate(segs_array):
        info = {"id": 0, "length": 0, "segs": [], "centers": [], "file_number": [], "file_infos": []}
        info["id"] = i
        info["length"] = len(fs)
        min_index = fs[0][4]
        max_index = 0
        total_numbers = 0
        x_total = float(0)
        y_total = float(0)
        file_info = []
        for j,f in enumerate(fs):
            total_numbers = total_numbers + 1
            x_total = x_total + (float(f[2]) + float(f[0])) / 2
            y_total = y_total + (float(f[3]) + float(f[1])) / 2
            file_info.append(f)           
            if j == (len(fs) - 1):
                max_index = f[4]
                info["segs"].append([min_index, max_index])
                info["centers"].append([x_total/total_numbers, y_total/total_numbers])
                info["file_number"].append(total_numbers)
                info["file_infos"].append(file_info)
                total_numbers = 0
                x_total = float(0)
                y_total = float(0)
                file_info = []
            elif int(fs[j + 1][4]) - int(fs[j][4]) > frame_gap :
                max_index = fs[j][4]
                info["segs"].append([min_index, max_index])
                info["centers"].append([x_total/total_numbers, y_total/total_numbers])
                info["file_number"].append(total_numbers)
                info["file_infos"].append(file_info)
                total_numbers = 0
                x_total = float(0)
                y_total = float(0)
                file_info = []
                min_index = fs[j][4] 
                max_index = fs[j + 1][4]
                
        my_json["result"].append(info)
        logger.info("第{}个文件夹生成json完成".format(str(i)))
    logger.info("片段总数{}".format(len(my_json["result"])))
    return my_json

def cal_distance(json_1, json_2):
    x1 = 0
    y1 = 0
    weight1 = 0
    for s in json_1["segs"]:
        x1 = x1 + s["center"][0] * s["file_number"]
        y1 = y1 + s["center"][1] * s["file_number"]
        weight1 = weight1 + s["file_number"]
    x1 = x1/weight1
    y1 = y1/weight1
    x2 = 0
    y2 = 0
    weight2 = 0
    for s in json_2["segs"]:
        x2 = x2 + s["center"][0] * s["file_number"]
        y2 = y2 + s["center"][1] * s["file_number"]
        weight2 = weight2 + s["file_number"]
    x2 = x2/weight2
    y2 = y2/weight2
    dis = math.sqrt( pow(x1 - x2, 2) + pow(y1 - y2, 2) )
    return dis

def sort_json(result):
    sort_arr = []
    new_result = []
    for r in result:
        file_number = 0
        for s in r["segs"]:
            file_number = file_number + s["file_number"]
        sort_arr.append([r["id"], file_number])
    sort_arr.sort(key=lambda arr: arr[1], reverse=True)
    for s in sort_arr:
        new_result.append(result[s[0]])
    return new_result


def cluster(my_json, min_number, iters, max_distance, step_length, min_clusternumber):
    logger = logging.getLogger(__name__)
    all_frames = []
    for i in my_json["result"]:
        for c in range(len(i["centers"])):
            if i["file_number"][c] > min_number:
                all_frames.append({"id": i["id"], "file_number": i["file_number"][c], "seg": i["segs"][c], "center": i["centers"][c], "file_info": i["file_infos"][c]})
    calculated_frames = []
    result = []
    for f in all_frames:
        result.append({"id": len(result), "segs": [f]})
    for i in range(iters):
        calculated_frames = []
        iter_result = []
        result = sort_json(result)
        for r in result:
            if r not in calculated_frames:
                f_json = {"id": len(iter_result), "segs": []}
                r_file_number = 0
                for s in r["segs"]:
                    f_json["segs"].append(s)
                    r_file_number = r_file_number + s["file_number"]
                calculated_frames.append(r)
                if r_file_number > min_clusternumber or i > iters * 0.8:
                    for r2 in result:
                        if r2 not in calculated_frames:
                            if_possible = 1
                            for s in f_json["segs"]:
                                for s2 in r2["segs"]:
                                    if not ( s2["seg"][0] > s["seg"][1] or s2["seg"][1] < s["seg"][0] ):
                                        if_possible = 0
                                        break
                                if if_possible == 0:
                                    break
                            if if_possible == 1:
                                dis = cal_distance(r2, f_json)
                                if dis < ( max_distance if max_distance < (i + 1) * step_length else (i + 1) * step_length ):
                                    for s in r2["segs"]:
                                        f_json["segs"].append(s)
                                    calculated_frames.append(r2)

                iter_result.append(f_json)
        result = []
        for rs in iter_result:
            result.append(rs)

        logger.info("第{}轮迭代后文件数： {}".format(str(i), len(result)))
    return result

    
def final_json(result, max_distance, min_filenumber):
    logger = logging.getLogger(__name__)
    total_frame_nums = []
    for r in result:
        cur_frame_nums = []
        for s in r["segs"]:
            for i in s["file_info"]:
                cur_frame_nums.append(i[4])
        total_frame_nums.append(cur_frame_nums)
    calculated_frames = []
    final_result = []
    index_array = []
    result = sort_json(result)
    for index_r, r in enumerate(result):
        if r not in calculated_frames:
            index_array.append([index_r])
            f_json = {"id": len(final_result), "segs": []}
            frame_nums = []
            for i in total_frame_nums[r["id"]]:
                frame_nums.append(i)
            center = [0, 0, 0]
            for s in r["segs"]:
                center[0] = center[0] + s["center"][0] * s["file_number"]
                center[1] = center[1] + s["center"][1] * s["file_number"]
                center[2] = center[2] + s["file_number"]
                f_json["segs"].append(s)
            calculated_frames.append(r)
            for index_r2, r2 in enumerate(result):
                if r2 not in calculated_frames:
                    cur_frame_nums = []
                    for i in total_frame_nums[r2["id"]]:
                        cur_frame_nums.append(i)
                    overlay = 0
                    overlay_arr = []
                    cur_center = [0, 0, 0]
                    for s2 in r2["segs"]:
                        cur_center[0] = cur_center[0] + s2["center"][0] * s2["file_number"]
                        cur_center[1] = cur_center[1] + s2["center"][1] * s2["file_number"]
                        cur_center[2] = cur_center[2] + s2["file_number"]
                    for n in cur_frame_nums:
                        if n in frame_nums:
                            overlay = overlay + 1
                        else:
                            overlay_arr.append(n)
                    distance = math.sqrt( pow(cur_center[0]/cur_center[2] - center[0]/center[2], 2) + pow(cur_center[1]/cur_center[2] - center[1]/center[2], 2) )
                    if float(overlay)/float(len(cur_frame_nums)) < 0.05 and float(overlay)/float(len(frame_nums)) < 0.05 and distance < max_distance:
                        index_array[len(final_result)].append(index_r2)
                        for s2 in r2["segs"]:
                            f_json["segs"].append(s2)
                        frame_nums.extend(overlay_arr)
                        calculated_frames.append(r2)
                        center[0] = center[0] + cur_center[0]
                        center[1] = center[1] + cur_center[1]
                        center[2] = center[2] + cur_center[2]
            final_result.append(f_json)
    f_final_result = []
    for index_f, r in enumerate(final_result):
        f_file_number = 0
        for s in r["segs"]:
            f_file_number = f_file_number + s["file_number"]
        if f_file_number > min_filenumber:
            f_final_result.append(r)
        else:
            for index_r in index_array[index_f]:
                f_final_result.append(result[index_r])

    logger.info("最后文件数： {}".format(len(f_final_result)))
    with open(str(time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))) + ".json", "w") as f:
        json.dump({"result": f_final_result}, f, indent = 4)
    return f_final_result

def generate_single_videos(j, r, output_image_dir, videos_path, fps):
    logger = logging.getLogger(__name__)
    fourcc = 1196444237

    file_number = 0
    for n in r["segs"]:
        file_number = file_number + n["file_number"]
    sort1 = []
    sort2 = []
    for s in r["segs"]:
        sort1.append(s["seg"][0])
    sort1.sort()
    for s in sort1:
        for s1 in r["segs"]:
            if s1["seg"][0] == s:
                sort2.append(s1)
                break
    
    # img_list = []
    # for s in sort2:
    #     for i in range(s["seg"][0], s["seg"][1] + 1):
    #         img_list.extend(glob.glob(os.path.join(imgs_path, str(s["id"]) + "/" + str(i) + "_*.jpg")))
    # os.mkdir(os.path.join(videos_path, str(j) + "_" + str(len(img_list))))
    # for img_path in img_list:
    #     shutil.copyfile(img_path, os.path.join(videos_path, str(j) + "_" + str(len(img_list)), img_path.split("/")[-1]))

    # logger.info("第{}个文件夹完成".format(str(j) + "_" + str(len(img_list))))


    length = 0
    for s in sort2:
        length = length + s["file_number"]
    width = int(sort2[0]["file_info"][0][2]) - int(sort2[0]["file_info"][0][0])
    height = int(sort2[0]["file_info"][0][3]) - int(sort2[0]["file_info"][0][1])
    # videoWriter = cv2.VideoWriter(os.path.join(videos_path, str(j) + "_" + str(length) + '.avi'),fourcc,fps,(width,height))
    for s in sort2:
        
        os.mkdir(os.path.join(videos_path, str(j) + "_" + str(len(s["file_info"]))))
        for i in s["file_info"]:
            try:
                im = cv2.imread(os.path.join(output_image_dir, str(i[4]) + '.jpg'))
                frame = im[i[1]:i[3],i[0]:i[2]]
                res=cv2.resize(frame,(width,height),interpolation=cv2.INTER_CUBIC)
                cv2.imwrite(os.path.join(videos_path, str(j) + "_" + str(len(s["file_info"])) + '/' 
                    + str(i[4]) + "_" + str(i[0]) + "_" + str(i[1]) + "_" + str(i[2]) + "_" + str(i[3]) + "_" + str(i[5]) +'.jpg'),res)
                # videoWriter.write(res)
            except:
                pass
            
    # videoWriter.release()
    # logger.info("第{}个视频完成".format(str(j) + "_" + str(length)))
        logger.info("第{}个文件夹完成".format(str(j) + "_" + str(len(img_list))))


def generate_videos(my_json, output_image_dir, videos_path, fps, min_number, iters, max_distance, step_length, min_filenumber, min_clusternumber, multiprocess_num):

    step1_json = cluster(my_json, min_number, iters, max_distance, step_length, min_clusternumber)
    # step2_json = final_json(step1_json, max_distance, min_filenumber)
    result = step1_json
    with open("/home/xyzgate/cq/data_process/zjt.json", "w") as f:
        json.dump(result, f, indent=4)

    pool = multiprocessing.Pool()
    for j, r in enumerate(result):
        pool.apply_async(generate_single_videos, args=(j, r, output_image_dir, videos_path, fps))
    pool.close()
    pool.join()


def prepare(args):
    total_numbers = 0
    logger = logging.getLogger(__name__)
    if os.path.exists(args.videos_path):
        for f in os.listdir(args.videos_path):
            os.remove(os.path.join(args.videos_path,f))
    else:
        os.makedirs(args.videos_path)
    if not os.path.isdir(args.video_or_folder):
        if os.path.exists(args.output_image_dir):
            for i in os.listdir(args.output_image_dir):
                img = os.path.join(args.output_image_dir,i)
                os.remove(img)
        else:
            os.makedirs(args.output_image_dir)
        logger.info('视频截图位于: {}'.format(args.output_image_dir))
        vc=cv2.VideoCapture(args.video_or_folder)
        c=1
        timef=args.fps
        if vc.isOpened():
            rval,frame=vc.read()
        else:
            rval=False
        while rval:
            rval,frame=vc.read()
            if(c%timef==0):
                total_numbers = total_numbers + 1
                cv2.imwrite(os.path.join(args.output_image_dir, str(int(c/timef))+'.jpg'),frame)
                logger.info('截图: {}'.format(os.path.join(args.output_image_dir, str(int(c/timef))+'.jpg')))
            c=c+1
            cv2.waitKey(1)
        vc.release()
    return total_numbers

def main(args, pic_nums):
    logger = logging.getLogger(__name__)

    merge_cfg_from_file(args.cfg)
    cfg.NUM_GPUS = 1
    args.weights = cache_url(args.weights, cfg.DOWNLOAD_CACHE)
    assert_and_infer_cfg(cache_urls=False)

    assert not cfg.MODEL.RPN_ONLY, \
        'RPN models are not supported'
    assert not cfg.TEST.PRECOMPUTED_PROPOSALS, \
        'Models that require precomputed proposals are not supported'

    model = infer_engine.initialize_model_from_cfg(args.weights)
    dummy_coco_dataset = dummy_datasets.get_coco_dataset()

    if os.path.isdir(args.video_or_folder):
        im_list = glob.glob(os.path.join(args.video_or_folder, '*.jpg'))
        img_dir = args.video_or_folder
    else:
        im_list = glob.glob(os.path.join(args.output_image_dir, '*.jpg'))
        img_dir = args.output_image_dir

    pre_frame_num = []
    pre_persons_position = []
    cur_boxes = []
    states = []
    segs_array = []

    for i in range( 1, len(im_list) + 1 ):
        im_name = os.path.join(img_dir, str(i) + ".jpg")
        logger.info('Processing {}'.format(im_name))
        im = cv2.imread(im_name)
        timers = defaultdict(Timer)
        t = time.time()
        # 获取boxes，segms，keyps
        with c2_utils.NamedCudaScope(0):
            cls_boxes, cls_segms, cls_keyps = infer_engine.im_detect_all(
                model, im, None, timers=timers
            )
        logger.info('Inference time: {:.3f}s'.format(time.time() - t))
        for k, v in timers.items():
            logger.info(' | {}: {:.3f}s'.format(k, v.average_time))
        if isinstance(cls_boxes, list):
            box_list = [b for b in cls_boxes if len(b) > 0]
            if len(box_list) > 0:
                boxes = np.concatenate(box_list)

        classes = []
        for j in range(len(cls_boxes)):
            classes += [j] * len(cls_boxes[j])

        if boxes is None:
            sorted_inds = [] # avoid crash when 'boxes' is None
        else:
            # Display in largest to smallest order to reduce occlusion
            areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
            sorted_inds = np.argsort(-areas)

        # 对每一张照片生成的boxes去重，并删除过大的框
        cur_boxes, states = duplicate_removal(sorted_inds, boxes, args.thresh, classes)

        # 裁剪所有图片
        cut_picture(cur_boxes, states, pre_persons_position, pre_frame_num, i, args.intersection, segs_array)
        
        del states[:]
        del cur_boxes[:]
    
    my_json = generate_json(segs_array, args.frame_gap)
    generate_videos(my_json, args.output_image_dir, args.videos_path, int(24/args.fps),pic_nums*args.min_number_percent, args.iters, args.max_distance, args.step_length, pic_nums*args.min_filepercent, pic_nums*args.min_clusterpercent, args.multiprocess_num)
      

if __name__ == '__main__':
    workspace.GlobalInit(['caffe2', '--caffe2_log_level=0'])
    setup_logging(__name__)
    args = parse_args()
    pic_nums = prepare(args)
    main(args, pic_nums)
