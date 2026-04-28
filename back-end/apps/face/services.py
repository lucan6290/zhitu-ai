"""
业务服务层 - 人脸识别核心业务逻辑
包含图像处理、人脸识别、数据库操作等服务
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
    """图像处理服务 - 处理前端上传的Base64图像"""

    @staticmethod
    def get_image_byte(request: HttpRequest) -> bytes:
        """从请求中获取图像字节数据"""
        data = json.loads(request.body.decode('utf-8'))
        image_data = data['image'].split(',')[1]  # 去除data:image/jpeg;base64,前缀
        return base64.b64decode(image_data)

    @staticmethod
    def get_image_array(request: HttpRequest) -> np.ndarray:
        """从请求中获取 numpy 图像数组"""
        data = json.loads(request.body.decode('utf-8'))
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(image_bytes))

        # 调试信息：打印图像信息
        print(f"[DEBUG] 图像模式：{img.mode}, 尺寸：{img.size}, 类型：{type(img)}")

        # 确保转换为 RGB 模式
        if img.mode != 'RGB':
            img = img.convert('RGB')
            print(f"[DEBUG] 已转换为 RGB 模式")

        return np.array(img)


class FaceService:
    """人脸识别服务 - 基于face_recognition库"""
    TOLERANCE = 0.5  # 人脸匹配容差

    @staticmethod
    def get_face_encoding(image) -> Optional[np.ndarray]:
        """提取人脸特征编码"""
        # 支持 bytes / PIL.Image / numpy.ndarray 输入
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
            # 如果是 cv2 BGR 格式则转 RGB
            if image.ndim == 3 and image.shape[-1] == 3:
                image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        # 确保 uint8 + 连续内存
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
        """获取人脸位置坐标"""
        rgb_image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        return face_recognition.face_locations(rgb_image)

    @staticmethod
    def compare_faces(known_encoding: np.ndarray, unknown_encoding: np.ndarray) -> bool:
        """比较两个人脸特征是否匹配"""
        result = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=FaceService.TOLERANCE)
        return result[0] if result else False

    @staticmethod
    def load_face_from_file(file_path: str) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """从文件加载人脸特征"""
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
    def insert_user(name: str, age: int, phone: str, pwd: str) -> int:
        try:
            conn = DatabaseService.get_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO user_info(user_name, user_age, user_phone, user_pwd, created_at, updated_at) VALUES (%s, %s, %s, %s, NOW(), NOW())"
            cursor.execute(sql, (name, age, phone, pwd))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"数据库插入失败: {e}")
            if 'conn' in locals():
                conn.rollback()
            return 0
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
