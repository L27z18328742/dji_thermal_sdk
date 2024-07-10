from dji_thermal_sdk.dji_sdk import *
from dji_thermal_sdk.utility import rjpeg_to_heatmap
import dji_thermal_sdk.dji_sdk as DJI
import dji_thermal_sdk.utility as util
import ctypes as CT
from ctypes import *
import os,sys
import matplotlib.pyplot as plt
import numpy as np
import PIL
from PIL import Image, ImageDraw

def init_dji_sdk(root):
    if sys.platform.startswith('linux'):
        dllpath = os.path.join(root,'tsdk-core/lib/linux/release_x64', 'libdirp.so')
        osname  = 'linux'
    else:
        dllpath = os.path.join(root,'tsdk-core\\lib\\windows\\release_x64', 'libdirp.dll')
        osname  = 'windows'

    if os.path.isfile(dllpath):
        print(f'current OS is {osname}, dllpath:{dllpath}')
    else:
        print("please download SDK from https://www.dji.com/downloads/softwares/dji-thermal-sdk")
    #
    dji_init(dllpath=dllpath, osname=osname)



def get_temperature_ndarray(src):

    if DJI._libdirp == "":
        print("run dji_init() to initialize the DJI sdk.")
    # src = r"dataset\Deer_Goats_Unsure.jpg"
    img = rjpeg_to_heatmap(src,dtype='int16')
    img = img / 10.0
    # fig = plt.figure(figsize=(10,8))
    # ax = sns.heatmap(img, cmap='gray')
    # ax.set_xticks([])
    # ax.set_yticks([])
    # plt.show()
    return img

# 定义一个函数，接受三个参数：image, threshold
def mark_hot_points(photo_path, threshold):

    image = PIL.Image.open(photo_path)
    # 创建一个和image一样大小的空白图片
    flag = False
    new_image = PIL.Image.new('RGB', image.size, (255, 255, 255))
    temp = get_temperature_ndarray(photo_path)
    # 创建一个画笔对象
    draw = PIL.ImageDraw.Draw(new_image)
    # 遍历temp数组，找到温度超过阈值的点
    for i in range(temp.shape[0]):
        for j in range(temp.shape[1]):
            if temp[i][j] >= threshold:
                # 在新图片上画一个红色的圆圈，半径为r像素，表示温度过高的点
                r = 2
                draw.ellipse((j - r, i - r, j + r, i + r), fill=(255, 0, 0))
                flag = True
    # 将原图片和新图片合并
    new_image = PIL.Image.blend(image, new_image, 0.5)
    # 返回新图片
    return new_image, flag, temp

if __name__ == '__main__':
    # 指定dji_thermal_sdk路径
    dji_thermal_sdk = "/home/tongtao.ling/ltt_code/dji_thermal_sdk"
    init_dji_sdk(dji_thermal_sdk)

    photo_path = "dataset/H20T/DJI_0001_R.JPG"
    threshold = 50
    analyze_res, is_exist_exception = mark_hot_points(photo_path, threshold)
    analyze_res.save("./test.jpg")
    print("is_exist_exception:",is_exist_exception)