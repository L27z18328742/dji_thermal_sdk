# 检测温度



## 检测图片中超出阈值的点

原图：

![](dataset/H20T/DJI_0001_R.JPG)

识别后结果：

![](processed_image_threshold.jpg)

## 检测图片中套管，并给出套管区域最高温度

原图：

![](dataset/14-20230523144700025699079060065986.jpg)

识别后结果：

![](processed_image_maxtemp.jpg)



## API调用

### 检测图片中超出阈值的点
```python
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
```

### 检测图片中套管，标出温度最高值

```python

@app.post("/process_insulator/")
async def process_insulator(request: ImageRequest):

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
```


