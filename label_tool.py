# -*- coding: utf-8 -*-

# This is the python code for classification multilabel label tool
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
# I refer to BBox-Label-Tool, and modify the original object detection label tool to support multilabel labelling,
# right now the label tool only support .jpg format, but you can easily modify the support format in
# def loadDir(self, dbg=False):
#    ...
#    self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))  # with the specified exts
#    ...
#
# besides, I add some new fuctions as follows when comparing with BBox-Label-Tool:
# 1. add a button to reset the class label
# 2. all label attributes should be checked before save in .txt file
# 3. show image name during labelling;
# 4. goto button supports locate image by image name

# reference:
# 1 https://github.com/puzzledqs/BBox-Label-Tool
#
# Author: hzhumeng01 2018-01-25


from __future__ import division
from Tkinter import *
from tkMessageBox import *
from PIL import Image, ImageTk
import os
import glob
import random

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

# colors for the bboxes
COLORS = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green', 'black']

# image sizes for the examples, but never use
SIZE          = 256, 256
INVALID       = -1
MULTITASK_NUM = 5

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


class LabelTool():
    def __init__(self, master):

        # set up the main frame
        self.parent = master
        self.parent.title("label_tool_classification_multilabel")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width=False, height=False)

        # initialize global state
        self.imageDir = ''
        self.imageList = []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = ''
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text="Image Dir:")
        self.label.grid(row=0, column=0, sticky=E)
        self.entry = Entry(self.frame)
        self.entry.grid(row=0, column=1, sticky=W + E)
        self.ldBtn = Button(self.frame, text="Load", command=self.loadDir)
        self.ldBtn.grid(row=0, column=2, sticky=W + E)

        # multi class label
        self.variableClothesStyle = StringVar()
        self.variableClothesColor = StringVar()
        self.variableClothesTexture = StringVar()
        self.variableClothesNeckline = StringVar()
        self.variableClothesSleeve = StringVar()

        self.variableClothesStyle.set(OptionsClothesStyle[len(OptionsClothesStyle) - 1])  # set default as none
        self.variableClothesColor.set(OptionsClothesColor[len(OptionsClothesColor) - 1])  # set default as none
        self.variableClothesTexture.set(OptionsCClothesTexture[len(OptionsCClothesTexture) - 1])  # set default as none
        self.variableClothesNeckline.set(OptionsClothesNeckline[len(OptionsClothesNeckline) - 1])  # set default as none
        self.variableClothesSleeve.set(OptionsClothesSleeve[len(OptionsClothesSleeve) - 1])  # set default as none

        # multilabel labelling
        self.multilabel = Label(self.frame, text="MultiLabel: ")
        self.multilabel.grid(row=1, column=0, sticky=E)

        self.ctrPanelClass = Frame(self.frame)
        self.ctrPanelClass.grid(row=1, column=1, columnspan=2, sticky=W + E)

        # 1 ClothesStyle, 26 classes
        self.optionMenuClothesStyle = OptionMenu(self.ctrPanelClass, self.variableClothesStyle, *OptionsClothesStyle)
        self.optionMenuClothesStyle.pack(side=LEFT)

        # 2 ClothesColor, 11 classes
        self.optionMenuClothesColor = OptionMenu(self.ctrPanelClass, self.variableClothesColor, *OptionsClothesColor)
        self.optionMenuClothesColor.pack(side=LEFT)

        # 3 ClothesTexture, 8 classes
        self.optionMenuClothesTexture = OptionMenu(self.ctrPanelClass, self.variableClothesTexture, *OptionsCClothesTexture)
        self.optionMenuClothesTexture.pack(side=LEFT)

        # 4 ClothesNeckline
        self.optionMenuClothesNeckline = OptionMenu(self.ctrPanelClass, self.variableClothesNeckline, *OptionsClothesNeckline)
        self.optionMenuClothesNeckline.pack(side=LEFT)

        # 5 ClothesSleeve, 4 classes
        self.optionMenuClothesSleeve = OptionMenu(self.ctrPanelClass, self.variableClothesSleeve, *OptionsClothesSleeve)
        self.optionMenuClothesSleeve.pack(side=LEFT)

        # clear label, add by hzhumeng01
        self.btnResetLabel = Button(self.ctrPanelClass, text='ResetLabel', width=7, command=self.resetLabel)
        self.btnResetLabel.pack(side=LEFT)

        self.label_imgname = Label(self.ctrPanelClass, text='img_name:')
        self.label_imgname.pack(side=LEFT)
        self.imgnamebox = Listbox(self.ctrPanelClass, width=20, height=2)
        self.imgnamebox.pack(side=LEFT)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        # self.parent.bind("a", self.prevImage)  # press 'a' to go backforward
        # self.parent.bind("d", self.nextImage)  # press 'd' to go forward
        self.mainPanel.grid(row=2, column=1, rowspan=4, sticky=W + N)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text='MultiLabel: ')
        self.lb1.grid(row=2, column=2, sticky=W + N)
        self.listbox = Listbox(self.frame, width=22, height=8)
        self.listbox.grid(row=3, column=2, sticky=N)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row=6, column=1, columnspan=2, sticky=W + E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width=6, command=self.prevImage)
        self.prevBtn.pack(side=LEFT, padx=5, pady=3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width=6, command=self.nextImage)
        self.nextBtn.pack(side=LEFT, padx=5, pady=3)
        self.progLabel = Label(self.ctrPanel, text="Progress:     /    ")
        self.progLabel.pack(side=LEFT, padx=5)
        self.tmpLabel = Label(self.ctrPanel, text="Go to Image Name: ")
        self.tmpLabel.pack(side=LEFT, padx=5)
        self.idxEntry = Entry(self.ctrPanel, width=5)
        self.idxEntry.pack(side=LEFT)
        self.goBtn = Button(self.ctrPanel, text='Go', command=self.gotoImage)
        self.goBtn.pack(side=LEFT)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side=RIGHT)

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(10, weight=1)

    def loadDir(self, dbg=False):
        if not dbg:
            img_folder = self.entry.get()       # this is the image file folder, and should set
            self.parent.focus()
            self.category = str(img_folder)
        else:
            img_folder = r'D:\workspace\python\labelGUI'

        # get image list
        self.imageDir  = os.path.join(r'./JPEGImages', '%s' % (self.category))
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))    # with the specified exts
        if len(self.imageList) == 0:
            print 'No .JPEG images found in the specified dir!'
            return

        # set up output dir
        self.outDir = os.path.join(r'./Labels', '%s' % (self.category))
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        labeledPicList = glob.glob(os.path.join(self.outDir, '*.txt'))
        for label in labeledPicList:
            data = open(label, 'r')
            if '0\n' == data.read():
                data.close()
                continue
            data.close()
            picture = label.replace('Labels', 'Images').replace('.txt', '.jpg')
            if picture in self.imageList:
                self.imageList.remove(picture)

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)
        self.loadImage()
        print '%d images loaded from %s' % (self.total, img_folder)

    # return the index in optionMenu by value
    def getIndex(self, optionMenuVar, optionMenulist):
        index = INVALID
        for (i, optionMenuItem) in enumerate(optionMenulist):
            if optionMenuItem == optionMenuVar:
                index = i
                break

        return index


    def checkLabelValid(self, idx, idx_max):
        return (idx > INVALID) and (idx < idx_max - 1)   # should not be None


    def resetOptionMenu(self):
        # reset the label to default label
        self.variableClothesStyle.set(OptionsClothesStyle[len(OptionsClothesStyle) - 1])  # set default as none
        self.variableClothesColor.set(OptionsClothesColor[len(OptionsClothesColor) - 1])  # set default as none
        self.variableClothesTexture.set(OptionsCClothesTexture[len(OptionsCClothesTexture) - 1])  # set default as none
        self.variableClothesNeckline.set(OptionsClothesNeckline[len(OptionsClothesNeckline) - 1])  # set default as none
        self.variableClothesSleeve.set(OptionsClothesSleeve[len(OptionsClothesSleeve) - 1])  # set default as none


    def loadImage(self):

        # load image
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        self.imgSize = self.img.size
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width=max(self.tkimg.width(), 100), height=max(self.tkimg.height(), 100))   # for the gui size
        self.mainPanel.create_image(0, 0, image=self.tkimg, anchor=NW)
        self.progLabel.config(text="%04d/%04d" % (self.cur, self.total))

        # load labels
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)

        # show name
        self.imgnamebox.delete(0, END)
        self.imgnamebox.insert(0, self.imagename)

        # clear the listbox
        self.listbox.delete(0, MULTITASK_NUM + 1)

        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    multiclassImgname = [t.strip() for t in line.split()]
                    multiclass = []
                    for item in multiclassImgname[:len(multiclassImgname) - 1]: # show labelled attribute
                        multiclass.append(int(float(item)))

                    self.variableClothesStyle.set(OptionsClothesStyle[multiclass[0]])  # set default as none
                    self.variableClothesColor.set(OptionsClothesColor[multiclass[1]])  # set default as none
                    self.variableClothesTexture.set(OptionsCClothesTexture[multiclass[2]])  # set default as none
                    self.variableClothesNeckline.set(OptionsClothesNeckline[multiclass[3]])  # set default as none
                    self.variableClothesSleeve.set(OptionsClothesSleeve[multiclass[4]])  # set default as none

                    self.listbox.delete(0, MULTITASK_NUM + 1)
                    self.listbox.insert(END, '%s' % (self.variableClothesStyle.get()))
                    self.listbox.insert(END, '%s' % (self.variableClothesColor.get()))
                    self.listbox.insert(END, '%s' % (self.variableClothesTexture.get()))
                    self.listbox.insert(END, '%s' % (self.variableClothesNeckline.get()))
                    self.listbox.insert(END, '%s' % (self.variableClothesSleeve.get()))
                    self.listbox.insert(END, '%s' % (os.path.join(self.category, os.path.split(imagepath)[-1])))


    def saveImage(self):
        #test = u' '.join(self.variableClothesNeckline.get()).encode('utf-8').strip()

        idxStyles   = self.getIndex(self.variableClothesStyle.get(), OptionsClothesStyle)
        idxColor    = self.getIndex(self.variableClothesColor.get(), OptionsClothesColor)
        idxTexture  = self.getIndex(self.variableClothesTexture.get(), OptionsCClothesTexture)
        idxNeckline = self.getIndex(self.variableClothesNeckline.get(), OptionsClothesNeckline)
        idxSleeve   = self.getIndex(self.variableClothesSleeve.get(), OptionsClothesSleeve)

        # valid check
        if (not self.checkLabelValid(idxStyles, len(OptionsClothesStyle))):
            showerror("Error", "Invalid None label in ClothesStyle")
            return False

        if (not self.checkLabelValid(idxColor, len(OptionsClothesColor))):
            showerror("Error", "Invalid None label in ClothesColor")
            return False

        if (not self.checkLabelValid(idxTexture, len(OptionsCClothesTexture))):
            showerror("Error", "Invalid None label in ClothesTexture")
            return False

        if (not self.checkLabelValid(idxNeckline, len(OptionsClothesNeckline))):
            showerror("Error", "Invalid None label in ClothesNeckline")
            return False

        if (not self.checkLabelValid(idxSleeve, len(OptionsClothesSleeve))):
            showerror("Error", "Invalid None label in ClothesSleeve")
            return False

        imagepath = self.imageList[self.cur - 1]
        imageRelativePath = os.path.join(self.category.strip(), os.path.split(imagepath)[-1])

        with open(self.labelfilename, 'w') as f:   # 5 labels, 1 category
            f.write('%f\t%f\t%f\t%f\t%f\t%s' % (float(idxStyles),
                                                float(idxColor),
                                                float(idxTexture),
                                                float(idxNeckline),
                                                float(idxSleeve),
                                                str(imageRelativePath)))

        print 'Image No. %d saved' % (self.cur)
        return True


    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    # add for reset the label
    def resetLabel(self):
        self.resetOptionMenu()

    def prevImage(self, event=None):
        if not self.saveImage():
            return None

        self.resetOptionMenu()

        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event=None):
        if not self.saveImage():
            return None

        self.resetOptionMenu()

        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def gotoImage(self):
        # by index NO.
        # idx = int(self.idxEntry.get())
        # if 1 <= idx and idx <= self.total:
        #     self.saveImage()
        #     self.cur = idx
        #     self.loadImage()

        # by imgname
        index = -1
        imgname_search = str(self.idxEntry.get())
        for (i, imgpath) in enumerate(self.imageList):
            imagename = os.path.split(imgpath)[-1].split('.')[0]
            if imgname_search in imagename:
                index = i + 1
                break

        if 1 <= index and index <= self.total:
            self.saveImage()
            self.cur = index
            self.loadImage()


if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.mainloop()
