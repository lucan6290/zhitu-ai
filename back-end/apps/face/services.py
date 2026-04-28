"""
业务服务层模块
=============

本模块提供人脸识别应用的核心业务逻辑，包括：
- 图像处理：Base64解码、格式转换
- 人脸识别：特征提取、人脸比对
- 数据库操作：用户CRUD操作
- 随机数生成：唯一ID生成

服务类：
- ImageService: 图像处理服务
- FaceService: 人脸识别服务
- DatabaseService: 数据库操作服务
- RandomService: 随机数生成服务

依赖说明：
- face_recognition: 人脸识别库（基于dlib）
- PIL: 图像处理库
- cv2: OpenCV图像处理
- pymysql: MySQL数据库驱动

使用示例：
    from apps.face.services import FaceService, DatabaseService
    
    # 提取人脸特征
    encoding = FaceService.get_face_encoding(image_bytes)
    
    # 比对人脸
    is_match = FaceService.compare_faces(known_encoding, unknown_encoding)
"""

import os
import json
import base64
import io
from pathlib import Path
from typing import Optional, Tuple, List
from PIL import Image
import numpy as np
import face_recognition
import cv2 as cv
import pymysql
from django.conf import settings
from django.http import HttpRequest


class ImageService:
    """
    图像处理服务类
    
    处理前端上传的Base64编码图像，转换为可用于人脸识别的格式。
    
    Methods:
        get_image_byte: 从请求中提取图像字节数据
        get_image_array: 从请求中提取numpy图像数组
    
    Example:
        image_bytes = ImageService.get_image_byte(request)
        image_array = ImageService.get_image_array(request)
    """
    
    @staticmethod
    def get_image_byte(request: HttpRequest) -> bytes:
        """
        从HTTP请求中提取图像字节数据
        
        解析请求体中的Base64编码图像，去除data URL前缀。
        
        Args:
            request: Django HTTP请求对象
                - body应包含JSON格式的图像数据
                - 图像格式：data:image/jpeg;base64,{base64_data}
        
        Returns:
            bytes: 解码后的图像字节数据
        
        Raises:
            JSONDecodeError: 请求体不是有效JSON
            KeyError: 缺少image字段
        
        Example:
            >>> image_bytes = ImageService.get_image_byte(request)
            >>> with open('image.jpg', 'wb') as f:
            ...     f.write(image_bytes)
        """
        data = json.loads(request.body.decode('utf-8'))
        image_data = data['image'].split(',')[1]
        return base64.b64decode(image_data)

    @staticmethod
    def get_image_array(request: HttpRequest) -> np.ndarray:
        """
        从HTTP请求中提取numpy图像数组
        
        将Base64图像转换为RGB格式的numpy数组，用于人脸识别。
        
        Args:
            request: Django HTTP请求对象
        
        Returns:
            np.ndarray: RGB格式的图像数组，shape为(H, W, 3)
        
        Note:
            - 自动将非RGB图像转换为RGB格式
            - 输出调试信息便于排查问题
        """
        data = json.loads(request.body.decode('utf-8'))
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(image_bytes))

        print(f"[DEBUG] 图像模式：{img.mode}, 尺寸：{img.size}, 类型：{type(img)}")

        if img.mode != 'RGB':
            img = img.convert('RGB')
            print(f"[DEBUG] 已转换为 RGB 模式")

        return np.array(img)


