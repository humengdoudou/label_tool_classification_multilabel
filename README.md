# 多标签的图像分类标定工具label_tool_classification_multilabel使用流程


标签： 多标签的图像分类标定工具

---

### 1. 背景

本文主要介绍多标签的图像分类标定工具label_tool_classification_multilabel [3]使用流程，代码基于开源目标标定工具BBox-Label-Tool [1]及多类别的目标检测框标定工具label_tool_detection[2]修改。

通过使用label_tool_classification_multilabel，可以对单张图像进行多个属性的标定，进而应用于多标签、多任务训练。通过label_tool_detection标定保存的图像标定结果.txt内容格式：

```
4.000000	3.000000	4.000000	3.000000	1.000000	coat/657i67i6k_1.jpg
```

在代码label_tool.py中有对其含义的解释，如下：

one .jpg image corresponds to one .txt file, and each .txt file has only one line as the above format, each line has 6 elements, 

the 6th element is image relative path, the 1st~5th elements are the multilabel of the image, and they are ordered by the labelling attribute.

take the above 5 elements as an example:

```
1st 4.000000 means in OptionsClothesStyle attribute is "small suit"/"小西装"
2nd 3.000000 means in OptionsClothesColor attribute is "gray"/"灰色"
3rd 4.000000 means in OptionsCClothesTexture attribute is "dot"/"圆点"
4th 3.000000 means in OptionsClothesNeckline attribute is "stand neck"/"立领"
5th 1.000000 means in OptionsClothesSleeve attribute is "middle"/"中袖"
```

ATTENTION: the different between "None" and "else"

the "None" attribute in 5 labels means unlabelled,

the "else" attribute means the attribute does not belong to above specified attributes.

I refer to BBox-Label-Tool, and modify the original object detection label tool to support multilabel labelling, right now the label tool only support .jpg format, but you can easily modify the support format in

```python
def loadDir(self, dbg=False):
    ...
    self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))  # with the specified exts
    ...
```

besides, I add some new fuctions as follows when comparing with BBox-Label-Tool:

1. 	add a button to reset the class label
1. 	all label attributes should be checked before save in .txt file
1. 	show image name during labelling;
1. 	goto button supports locate image by image name


### 2. 参考文献

1. 	https://github.com/puzzledqs/BBox-Label-Tool
1. 	https://g.hz.netease.com/nisp-AI-projects/label_tool_detection
1. 	https://g.hz.netease.com/nisp-AI-projects/label_tool_classification_multilabel
1. 	多类别的目标检测框标定工具BBox-Label-Tool使用流程

### 3. 图像的收集标定与格式转换
本小节主要介绍图像的收集与标定流程、标定结果的校验、训练测试图像列表的生成等步骤，相关代码可以参照label_tool_classification_multilabel [3]项目中的代码。

#### 3.1 图像收集 
图像的收集比较简单，我们使用label_tool_detection完成智能服饰识别中的服饰图像标定，图像主要来自于淘宝图像、百度街拍图片等，直接使用爬虫收集图片即可，图像风格类似图2。

<div align=left><img width="600" height="450" src="https://g.hz.netease.com/hzhumeng01/label_tool_classification_multilabel/raw/master/sups_img_for_readme/1.png"/></div>

图1 label_tool_detection标定结果示意图

<div align=left><img width="500" height="360" src="https://g.hz.netease.com/hzhumeng01/label_tool_classification_multilabel/raw/master/sups_img_for_readme/2.png"/></div>
图2 用于label_tool_classification_multilabel标定图像示意图

#### 3.2 图像的标定

标定使用label_tool_classification_multilabel完成标定，一张图像标定结果示意如图3所示：

<div align=left><img width="650" height="350" src="https://g.hz.netease.com/hzhumeng01/label_tool_classification_multilabel/raw/master/sups_img_for_readme/3.png"/></div>

图3 label_tool_classification_multilabel结果示意图

如图3所示，上衣coat标定为五个属性(knitted sweater、black、solid、feather neck、long)，每个下拉框都有多个属性供选择.

系统的标签与图片组织路径如图4所示，label_tool.py放在label_tool_classification_multilabel的根目录，JPEGImages下按子文件夹目录存放.jpg/.jpeg图片，Labels存放标注好的.txt标签文件。JPEGImages、Labels存放相同的子目录文件即可，例如截图中所示的coat文件夹，该文件夹需要手动新建。目前暂未使用到Annotations、Examples文件夹

<div align=left><img width="280" height="350" src="https://g.hz.netease.com/hzhumeng01/label_tool_classification_multilabel/raw/master/sups_img_for_readme/4.png"/></div>

图4 标定工具文件组织格式

操作流程比较简单：
1. 在Image Dir内填入图片路径，注意，只用填写子文件夹名如coat即可；
1. 点击load，加载该文件夹下所有图片；
1. 对每张图像标定multilabel属性；
1. 单张图片标定完成，点击next，进行下一张图片标定；

其他：

1. multilabel属性必须一次性全部标定，缺少属性标定将会报错；
1. 支持按文件名goto到特定图像；


#### 3.3 标定结果校验

具体可以参照check_label_valid.py文件，其功能在comments中有解释，用以校验每个标定的图像标签是否合规。

#### 3.4 训练验证列表生成

本小节完成训练/验证图像列表的生成，可以参照脚本create_trainval_test.py(其实是生成了train\val两类列表)。生成方式为读取所有标定的.txt文件内容，在标定内容前添加一个index索引，所有内容添加至一个list中，随即打乱，再按照VAL_RATIO设置的比例分为train\val两类列表，进而来支持mxnet的图像分类训练数据格式。


### 4. 附录

#### 4.1 使用代码列表清单

直接查看参考文献[3]即可。

### 5. 修订明细

| 修订号   |  修订时间  |  修订版本  |  修订人  | 修订说明 |
| :-----:  | :-----:    | :----:     | :-----:  | :----:   |
| 1        | 2018-01-25 |   V1.0     |   胡孟   |          |
| 2        |            |            |          |          |
| 3        |            |            |          |          |
| 4        |            |            |          |          |