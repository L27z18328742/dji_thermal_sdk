import requests
import cv2
import base64
import json
import numpy as np
from io import BytesIO


def test_image_threshold(image_path, threshold):
    url = "http://127.0.0.1:8231/process_image_threshold/"
    with open(image_path, "rb") as file:
        response = requests.post(url, files={"file": file}, data = {"threshold": threshold})
    
    if response.status_code == 200:
        response_data = response.json()
        # 返回图片和温度
        encoded_image = response_data['image']
        temperatures = response_data['temperatures']

        # 将Base64编码的图片数据解码并保存
        image_data = base64.b64decode(encoded_image)
        with open("test_result/processed_image_threshold.jpg", "wb") as f:
            f.write(image_data)
        print(f"Image processed and saved as 'test_result/processed_image.jpg'")

    else:
        print("Failed to process image")


def test_image_maxtemp(image_path):
    url = "http://127.0.0.1:8231/process_insulator/"
    with open(image_path, "rb") as file:
        response = requests.post(url, files={"file": file})

    if response.status_code == 200:
        response_data = response.json()
        encoded_image = response_data['image']

        # 将Base64编码的图片数据解码并保存
        image_data = base64.b64decode(encoded_image)
        with open("test_result/processed_image_maxtemp.jpg", "wb") as f:
            f.write(image_data)
        print(f"Image processed and saved as 'test_result/processed_image.jpg'")

    else:
        print("Failed to process image")

if __name__ == "__main__":
    image_path = '/home/tongtao.ling/ltt_code/dji_thermal_sdk/dataset/H20T/DJI_0001_R.JPG'
    test_image_threshold(image_path, 40)

    image_path = '/home/tongtao.ling/ltt_code/dji_thermal_sdk/test_file/4-20230414095543435907483722880227.jpg'
    test_image_maxtemp(image_path)