class FaceService:
    """
    人脸识别服务类
    
    基于face_recognition库提供人脸检测、特征提取和人脸比对功能。
    使用HOG模型进行人脸检测，128维特征向量进行人脸编码。
    
    Attributes:
        TOLERANCE: 人脸匹配容差阈值，默认0.5
            - 值越小，匹配越严格
            - 0.4-0.6为常用范围
    
    Methods:
        get_face_encoding: 提取人脸特征编码
        get_face_locations: 获取人脸位置坐标
        compare_faces: 比较两个人脸是否匹配
        load_face_from_file: 从文件加载人脸特征
    
    Example:
        >>> encoding = FaceService.get_face_encoding(image_bytes)
        >>> is_match = FaceService.compare_faces(known_encoding, encoding)
    """
    
    TOLERANCE = 0.5

    @staticmethod
    def get_face_encoding(image) -> Optional[np.ndarray]:
        """
        提取人脸特征编码
        
        从图像中检测人脸并提取128维特征向量。
        支持多种输入格式，自动进行格式转换。
        
        Args:
            image: 输入图像，支持以下格式：
                - bytes: 图像字节数据
                - PIL.Image: PIL图像对象
                - np.ndarray: numpy数组（H, W, 3）
        
        Returns:
            np.ndarray | None: 128维人脸特征向量，未检测到人脸返回None
        
        Processing:
            1. 格式转换：确保输入为RGB格式的uint8连续数组
            2. 人脸检测：使用HOG模型定位人脸
            3. 特征提取：生成128维特征向量
        
        Note:
            - 使用HOG模型，速度快但精度略低于CNN
            - 仅返回第一张人脸的特征
        """
        if isinstance(image, bytes):
            pil_image = Image.open(io.BytesIO(image))
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            image = np.array(pil_image)
        elif isinstance(image, Image.Image):
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image = np.array(image)
        elif isinstance(image, np.ndarray):
            if image.ndim == 3 and image.shape[-1] == 3:
                image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        if image.dtype != np.uint8:
            image = image.astype(np.uint8)
        if not image.flags['C_CONTIGUOUS']:
            image = np.ascontiguousarray(image)

        print(f"[DEBUG] get_face_encoding: shape={image.shape}, dtype={image.dtype}, C_CONTIGUOUS={image.flags['C_CONTIGUOUS']}")

        locations = face_recognition.face_locations(image, model='hog')
        if len(locations) == 0:
            print("[DEBUG] 未检测到人脸")
            return None
        encodings = face_recognition.face_encodings(image, locations)
        return encodings[0] if encodings else None

    @staticmethod
    def get_face_locations(image: np.ndarray) -> List[tuple]:
        """
        获取人脸位置坐标
        
        检测图像中所有人脸的位置。
        
        Args:
            image: BGR格式的numpy图像数组
        
        Returns:
            List[tuple]: 人脸位置列表，每个元素为(top, right, bottom, left)
        """
        rgb_image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        return face_recognition.face_locations(rgb_image)

    @staticmethod
    def compare_faces(known_encoding: np.ndarray, unknown_encoding: np.ndarray) -> bool:
        """
        比较两个人脸特征是否匹配
        
        使用欧氏距离计算特征向量相似度，判断是否为同一人。
        
        Args:
            known_encoding: 已知人脸的特征向量
            unknown_encoding: 待比对的人脸特征向量
        
        Returns:
            bool: True表示匹配，False表示不匹配
        
        Algorithm:
            计算两个128维向量的欧氏距离，小于TOLERANCE则认为匹配
        """
        result = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=FaceService.TOLERANCE)
        return result[0] if result else False

    @staticmethod
    def load_face_from_file(file_path: str) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        从文件加载人脸特征
        
        读取图像文件并提取人脸特征和位置。
        
        Args:
            file_path: 图像文件路径
        
        Returns:
            Tuple[encoding, location]: 
                - encoding: 人脸特征向量，失败返回None
                - location: 人脸位置坐标，失败返回None
        
        Note:
            仅返回第一张人脸的信息
        """
        try:
            image = face_recognition.load_image_file(file_path)
            locations = face_recognition.face_locations(image)
            if len(locations) == 0:
                return None, None
            encodings = face_recognition.face_encodings(image, locations)
            return encodings[0] if encodings else None, locations[0] if locations else None
        except Exception:
            return None, None


class DatabaseService:
    """数据库服务 - MySQL数据库操作"""

    @staticmethod
    def get_connection():
        """获取数据库连接"""
        config = settings.DATABASE_CONFIG
        return pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['name'],
            charset=config['charset']
        )

    @staticmethod
    def insert_user(user_id: int, name: str, age: int, phone: str, pwd: str) -> bool:
        """插入用户信息"""
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO user_info(user_id, user_name, user_age, user_phone, user_pwd, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())"
            cursor.execute(sql, (user_id, name, age, phone, pwd))
            conn.commit()
            return True
        except Exception as e:
            print(f"数据库插入失败：{e}")
            if 'conn' in locals():
                conn.rollback()
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def select_user(user_id: int = None, phone: str = None, name: str = None) -> Optional[List[tuple]]:
        """查询用户信息"""
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            if user_id is not None:
                sql = "SELECT * FROM user_info WHERE user_id=%s"
                cursor.execute(sql, (user_id,))
            elif phone is not None:
                sql = "SELECT * FROM user_info WHERE user_phone=%s"
                cursor.execute(sql, (phone,))
            elif name is not None:
                sql = "SELECT * FROM user_info WHERE user_name=%s"
                cursor.execute(sql, (name,))
            else:
                return []
            result = cursor.fetchall()
            return list(result) if result else []
        except Exception as e:
            print(f"数据库查询失败: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()


    @staticmethod
    def update_user(name: str, age: int = None, phone: str = None, pwd: str = None) -> bool:
        """更新用户信息"""
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            fields = []
            values = []
            if age is not None:
                fields.append("user_age=%s")
                values.append(age)
            if phone is not None:
                fields.append("user_phone=%s")
                values.append(phone)
            if pwd is not None:
                fields.append("user_pwd=%s")
                values.append(pwd)
            if fields:
                fields.append("updated_at=NOW()")
                values.append(name)
                sql = f"UPDATE user_info SET {', '.join(fields)} WHERE user_name=%s"
                cursor.execute(sql, values)
                conn.commit()
                return True
            return False
        except Exception as e:
            print(f"数据库更新失败: {e}")
            if 'conn' in locals():
                conn.rollback()
            return False
        finally:
            if 'conn' in locals():
                conn.close()

class RandomService:
    """随机数服务 - 生成唯一随机ID"""
    FILE_PATH = Path(settings.BASE_DIR) / 'generated_numbers.json'

    @staticmethod
    def load_generated_numbers() -> set:
        """加载已生成的数字集合"""
        if RandomService.FILE_PATH.exists():
            try:
                with open(RandomService.FILE_PATH, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        return set()
                    return set(json.loads(content))
            except (json.JSONDecodeError, ValueError):
                return set()
        return set()

    @staticmethod
    def save_generated_numbers(numbers: set):
        """保存已生成的数字集合"""
        with open(RandomService.FILE_PATH, 'w') as f:
            json.dump(list(numbers), f)

    @staticmethod
    def generate_unique_random(min_num: int, max_num: int) -> int:
        """生成指定范围内的唯一随机数"""
        generated = RandomService.load_generated_numbers()
        available = set(range(min_num, max_num + 1)) - generated
        if not available:
            raise ValueError("所有可能的数字都已经生成过了")
        number = int(np.random.choice(list(available)))
        generated.add(number)
        RandomService.save_generated_numbers(generated)
        return number
