import requests
import base64

def test_image_threshold(image_url, threshold):
    url = "http://127.0.0.1:8321/process_image_threshold/"

    payload = {
        "image_url": image_url,
        "threshold": threshold
    }
    
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        response_data = response.json()
        # 返回图片和温度
        encoded_image = response_data['image']
        temperatures = response_data['temperatures']
        is_exist_exception = response_data['is_exist_exception']
        time = response_data['time']

        print("is_exist_exception:", is_exist_exception)
        print("time:", time)
        # 将Base64编码的图片数据解码并保存
        image_data = base64.b64decode(encoded_image)
        with open("./processed_image_threshold.jpg", "wb") as f:
            f.write(image_data)
        print(f"Image processed and saved as 'processed_image_threshold.jpg'")

    else:
        print("Failed to process image")


def test_image_maxtemp(image_url):
    url = "http://127.0.0.1:8321/process_insulator/"

    payload = {
        "image_url": image_url,
    }
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        response_data = response.json()
        encoded_image = response_data['image']

        boxes = response_data['boxes']
        max_temps = response_data['max_temps']
        time = response_data['time']

        print("boxes:", boxes)
        print("max_temps:", max_temps)
        print("time:", time)

        # 将Base64编码的图片数据解码并保存
        image_data = base64.b64decode(encoded_image)
        with open("./processed_image_maxtemp.jpg", "wb") as f:
            f.write(image_data)
        print(f"Image processed and saved as 'processed_image_maxtemp.jpg'")

    else:
        print("Failed to process image")

if __name__ == "__main__":
    image_path = "https://img520.com/KjTwqG.jpg"
    test_image_threshold(image_path, 40)

    image_path = "https://img520.com/vYcT7s.jpg"
    test_image_maxtemp(image_path)
