"""
测试工具模块 - 提供测试辅助函数和模拟数据
"""

import base64
import io
import json
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
import numpy as np
from django.test import Client
from django.contrib.sessions.backends.db import SessionStore


class TestClient:
    """测试客户端封装 - 提供便捷的API测试方法"""
    
    def __init__(self):
        self.client = Client()
        self.session_data = {}
    
    def login_as_user(self, user_id: int, user_name: str = "测试用户"):
        """模拟用户登录状态"""
        session = SessionStore()
        session['user_id'] = user_id
        session['user_name'] = user_name
        session.save()
        
        self.client.cookies['sessionid'] = session.session_key
        self.session_data = {
            'user_id': user_id,
            'user_name': user_name
        }
    
    def logout(self):
        """清除登录状态"""
        self.client = Client()
        self.session_data = {}
    
    def post_json(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送JSON POST请求"""
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        return self._parse_response(response)
    
    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送GET请求"""
        response = self.client.get(url, params or {})
        return self._parse_response(response)
    
    def delete(self, url: str) -> Dict[str, Any]:
        """发送DELETE请求"""
        response = self.client.delete(url)
        return self._parse_response(response)
    
    def _parse_response(self, response) -> Dict[str, Any]:
        """解析响应"""
        try:
            return {
                'status_code': response.status_code,
                'data': json.loads(response.content.decode('utf-8')),
                'response': response
            }
        except Exception:
            return {
                'status_code': response.status_code,
                'data': response.content.decode('utf-8'),
                'response': response
            }


class MockDataFactory:
    """模拟数据工厂 - 生成测试数据"""
    
    @staticmethod
    def create_user_data(
        user_name: str = "测试用户",
        user_pwd: str = "password123",
        user_age: int = 22,
        user_phone: str = "13800138000",
        invitation_code: str = "INVITE2026"
    ) -> Dict[str, Any]:
        """创建用户注册数据"""
        return {
            "user_name": user_name,
            "user_pwd": user_pwd,
            "user_age": user_age,
            "user_phone": user_phone,
            "invitation_code": invitation_code
        }
    
    @staticmethod
    def create_login_data(
        login_account: str = "测试用户",
        user_pwd: str = "password123"
    ) -> Dict[str, Any]:
        """创建登录数据"""
        return {
            "login_account": login_account,
            "user_pwd": user_pwd
        }
    
    @staticmethod
    def create_face_image_base64(width: int = 200, height: int = 200, color: tuple = (255, 200, 150)) -> str:
        """创建模拟人脸图片的Base64编码"""
        img = Image.new('RGB', (width, height), color)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        image_bytes = buffer.getvalue()
        base64_str = base64.b64encode(image_bytes).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_str}"
    
    @staticmethod
    def create_session_data(title: str = "测试会话") -> Dict[str, Any]:
        """创建会话数据"""
        return {
            "title": title
        }
    
    @staticmethod
    def create_chat_message(
        session_id: int,
        content: str = "测试消息内容",
        deep_thinking: bool = False
    ) -> Dict[str, Any]:
        """创建聊天消息数据"""
        return {
            "session_id": session_id,
            "content": content,
            "deep_thinking": deep_thinking
        }
    
    @staticmethod
    def create_profile_update_data(
        action: str = "update",
        user_age: Optional[int] = None,
        user_phone: Optional[str] = None,
        new_user_pwd: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建用户信息更新数据"""
        data = {"action": action}
        if user_age is not None:
            data["user_age"] = user_age
        if user_phone is not None:
            data["user_phone"] = user_phone
        if new_user_pwd is not None:
            data["new_user_pwd"] = new_user_pwd
        return data


class AssertionHelper:
    """断言辅助类 - 提供常用的断言方法"""
    
    @staticmethod
    def assert_success_response(response_data: Dict[str, Any], expected_code: int = 200):
        """断言成功响应"""
        assert response_data['data']['code'] == expected_code, \
            f"期望状态码 {expected_code}, 实际 {response_data['data']['code']}"
        assert response_data['data']['msg'] == 'success' or response_data['data']['msg'] == 'updated', \
            f"期望消息为 'success' 或 'updated', 实际 '{response_data['data']['msg']}'"
    
    @staticmethod
    def assert_error_response(response_data: Dict[str, Any], expected_code: int, expected_msg: str = None):
        """断言错误响应"""
        assert response_data['data']['code'] == expected_code, \
            f"期望错误码 {expected_code}, 实际 {response_data['data']['code']}"
        if expected_msg:
            assert expected_msg in response_data['data']['msg'], \
                f"期望错误消息包含 '{expected_msg}', 实际 '{response_data['data']['msg']}'"
    
    @staticmethod
    def assert_response_has_fields(response_data: Dict[str, Any], fields: list):
        """断言响应包含指定字段"""
        data = response_data['data'].get('data', {})
        for field in fields:
            assert field in data, f"响应数据缺少字段: {field}"
    
    @staticmethod
    def assert_datetime_format(datetime_str: str):
        """断言时间格式为ISO 8601"""
        assert 'T' in datetime_str, f"时间格式不正确，应为ISO 8601格式，实际: {datetime_str}"
        parts = datetime_str.split('T')
        assert len(parts) == 2, f"时间格式不正确: {datetime_str}"


class PerformanceTimer:
    """性能计时器 - 用于测试接口响应时间"""
    
    def __init__(self):
        import time
        self.time = time
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """开始计时"""
        self.start_time = self.time.time()
    
    def stop(self):
        """停止计时"""
        self.end_time = self.time.time()
    
    def elapsed(self) -> float:
        """获取耗时（秒）"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def assert_faster_than(self, seconds: float):
        """断言响应时间小于指定秒数"""
        elapsed = self.elapsed()
        assert elapsed < seconds, f"响应时间 {elapsed:.2f}s 超过预期 {seconds}s"


class TestDataCleaner:
    """测试数据清理器 - 清理测试产生的数据"""
    
    @staticmethod
    def cleanup_test_users(user_ids: list):
        """清理测试用户"""
        from apps.face.services import DatabaseService
        for user_id in user_ids:
            try:
                conn = DatabaseService.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM user_info WHERE user_id = %s", (user_id,))
                conn.commit()
            except Exception as e:
                print(f"清理用户 {user_id} 失败: {e}")
            finally:
                if 'conn' in locals():
                    conn.close()
    
    @staticmethod
    def cleanup_test_sessions(session_ids: list):
        """清理测试会话"""
        from apps.chat.models import ChatSession, ChatMessage
        ChatMessage.objects.filter(session_id__in=session_ids).delete()
        ChatSession.objects.filter(session_id__in=session_ids).delete()
    
    @staticmethod
    def cleanup_test_face_images(user_ids: list):
        """清理测试人脸图片"""
        from django.conf import settings
        face_dir = settings.FACE_IMAGES_DIR
        for user_id in user_ids:
            face_file = face_dir / f"{user_id}.jpg"
            if face_file.exists():
                face_file.unlink()
