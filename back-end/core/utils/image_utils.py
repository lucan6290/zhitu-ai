"""
图像处理工具 - 处理Base64图像数据
"""

import json
import base64
import io
from typing import Optional, Tuple
from PIL import Image
import numpy as np
from django.http import HttpRequest


def get_image_byte(request: HttpRequest) -> bytes:
    """从请求中获取图像字节数据"""
    data = json.loads(request.body.decode('utf-8'))
    image_data = data['image'].split(',')[1]  # 去除Base64前缀
    return base64.b64decode(image_data)


def get_image_array(request: HttpRequest) -> np.ndarray:
    """从请求中获取numpy图像数组"""
    data = json.loads(request.body.decode('utf-8'))
    image_data = data['image'].split(',')[1]
    image_bytes = base64.b64decode(image_data)
    img = Image.open(io.BytesIO(image_bytes))
    return np.array(img)
