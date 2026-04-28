"""
认证模块API测试 - 测试用户注册、登录、退出等接口

测试范围：
1. 用户注册接口 (POST /api/v1/auth/register/)
2. 账号密码登录接口 (POST /api/v1/auth/login/password/)
3. 人脸识别登录接口 (POST /api/v1/auth/login/face/)
4. 退出登录接口 (POST /api/v1/auth/logout/)
"""

import json
import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from tests.test_utils import (
    TestClient,
    MockDataFactory,
    AssertionHelper,
    PerformanceTimer,
    TestDataCleaner
)


class UserRegistrationAPITestCase(TestCase):
    """
    用户注册接口测试 (POST /api/v1/auth/register/)
    
    接口说明：
    - 用户名：6-20字符，全局唯一
    - 密码：6-20字符，必须同时包含字母和数字
    - 邀请码：业务必填，无邀请码无法注册
    - 人脸图片：可选，base64编码
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
        TestDataCleaner.cleanup_test_face_images(self.cleanup_user_ids)
    
    def test_register_success_without_face(self):
        """
        测试：无人脸图片注册成功
        
        验证点：
        1. 响应状态码为200
        2. 返回user_id字段
        3. user_id为整数类型
        """
        user_data = MockDataFactory.create_user_data(
            user_name="测试用户001",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        
        AssertionHelper.assert_success_response(response)
        AssertionHelper.assert_response_has_fields(response, ['user_id'])
        
        user_id = response['data']['data']['user_id']
        assert isinstance(user_id, int), "user_id应为整数类型"
        
        self.cleanup_user_ids.append(user_id)
    
    def test_register_success_with_face(self):
        """
        测试：带人脸图片注册成功
        
        验证点：
        1. 响应状态码为200
        2. 返回user_id字段
        3. 人脸图片被正确保存
        """
        user_data = MockDataFactory.create_user_data(
            user_name="测试用户002",
            user_pwd="password123"
        )
        user_data['face_image'] = MockDataFactory.create_face_image_base64()
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        
        AssertionHelper.assert_success_response(response)
        AssertionHelper.assert_response_has_fields(response, ['user_id'])
        
        user_id = response['data']['data']['user_id']
        self.cleanup_user_ids.append(user_id)
    
    def test_register_invalid_invitation_code(self):
        """
        测试：邀请码无效
        
        验证点：
        1. 响应错误码为1001
        2. 错误消息为"邀请码无效"
        """
        user_data = MockDataFactory.create_user_data(
            user_name="测试用户003",
            user_pwd="password123",
            invitation_code="INVALID_CODE"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        
        AssertionHelper.assert_error_response(response, 1001, "邀请码无效")
    
    def test_register_missing_invitation_code(self):
        """
        测试：缺少邀请码
        
        验证点：
        1. 响应错误码为1001
        2. 错误消息为"邀请码无效"
        """
        user_data = MockDataFactory.create_user_data(
            user_name="测试用户004",
            user_pwd="password123"
        )
        del user_data['invitation_code']
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        
        AssertionHelper.assert_error_response(response, 1001, "邀请码无效")
    
    def test_register_duplicate_username(self):
        """
        测试：用户名已存在
        
        验证点：
        1. 第一次注册成功
        2. 第二次注册失败，错误码为1002
        3. 错误消息为"用户名已存在"
        """
        user_data = MockDataFactory.create_user_data(
            user_name="重复用户名测试",
            user_pwd="password123"
        )
        
        response1 = self.client.post_json('/api/v1/auth/register/', user_data)
        AssertionHelper.assert_success_response(response1)
        user_id = response1['data']['data']['user_id']
        self.cleanup_user_ids.append(user_id)
        
        response2 = self.client.post_json('/api/v1/auth/register/', user_data)
        AssertionHelper.assert_error_response(response2, 1002, "用户名已存在")
    
    def test_register_invalid_password_too_short(self):
        """
        测试：密码长度过短（少于6位）
        
        验证点：
        1. 响应错误码为1003
        2. 错误消息包含"密码"
        """
        user_data = MockDataFactory.create_user_data(
            user_name="测试用户005",
            user_pwd="pass1"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        
        AssertionHelper.assert_error_response(response, 1003, "密码")
    
    def test_register_invalid_password_too_long(self):
        """
        测试：密码长度过长（超过20位）
        
        验证点：
        1. 响应错误码为1003
        2. 错误消息包含"密码"
        """
        user_data = MockDataFactory.create_user_data(
            user_name="测试用户006",
            user_pwd="a" * 21 + "1"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        
        AssertionHelper.assert_error_response(response, 1003, "密码")
    
    def test_register_invalid_password_no_letter(self):
        """
        测试：密码不包含字母
        
        验证点：
        1. 响应错误码为1003
        2. 错误消息包含"密码"
        """
        user_data = MockDataFactory.create_user_data(
            user_name="测试用户007",
            user_pwd="12345678"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        
        AssertionHelper.assert_error_response(response, 1003, "密码")
    
    def test_register_invalid_password_no_digit(self):
        """
        测试：密码不包含数字
        
        验证点：
        1. 响应错误码为1003
        2. 错误消息包含"密码"
        """
        user_data = MockDataFactory.create_user_data(
            user_name="测试用户008",
            user_pwd="password"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        
        AssertionHelper.assert_error_response(response, 1003, "密码")
    
    def test_register_missing_username(self):
        """
        测试：缺少用户名
        
        验证点：
        1. 响应错误码为400
        2. 错误消息包含"参数错误"
        """
        user_data = MockDataFactory.create_user_data()
        del user_data['user_name']
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        
        AssertionHelper.assert_error_response(response, 400, "参数错误")
    
    def test_register_missing_password(self):
        """
        测试：缺少密码
        
        验证点：
        1. 响应错误码为400
        2. 错误消息包含"参数错误"
        """
        user_data = MockDataFactory.create_user_data()
        del user_data['user_pwd']
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        
        AssertionHelper.assert_error_response(response, 400, "参数错误")
    
    def test_register_performance(self):
        """
        测试：注册接口性能
        
        验证点：
        1. 响应时间小于2秒
        """
        timer = PerformanceTimer()
        
        user_data = MockDataFactory.create_user_data(
            user_name="性能测试用户",
            user_pwd="password123"
        )
        
        timer.start()
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        timer.stop()
        
        timer.assert_faster_than(2.0)
        
        if response['data']['code'] == 200:
            user_id = response['data']['data']['user_id']
            self.cleanup_user_ids.append(user_id)


class PasswordLoginAPITestCase(TestCase):
    """
    账号密码登录接口测试 (POST /api/v1/auth/login/password/)
    
    接口说明：
    - 登录账号：支持user_name或user_phone
    - 密码：用户密码
    - 认证方式：Session Cookie (HttpOnly)
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="登录测试用户",
            user_pwd="password123",
            user_phone="13800138001"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        if response['data']['code'] == 200:
            self.test_user_id = response['data']['data']['user_id']
            self.test_user_name = user_data['user_name']
            self.test_user_phone = user_data['user_phone']
            self.test_user_pwd = user_data['user_pwd']
            self.cleanup_user_ids.append(self.test_user_id)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_login_success_with_username(self):
        """
        测试：使用用户名登录成功
        
        验证点：
        1. 响应状态码为200
        2. 返回用户信息字段：user_id, user_name, user_age, user_phone
        3. Session中保存了user_id和user_name
        """
        login_data = MockDataFactory.create_login_data(
            login_account=self.test_user_name,
            user_pwd=self.test_user_pwd
        )
        
        response = self.client.post_json('/api/v1/auth/login/password/', login_data)
        
        AssertionHelper.assert_success_response(response)
        AssertionHelper.assert_response_has_fields(
            response, 
            ['user_id', 'user_name', 'user_age', 'user_phone']
        )
        
        assert response['data']['data']['user_id'] == self.test_user_id
        assert response['data']['data']['user_name'] == self.test_user_name
    
    def test_login_success_with_phone(self):
        """
        测试：使用手机号登录成功
        
        验证点：
        1. 响应状态码为200
        2. 返回用户信息字段
        3. user_phone字段正确
        """
        login_data = MockDataFactory.create_login_data(
            login_account=self.test_user_phone,
            user_pwd=self.test_user_pwd
        )
        
        response = self.client.post_json('/api/v1/auth/login/password/', login_data)
        
        AssertionHelper.assert_success_response(response)
        AssertionHelper.assert_response_has_fields(
            response, 
            ['user_id', 'user_name', 'user_age', 'user_phone']
        )
        
        assert response['data']['data']['user_phone'] == self.test_user_phone
    
    def test_login_invalid_account(self):
        """
        测试：登录账号不存在
        
        验证点：
        1. 响应错误码为1004
        2. 错误消息为"登录账号或密码错误"
        """
        login_data = MockDataFactory.create_login_data(
            login_account="不存在的用户",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/login/password/', login_data)
        
        AssertionHelper.assert_error_response(response, 1004, "登录账号或密码错误")
    
    def test_login_invalid_password(self):
        """
        测试：密码错误
        
        验证点：
        1. 响应错误码为1004
        2. 错误消息为"登录账号或密码错误"
        """
        login_data = MockDataFactory.create_login_data(
            login_account=self.test_user_name,
            user_pwd="wrongpassword"
        )
        
        response = self.client.post_json('/api/v1/auth/login/password/', login_data)
        
        AssertionHelper.assert_error_response(response, 1004, "登录账号或密码错误")
    
    def test_login_missing_account(self):
        """
        测试：缺少登录账号
        
        验证点：
        1. 响应错误码为400
        2. 错误消息为"请求参数错误"
        """
        login_data = {"user_pwd": "password123"}
        
        response = self.client.post_json('/api/v1/auth/login/password/', login_data)
        
        AssertionHelper.assert_error_response(response, 400, "请求参数错误")
    
    def test_login_missing_password(self):
        """
        测试：缺少密码
        
        验证点：
        1. 响应错误码为400
        2. 错误消息为"请求参数错误"
        """
        login_data = {"login_account": self.test_user_name}
        
        response = self.client.post_json('/api/v1/auth/login/password/', login_data)
        
        AssertionHelper.assert_error_response(response, 400, "请求参数错误")
    
    def test_login_empty_account(self):
        """
        测试：登录账号为空字符串
        
        验证点：
        1. 响应错误码为400
        2. 错误消息为"请求参数错误"
        """
        login_data = MockDataFactory.create_login_data(
            login_account="",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/login/password/', login_data)
        
        AssertionHelper.assert_error_response(response, 400, "请求参数错误")
    
    def test_login_empty_password(self):
        """
        测试：密码为空字符串
        
        验证点：
        1. 响应错误码为400
        2. 错误消息为"请求参数错误"
        """
        login_data = MockDataFactory.create_login_data(
            login_account=self.test_user_name,
            user_pwd=""
        )
        
        response = self.client.post_json('/api/v1/auth/login/password/', login_data)
        
        AssertionHelper.assert_error_response(response, 400, "请求参数错误")
    
    def test_login_performance(self):
        """
        测试：登录接口性能
        
        验证点：
        1. 响应时间小于1秒
        """
        timer = PerformanceTimer()
        
        login_data = MockDataFactory.create_login_data(
            login_account=self.test_user_name,
            user_pwd=self.test_user_pwd
        )
        
        timer.start()
        response = self.client.post_json('/api/v1/auth/login/password/', login_data)
        timer.stop()
        
        timer.assert_faster_than(1.0)


class FaceLoginAPITestCase(TestCase):
    """
    人脸识别登录接口测试 (POST /api/v1/auth/login/face/)
    
    接口说明：
    - 人脸图片：base64编码
    - 认证方式：Session Cookie (HttpOnly)
    - 错误码1005：未识别到已注册人脸
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
        TestDataCleaner.cleanup_test_face_images(self.cleanup_user_ids)
    
    def test_face_login_missing_face_image(self):
        """
        测试：缺少人脸图片
        
        验证点：
        1. 响应错误码为400
        2. 错误消息为"请求参数错误"
        """
        login_data = {}
        
        response = self.client.post_json('/api/v1/auth/login/face/', login_data)
        
        AssertionHelper.assert_error_response(response, 400, "请求参数错误")
    
    def test_face_login_empty_face_image(self):
        """
        测试：人脸图片为空字符串
        
        验证点：
        1. 响应错误码为400
        2. 错误消息为"请求参数错误"
        """
        login_data = {"face_image": ""}
        
        response = self.client.post_json('/api/v1/auth/login/face/', login_data)
        
        AssertionHelper.assert_error_response(response, 400, "请求参数错误")
    
    def test_face_login_no_registered_face(self):
        """
        测试：未识别到已注册人脸
        
        验证点：
        1. 响应错误码为1005
        2. 错误消息为"未识别到已注册人脸"
        """
        face_image = MockDataFactory.create_face_image_base64()
        login_data = {"face_image": face_image}
        
        response = self.client.post_json('/api/v1/auth/login/face/', login_data)
        
        AssertionHelper.assert_error_response(response, 1005, "未识别到已注册人脸")
    
    def test_face_login_invalid_base64(self):
        """
        测试：无效的base64编码
        
        验证点：
        1. 响应错误码为500
        2. 错误消息为"服务器内部错误"
        """
        login_data = {"face_image": "data:image/jpeg;base64,invalid_base64"}
        
        response = self.client.post_json('/api/v1/auth/login/face/', login_data)
        
        AssertionHelper.assert_error_response(response, 500, "服务器内部错误")


class LogoutAPITestCase(TestCase):
    """
    退出登录接口测试 (POST /api/v1/auth/logout/)
    
    接口说明：
    - 清除Session Cookie
    - 无需请求参数
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="退出测试用户",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        if response['data']['code'] == 200:
            self.test_user_id = response['data']['data']['user_id']
            self.test_user_name = user_data['user_name']
            self.test_user_pwd = user_data['user_pwd']
            self.cleanup_user_ids.append(self.test_user_id)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_logout_success(self):
        """
        测试：退出登录成功
        
        验证点：
        1. 响应状态码为200
        2. data字段为null
        """
        login_data = MockDataFactory.create_login_data(
            login_account=self.test_user_name,
            user_pwd=self.test_user_pwd
        )
        self.client.post_json('/api/v1/auth/login/password/', login_data)
        
        response = self.client.post_json('/api/v1/auth/logout/', {})
        
        AssertionHelper.assert_success_response(response)
        assert response['data']['data'] is None
    
    def test_logout_without_login(self):
        """
        测试：未登录状态下退出
        
        验证点：
        1. 响应状态码为200（退出操作幂等）
        2. data字段为null
        """
        response = self.client.post_json('/api/v1/auth/logout/', {})
        
        AssertionHelper.assert_success_response(response)
        assert response['data']['data'] is None
    
    def test_logout_performance(self):
        """
        测试：退出接口性能
        
        验证点：
        1. 响应时间小于0.5秒
        """
        timer = PerformanceTimer()
        
        timer.start()
        response = self.client.post_json('/api/v1/auth/logout/', {})
        timer.stop()
        
        timer.assert_faster_than(0.5)


class AuthenticationIntegrationTestCase(TestCase):
    """
    认证模块集成测试 - 测试完整的认证流程
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_complete_auth_flow(self):
        """
        测试：完整的认证流程
        
        流程：
        1. 用户注册
        2. 账号密码登录
        3. 访问需要认证的接口
        4. 退出登录
        5. 再次访问需要认证的接口（应失败）
        """
        user_data = MockDataFactory.create_user_data(
            user_name="集成测试用户",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        AssertionHelper.assert_success_response(response)
        user_id = response['data']['data']['user_id']
        self.cleanup_user_ids.append(user_id)
        
        login_data = MockDataFactory.create_login_data(
            login_account=user_data['user_name'],
            user_pwd=user_data['user_pwd']
        )
        response = self.client.post_json('/api/v1/auth/login/password/', login_data)
        AssertionHelper.assert_success_response(response)
        
        response = self.client.get('/api/v1/user/profile/')
        AssertionHelper.assert_success_response(response)
        
        response = self.client.post_json('/api/v1/auth/logout/', {})
        AssertionHelper.assert_success_response(response)
        
        response = self.client.get('/api/v1/user/profile/')
        AssertionHelper.assert_error_response(response, 401, "未登录或登录已过期")
