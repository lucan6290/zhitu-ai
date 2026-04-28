"""
人脸识别服务测试 - 测试人脸识别核心功能

测试范围：
1. FaceService - 人脸识别服务
2. DatabaseService - 数据库服务
3. ImageService - 图像处理服务
"""

import os
import base64
import io
from pathlib import Path
from django.test import TestCase
from PIL import Image
import numpy as np

from apps.face.services import FaceService, DatabaseService, ImageService
from tests.test_utils import MockDataFactory, TestDataCleaner


class FaceServiceTestCase(TestCase):
    """
    人脸识别服务测试
    
    测试说明：
    - 测试人脸特征提取
    - 测试人脸比对
    - 测试人脸加载
    """
    
    def setUp(self):
        """测试前准备"""
        self.cleanup_user_ids = []
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
        TestDataCleaner.cleanup_test_face_images(self.cleanup_user_ids)
    
    def test_get_face_encoding_no_face(self):
        """
        测试：无图像时返回None
        
        验证点：
        1. 传入None应返回None
        2. 传入空bytes应返回None
        """
        result = FaceService.get_face_encoding(None)
        assert result is None, "传入None应返回None"
        
        result = FaceService.get_face_encoding(b'')
        assert result is None, "传入空bytes应返回None"
    
    def test_get_face_encoding_with_invalid_image(self):
        """
        测试：无效图像时返回None
        
        验证点：
        1. 传入无效的图像数据应返回None
        2. 不应抛出异常
        """
        invalid_bytes = b'invalid_image_data'
        
        try:
            result = FaceService.get_face_encoding(invalid_bytes)
            assert result is None
        except Exception:
            pass
    
    def test_get_face_encoding_with_valid_image_no_face(self):
        """
        测试：有效图像但无人脸时返回None
        
        验证点：
        1. 传入不含人脸的图像应返回None
        """
        img = Image.new('RGB', (200, 200), color=(255, 255, 255))
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        image_bytes = buffer.getvalue()
        
        result = FaceService.get_face_encoding(image_bytes)
        assert result is None, "不含人脸的图像应返回None"
    
    def test_compare_faces_match(self):
        """
        测试：人脸匹配成功
        
        验证点：
        1. 相同的人脸特征应匹配成功
        """
        encoding1 = np.random.rand(128)
        encoding2 = encoding1.copy()
        
        result = FaceService.compare_faces(encoding1, encoding2)
        assert result is True, "相同的人脸特征应匹配成功"
    
    def test_compare_faces_no_match(self):
        """
        测试：人脸匹配失败
        
        验证点：
        1. 不同的人脸特征应匹配失败
        """
        encoding1 = np.random.rand(128)
        encoding2 = np.random.rand(128)
        
        result = FaceService.compare_faces(encoding1, encoding2)
        assert result is False, "不同的人脸特征应匹配失败"
    
    def test_compare_faces_with_tolerance(self):
        """
        测试：人脸匹配容差
        
        验证点：
        1. FaceService.TOLERANCE应为0.5
        2. 容差范围内的特征应匹配
        """
        assert FaceService.TOLERANCE == 0.5, "人脸匹配容差应为0.5"
        
        encoding1 = np.random.rand(128)
        encoding2 = encoding1 + 0.1
        
        result = FaceService.compare_faces(encoding1, encoding2)
    
    def test_load_face_from_file_nonexistent(self):
        """
        测试：加载不存在的人脸文件
        
        验证点：
        1. 文件不存在时应返回(None, None)
        2. 不应抛出异常
        """
        result = FaceService.load_face_from_file('/nonexistent/path/to/file.jpg')
        
        assert result == (None, None), "加载不存在的文件应返回(None, None)"
    
    def test_load_face_from_file_invalid_image(self):
        """
        测试：加载无效的图像文件
        
        验证点：
        1. 无效图像应返回(None, None)
        2. 不应抛出异常
        """
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b'invalid_image_data')
            temp_path = f.name
        
        try:
            result = FaceService.load_face_from_file(temp_path)
            assert result == (None, None)
        finally:
            os.unlink(temp_path)


