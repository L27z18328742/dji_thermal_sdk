from dji_thermal_sdk.dji_sdk import *
# from dji_thermal_sdk.utility import rjpeg_to_heatmap
import dji_thermal_sdk.dji_sdk as DJI
import dji_thermal_sdk.utility as util
import ctypes as CT
from ctypes import *
import os,sys,requests
from io import BytesIO, StringIO
from urllib.parse import urlparse
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
import torch
import torchvision


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


def apply_nms(results, iou_threshold=0.5):

    boxes = results.boxes.xyxy # 取出框的坐标
    scores = results.boxes.conf  # 取出置信度分数
    # 转换为 numpy 数组
    boxes = boxes.cpu().numpy()
    scores = scores.cpu().numpy()

    # 应用非极大值抑制
    indices = torchvision.ops.nms(torch.tensor(boxes), torch.tensor(scores), iou_threshold)
    
    return boxes[indices]

def getJPEGHandle(image_url):
    '''
    parameters:
        [str] file_path: jpg file
    return:
        DIRP_HANDLE
    '''
    # rd = file_path
    # with open(rd, 'rb') as f:
    #     content = f.read()
    response = requests.get(image_url)
    content = BytesIO(response.content).read()

    # content = BytesIO(contents).read()
    # print(dir(content))

    # method1 to get the file size
    #print(f"File size: {os.path.getsize(rd)}")
    # method 2 to get the file size
    # file_stat = os.stat(content)
    # size = c_int32(file_stat.st_size)

    size = sys.getsizeof(content)
    # fileSize = dict(response.headers).get('content-length', 0)
    print("filesize:", size)
    # the method to create a string buffer, which is important.
    rjpeg_data = CT.create_string_buffer(len(content))
    rjpeg_data.value = content
    # test the function to create a handle of an image
    ret = dirp_create_from_rjpeg(content, size, CT.byref(DIRP_HANDLE))
    return ret

def rjpeg_to_heatmap(src:str,dtype='float32'):
    '''
    parameters:
        [str] src: file path of original jpg. For example, c:\\deer.jpg
        [str] dtype: 'float32' or 'int16'
    return:
        return numpy.ndarray -> img
    '''
    ret = getJPEGHandle(src)
    if ret != 0:
        raise ValueError(f"the rjpg file:{src} is not from DJI device")
    rjpeg_resolution = dirp_resolution_t()
    dirp_get_rjpeg_resolution(DIRP_HANDLE, CT.byref(rjpeg_resolution))
    img_h = rjpeg_resolution.height
    img_w = rjpeg_resolution.width
    # calculate the buffer size based on the resolution
    if dtype == 'int16':
        size = rjpeg_resolution.height * rjpeg_resolution.width *  CT.sizeof(CT.c_int16)
        # create a buffer for a raw image
        raw_image_buffer = CT.create_string_buffer(size)
        ret = dirp_measure(DIRP_HANDLE, CT.byref(raw_image_buffer), size)
        if ret != DIRP_SUCCESS:
            raise ValueError(f"Error: error code={ret}")
        file = os.path.basename(urlparse(src).path)
        file_name, _ = os.path.splitext(file)

        raw_file_path = file_name + ".raw"

        # raw_file_path = os.path.splitext(src)[0] + ".raw"

        with open(raw_file_path, 'wb') as f:
            f.write(raw_image_buffer.raw)
        with open(raw_file_path, encoding='cp1252') as fin:
            img = np.fromfile(fin, dtype = np.int16)
            img.shape = (img_h,img_w)
    else:
        size = rjpeg_resolution.height * rjpeg_resolution.width *  CT.sizeof(CT.c_float)
        # create a buffer for a raw image
        raw_image_buffer = CT.create_string_buffer(size)
        ret = dirp_measure_ex(DIRP_HANDLE, CT.byref(raw_image_buffer), size)
        if ret != DIRP_SUCCESS:
            raise ValueError(f"Error: error code={ret}")
        file = os.path.basename(urlparse(src).path)
        file_name, _ = os.path.splitext(file)

        raw_file_path = file_name + ".raw"

        with open(raw_file_path, 'wb') as f:
            f.write(raw_image_buffer.raw)
        with open(raw_file_path, encoding='cp1252') as fin:
            img = np.fromfile(fin, dtype = np.float32)
            img.shape = (img_h,img_w)
    # delete .raw file
    os.remove(raw_file_path)
    return img


def get_temperature_ndarray(src):

    if DJI._libdirp == "":
        print("run dji_init() to initialize the DJI sdk.")
    img = rjpeg_to_heatmap(src,dtype='int16')
    img = img / 10.0
    # fig = plt.figure(figsize=(10,8))
    # ax = sns.heatmap(img, cmap='gray')
    # ax.set_xticks([])
    # ax.set_yticks([])
    # plt.show()
    return img

# 定义一个函数，接受三个参数：image, threshold
def mark_hot_points(image_url, threshold):

    response = requests.get(image_url)
    content = BytesIO(response.content)
    image = Image.open(content)
    # 创建一个和image一样大小的空白图片
    flag = False
    new_image = Image.new('RGB', image.size, (255, 255, 255))
    temp = get_temperature_ndarray(image_url)
    # 创建一个画笔对象
    draw = ImageDraw.Draw(new_image)
    # 遍历temp数组，找到温度超过阈值的点
    for i in range(temp.shape[0]):
        for j in range(temp.shape[1]):
            if temp[i][j] >= threshold:
                # 在新图片上画一个红色的圆圈，半径为r像素，表示温度过高的点
                r = 2
                draw.ellipse((j - r, i - r, j + r, i + r), fill=(255, 0, 0))
                flag = True
    # 将原图片和新图片合并
    new_image = Image.blend(image, new_image, 0.5)
    # 返回新图片
    return new_image, flag, temp

if __name__ == '__main__':
    # 指定dji_thermal_sdk路径
    dji_thermal_sdk = "./"
    init_dji_sdk(dji_thermal_sdk)
    image_url = "https://img520.com/KjTwqG.jpg"

    temps = get_temperature_ndarray(image_url)
    print(temps)
    analyze_res, flag, is_exist_exception = mark_hot_points(image_url, 40)
#     photo_path = "dataset/H20T/DJI_0001_R.JPG"
#     threshold = 50
#     analyze_res, is_exist_exception = mark_hot_points(photo_path, threshold)
#     analyze_res.save("./test.jpg")
#     print("is_exist_exception:",is_exist_exception)