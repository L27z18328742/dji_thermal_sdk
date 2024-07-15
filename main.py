from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from fastapi.responses import JSONResponse
from dji_sdk import mark_hot_points, init_dji_sdk, get_temperature_ndarray, apply_nms
import uvicorn
import os
import io
import base64
import shutil
import cv2
import datetime
from urllib.parse import urlparse
import numpy as np
from ultralytics import YOLO
from config import dji_thermal_sdk, yolo_checkpoint

model = YOLO(yolo_checkpoint)

# 初始化大疆sdk
init_dji_sdk(dji_thermal_sdk)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)


class ImageRequestWithThreshold(BaseModel):
    image_url: str
    threshold: float

class ImageRequest(BaseModel):
    image_url: str


@app.post("/process_image_threshold/")
async def process_image_threshold(request: ImageRequestWithThreshold):

    analyze_res, is_exist_exception, temperatures = mark_hot_points(request.image_url, request.threshold)

    temperatures = np.array(temperatures).tolist()

    # 将处理后的图片保存到字节流
    byte_arr = io.BytesIO()
    analyze_res.save(byte_arr, format='JPEG')
    byte_arr.seek(0)

     # 将图片转换为Base64编码
    encoded_image = base64.b64encode(byte_arr.getvalue()).decode('utf-8')

    now = datetime.datetime.now()
    now_time = now.strftime("%Y-%m-%d %H:%M:%S")

    return JSONResponse(content={"status_code": 200,
                                 "temperatures": temperatures, 
                                 "image": encoded_image, 
                                 "is_exist_exception": is_exist_exception, 
                                 "time": now_time})


@app.post("/process_insulator/")
async def process_insulator(request: ImageRequest):
    # try:
    #     # 下载图片
    #     response = requests.get(request.image_url)
    #     filename = request.image_url.split("/")[-1]
    #     if response.status_code == 200:
    #         raw_path = "./{}".format(filename)
    #         with open(raw_path, "wb") as f:
    #             f.write(response.content)
    #     else:
    #         return {"error": "Failed to download image from URL"}
    # except Exception as e:
    #     return {"error": str(e)}
    
    # img = cv2.imread(request.image_url)

    # 请求 URL
    response = requests.get(request.image_url)

    # 将获取到的数据转为 numpy array 格式
    arr = np.asarray(bytearray(response.content), dtype=np.uint8)

    # 使用 cv2.imdecode 读取图片数据
    img = cv2.imdecode(arr, -1) # cv2.IMREAD_COLOR 表示读取彩色图片，cv2.IMREAD_GRAYSCALE 表示灰度处理

    temperatures = get_temperature_ndarray(request.image_url)

    predicted_results = model.predict(request.image_url, show_conf = True, device="cpu")

    boxes = apply_nms(predicted_results[0])

    boxes = boxes.astype(np.int32).tolist()

    _, byte_arr = cv2.imencode(".jpg", img)

    max_temps = []
    for box in boxes:
        x_min, y_min, x_max, y_max = box

        max_temp = np.max(temperatures[y_min:y_max, x_min:x_max])
        max_temps.append(max_temp)
        # 在图片上绘制矩形框
        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (255, 255, 255), 2)
        center_y = (y_min + y_max) // 2

        # 获取文本的大小
        text = f"{max_temp:.2f}"
        font_scale = 0.5  # 字体大小与之前一致
        font_thickness = 2

        # 获取文本的大小
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)

        # 计算文本的中心点
        text_x = x_min + (x_max - x_min - text_width) // 2
        text_y = center_y + text_height // 2
        # 绘制文本
        cv2.putText(img, text, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)

    _, byte_arr = cv2.imencode(".jpg", img)

    # 将图片转换为Base64编码
    encoded_image = base64.b64encode(byte_arr).decode('utf-8')

    now = datetime.datetime.now()
    now_time = now.strftime("%Y-%m-%d %H:%M:%S")

    file = os.path.basename(urlparse(request.image_url).path)

    os.remove(file)

    return JSONResponse(content={"status_code": 200,
                                 "image": encoded_image, 
                                 "boxes": boxes, 
                                 "max_temps": max_temps,
                                 "time": now_time})

if __name__ == "__main__":
    # uvicorn.run("main:app", host="0.0.0.0", port=8231, reload=True, workers=1)
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
