# -*- coding: utf-8 -*-

# This is the python code for label validation check by using classification multilabel label tool
#
# I use the label tool by labelling image as the following format in txt:
#
# 4.000000	3.000000	4.000000	3.000000	1.000000	coat/657i67i6k_1.jpg
#
# one .jpg image corresponds to one .txt file, and each .txt file has only one line as the above format,
# each line has 6 elements, the 6th element is image relative path,
# the 1st~5th elements are the multilabel of the image, and they are ordered by the labelling attribute.
# take the above 5 elements as an example:
# 1st 4.000000 means in OptionsClothesStyle attribute is "small suit"/"小西装"
# 2nd 3.000000 means in OptionsClothesColor attribute is "gray"/"灰色"
# 3rd 4.000000 means in OptionsCClothesTexture attribute is "dot"/"圆点"
# 4th 3.000000 means in OptionsClothesNeckline attribute is "stand neck"/"立领"
# 5th 1.000000 means in OptionsClothesSleeve attribute is "middle"/"中袖"
#
# ATTENTION: the different between "None" and "else"
# the "None" attribute in 5 labels means unlabelled,
# the "else" attribute means the attribute does not belong to above specified attributes.
#
# in each .txt, each attribute should not be smaller than 0, and should not be a None.
#
# Author: hzhumeng01 2018-01-25

from __future__ import print_function
import os
import sys

import random
import argparse
import cv2
import time
import traceback
import numpy as np

import os.path
import shutil

ROOT_PATH    = "label_tool_classification_multilabel/Labels/"

# OptionsClothesStyle    = ["风衣",   "毛呢大衣", "羊毛衫", "羽绒服", "小西装", "西装套装",
#                           "夹克",   "旗袍", "皮衣", "皮草", "婚纱", "衬衫",
#                           "T恤",    "POLO衫", "针织衫", "马甲", "吊带", "卫衣",
#                           "雪纺衫", "连衣裙", "半身裙", "打底裤", "休闲裤", "牛仔裤",
#                           "短裤",   "运动裤", "无"]
OptionsClothesStyle    = ["wind coat",   "woolen coat", "knitted sweater", "down jacket", "small suit", "west suit",
                          "jacket",   "cheongsam", "leather", "fur", "wedding", "shirt",
                          "T shirt",    "POLO shirt", "knitwear", "vest", "gallus", "hoodie",
                          "chiffon shirt", "one-piece", "skirt", "leggings", "casual pants", "jeans",
                          "shorts",   "slacks", "None"]

# OptionsClothesColor    = ["黑色", "蓝色", "棕色", "灰色", "绿色", "橙色",
#                           "粉色", "紫色", "红色", "白色", "黄色", "无"]
OptionsClothesColor    = ["black", "blue", "blown", "gray", "green", "orange",
                          "pink", "purple", "red", "white", "yellow", "None"]

# OptionsCClothesTexture = ["纯色", "横条纹", "纵条纹", "格子", "圆点", "乱花",
#                           "LOGO", "其他", "无"]
OptionsCClothesTexture = ["solid", "horizon", "vertical", "grid", "dot", "paisley",
                          "LOGO", "else", "None"]

# OptionsClothesNeckline = ["圆领", "V领", "翻领", "立领", "毛领", "西装领",
#                           "连毛领", "其他", "None"]
OptionsClothesNeckline = ["round neck", "V neck", "lapel neck", "stand neck", "feather neck", "suit neck",
                          "collars neck", "else", "None"]

# OptionsClothesSleeve   = ["短袖", "中袖", "长袖", "无袖", "无"]
OptionsClothesSleeve   = ["short", "middle", "long", "sleeveless", "None"]

INVALID       = -1

def check_label_index(idx, idx_max):
    return (idx > INVALID) and (idx < idx_max - 1)  # should not be None


def check_label_valid(root_path):

    # val root file folder
    if not os.path.exists(root_path):
        print ("Are you kidding?! path do not exists!!!!")

    # for each path, subdirs is the sub-dir, files include all images in path
    for path, subdirs, files in os.walk(root_path, followlinks=True):
        # subdirs.sort()
        # print (subdirs)
        for file_name in files:
            # print((os.path.join(path, file_name)))

            with open(os.path.join(path, file_name), "r") as f_read:
                labelsImage = f_read.readlines()     # only one line

                multilabelImgname = [t.strip() for t in labelsImage[0].split()]
                # print ("multilabelImgname: ", multilabelImgname)
                multilabel = []
                for item in multilabelImgname[:len(multilabelImgname) - 1]:  # show labelled attribute
                    multilabel.append(int(float(item)))

                # valid check
                if (not check_label_index(multilabel[0], len(OptionsClothesStyle))):
                    print ("Error", "Invalid None label in ClothesStyle")
                    return False

                if (not check_label_index(multilabel[1], len(OptionsClothesColor))):
                    print ("Error", "Invalid None label in ClothesColor")
                    return False

                if (not check_label_index(multilabel[2], len(OptionsCClothesTexture))):
                    print ("Error", "Invalid None label in ClothesTexture")
                    return False

                if (not check_label_index(multilabel[3], len(OptionsClothesNeckline))):
                    print ("Error", "Invalid None label in ClothesNeckline")
                    return False

                if (not check_label_index(multilabel[4], len(OptionsClothesSleeve))):
                    print ("Error", "Invalid None label in ClothesSleeve")
                    return False

    return True


if __name__ == '__main__':

    if check_label_valid(ROOT_PATH):
        print("all ok!!!")
