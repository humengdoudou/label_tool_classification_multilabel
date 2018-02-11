# -*- coding: utf-8 -*-
#!/usr/bin/env python

# This is the python code for creating trainval/test .txt for fitting the data format in mxnet classification task
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
# the procedure is very straightforward, read the whole labelled image txt,
# get their label content and add an index before the label content, like:
# 145344    4.000000	3.000000	4.000000	3.000000	1.000000	coat/657i67i6k_1.jpg
#
# random shuffle the list, and finally split the list into trainval/test
# the trainval/test ratio settings is done by VAL_RATIO
#
# Author: hzhumeng01 2018-01-25

import os
import sys
import math
import random

ROOT_PATH    = "label_tool_classification_multilabel/Labels/coat"

VAL_RATIO = 0.1   # VAL_RATIO * total_list is the val list, (1 - VAL_RATIO) * total_list is the train list

def create_trainval_label(root_path):

    # val root file folder
    if not os.path.exists(root_path):
        print ("Are you kidding?! path do not exists!!!!")

    file_name_list = []
    count = 0
    # for each path, subdirs is the sub-dir, files include all images in path
    for path, subdirs, file_names in os.walk(root_path, followlinks=True):

        for file_name in file_names:
            # print((os.path.join(path, file_name)))

            with open(os.path.join(path, file_name), "r") as f_read:
                labelsImage = f_read.readlines()  # only one line

                final_index = str(count) + "\t" + labelsImage[0]
                file_name_list.append(final_index)
                count += 1

    return file_name_list


if __name__ == '__main__':
    file_name_list = create_trainval_label(ROOT_PATH)

    random.seed(100)
    random.shuffle(file_name_list)

    testFile  = open('test.txt', 'w')
    trainFile = open('trainval.txt', 'w')

    # split train and test list
    for i in range(int(math.ceil(len(file_name_list) * VAL_RATIO))):
        testFile.write(str(file_name_list[i]) + '\n')

    for j in range(int(math.ceil(len(file_name_list) * VAL_RATIO)), len(file_name_list), 1):
        trainFile.write(str(file_name_list[j]) + '\n')