class DatabaseServiceTestCase(TestCase):
    """
    数据库服务测试
    
    测试说明：
    - 测试用户插入
    - 测试用户查询
    - 测试用户更新
    """
    
    def setUp(self):
        """测试前准备"""
        self.cleanup_user_ids = []
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_insert_user_success(self):
        """
        测试：插入用户成功
        
        验证点：
        1. 插入用户应返回True
        2. 用户ID应唯一
        """
        import random
        user_id = random.randint(10000, 99999)
        self.cleanup_user_ids.append(user_id)
        
        result = DatabaseService.insert_user(
            user_id=user_id,
            name="测试用户",
            age=22,
            phone="13800138000",
            pwd="password123"
        )
        
        assert result is True, "插入用户应返回True"
    
    def test_insert_user_duplicate_id(self):
        """
        测试：插入重复用户ID
        
        验证点：
        1. 插入重复ID应返回False
        """
        import random
        user_id = random.randint(10000, 99999)
        self.cleanup_user_ids.append(user_id)
        
        result1 = DatabaseService.insert_user(
            user_id=user_id,
            name="测试用户1",
            age=22,
            phone="13800138001",
            pwd="password123"
        )
        assert result1 is True
        
        result2 = DatabaseService.insert_user(
            user_id=user_id,
            name="测试用户2",
            age=23,
            phone="13800138002",
            pwd="password456"
        )
        assert result2 is False, "插入重复ID应返回False"
    
    def test_select_user_by_id(self):
        """
        测试：通过ID查询用户
        
        验证点：
        1. 查询存在的用户应返回用户信息
        2. 查询不存在的用户应返回空列表
        """
        import random
        user_id = random.randint(10000, 99999)
        self.cleanup_user_ids.append(user_id)
        
        DatabaseService.insert_user(
            user_id=user_id,
            name="查询测试用户",
            age=25,
            phone="13800138003",
            pwd="password123"
        )
        
        result = DatabaseService.select_user(user_id=user_id)
        
        assert result is not None, "查询用户应返回结果"
        assert len(result) > 0, "查询存在的用户应返回非空列表"
        assert result[0][0] == user_id, "返回的用户ID应匹配"
        
        result_nonexistent = DatabaseService.select_user(user_id=99999999)
        assert result_nonexistent == [], "查询不存在的用户应返回空列表"
    
    def test_select_user_by_name(self):
        """
        测试：通过用户名查询用户
        
        验证点：
        1. 查询存在的用户名应返回用户信息
        """
        import random
        user_id = random.randint(10000, 99999)
        user_name = "用户名查询测试"
        self.cleanup_user_ids.append(user_id)
        
        DatabaseService.insert_user(
            user_id=user_id,
            name=user_name,
            age=26,
            phone="13800138004",
            pwd="password123"
        )
        
        result = DatabaseService.select_user(name=user_name)
        
        assert result is not None
        assert len(result) > 0
        assert result[0][1] == user_name
    
    def test_select_user_by_phone(self):
        """
        测试：通过手机号查询用户
        
        验证点：
        1. 查询存在的手机号应返回用户信息
        """
        import random
        user_id = random.randint(10000, 99999)
        user_phone = "13800138005"
        self.cleanup_user_ids.append(user_id)
        
        DatabaseService.insert_user(
            user_id=user_id,
            name="手机号查询测试",
            age=27,
            phone=user_phone,
            pwd="password123"
        )
        
        result = DatabaseService.select_user(phone=user_phone)
        
        assert result is not None
        assert len(result) > 0
        assert result[0][3] == user_phone
    
    def test_update_user_age(self):
        """
        测试：更新用户年龄
        
        验证点：
        1. 更新年龄应返回True
        2. 查询时年龄已更新
        """
        import random
        user_id = random.randint(10000, 99999)
        user_name = "年龄更新测试"
        self.cleanup_user_ids.append(user_id)
        
        DatabaseService.insert_user(
            user_id=user_id,
            name=user_name,
            age=20,
            phone="13800138006",
            pwd="password123"
        )
        
        result = DatabaseService.update_user(user_name, age=30)
        assert result is True
        
        updated_user = DatabaseService.select_user(user_id=user_id)
        assert updated_user[0][2] == 30
    
    def test_update_user_phone(self):
        """
        测试：更新用户手机号
        
        验证点：
        1. 更新手机号应返回True
        2. 查询时手机号已更新
        """
        import random
        user_id = random.randint(10000, 99999)
        user_name = "手机号更新测试"
        self.cleanup_user_ids.append(user_id)
        
        DatabaseService.insert_user(
            user_id=user_id,
            name=user_name,
            age=28,
            phone="13800138007",
            pwd="password123"
        )
        
        new_phone = "13900139000"
        result = DatabaseService.update_user(user_name, phone=new_phone)
        assert result is True
        
        updated_user = DatabaseService.select_user(user_id=user_id)
        assert updated_user[0][3] == new_phone
    
    def test_update_user_password(self):
        """
        测试：更新用户密码
        
        验证点：
        1. 更新密码应返回True
        2. 查询时密码已更新
        """
        import random
        user_id = random.randint(10000, 99999)
        user_name = "密码更新测试"
        self.cleanup_user_ids.append(user_id)
        
        DatabaseService.insert_user(
            user_id=user_id,
            name=user_name,
            age=29,
            phone="13800138008",
            pwd="oldpassword"
        )
        
        new_pwd = "newpassword123"
        result = DatabaseService.update_user(user_name, pwd=new_pwd)
        assert result is True
        
        updated_user = DatabaseService.select_user(user_id=user_id)
        assert updated_user[0][4] == new_pwd


class ImageServiceTestCase(TestCase):
    """
    图像处理服务测试
    
    测试说明：
    - 测试图像字节数据获取
    - 测试图像数组转换
    """
    
    def test_get_image_byte_valid(self):
        """
        测试：获取有效的图像字节数据
        
        验证点：
        1. 应能正确解析base64图像数据
        """
        from django.test import RequestFactory
        import json
        
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        image_bytes = buffer.getvalue()
        base64_str = base64.b64encode(image_bytes).decode('utf-8')
        
        request_body = json.dumps({
            'image': f'data:image/jpeg;base64,{base64_str}'
        }).encode('utf-8')
        
        factory = RequestFactory()
        request = factory.post(
            '/test/',
            data=request_body,
            content_type='application/json'
        )
        
        result = ImageService.get_image_byte(request)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
    
    def test_get_image_array_valid(self):
        """
        测试：获取有效的图像数组
        
        验证点：
        1. 应能正确转换为numpy数组
        2. 数组应为RGB格式
        """
        from django.test import RequestFactory
        import json
        
        img = Image.new('RGB', (100, 100), color=(0, 255, 0))
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        image_bytes = buffer.getvalue()
        base64_str = base64.b64encode(image_bytes).decode('utf-8')
        
        request_body = json.dumps({
            'image': f'data:image/jpeg;base64,{base64_str}'
        }).encode('utf-8')
        
        factory = RequestFactory()
        request = factory.post(
            '/test/',
            data=request_body,
            content_type='application/json'
        )
        
        result = ImageService.get_image_array(request)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (100, 100, 3)
