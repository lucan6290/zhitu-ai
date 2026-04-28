"""
人脸识别测试用例
"""

from django.test import TestCase
from apps.face.services import ImageService, FaceService, DatabaseService


class FaceServiceTestCase(TestCase):
    """人脸服务测试"""

    def test_get_face_encoding_no_face(self):
        """测试：无图像时返回None"""
        pass

    def test_compare_faces_match(self):
        """测试：人脸匹配成功"""
        pass

    def test_compare_faces_no_match(self):
        """测试：人脸匹配失败"""
        pass


class DatabaseServiceTestCase(TestCase):
    """数据库服务测试"""

    def test_insert_user(self):
        """测试：插入用户"""
        pass

    def test_select_user(self):
        """测试：查询用户"""
        pass
