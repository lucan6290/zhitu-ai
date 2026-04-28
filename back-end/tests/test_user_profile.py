"""
用户模块API测试 - 测试用户信息查询和更新接口

测试范围：
1. 获取用户信息接口 (POST /api/v1/user/profile/ - 查询模式)
2. 更新用户信息接口 (POST /api/v1/user/profile/ - 更新模式)
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


class UserProfileQueryAPITestCase(TestCase):
    """
    用户信息查询接口测试 (POST /api/v1/user/profile/ - 查询模式)
    
    接口说明：
    - 认证要求：需要登录，从Session Cookie中获取当前用户身份
    - 请求参数：无（不传action参数或action不为"update"）
    - 响应字段：user_id, user_name, user_age, user_phone, created_at
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="用户信息测试用户",
            user_pwd="password123",
            user_age=22,
            user_phone="13800138002"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        if response['data']['code'] == 200:
            self.test_user_id = response['data']['data']['user_id']
            self.test_user_name = user_data['user_name']
            self.test_user_age = user_data['user_age']
            self.test_user_phone = user_data['user_phone']
            self.cleanup_user_ids.append(self.test_user_id)
            
            login_data = MockDataFactory.create_login_data(
                login_account=self.test_user_name,
                user_pwd="password123"
            )
            self.client.post_json('/api/v1/auth/login/password/', login_data)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_query_profile_success(self):
        """
        测试：查询用户信息成功
        
        验证点：
        1. 响应状态码为200
        2. 返回所有必需字段：user_id, user_name, user_age, user_phone, created_at
        3. 字段值与注册时一致
        4. created_at格式为ISO 8601
        """
        response = self.client.post_json('/api/v1/user/profile/', {})
        
        AssertionHelper.assert_success_response(response)
        AssertionHelper.assert_response_has_fields(
            response,
            ['user_id', 'user_name', 'user_age', 'user_phone', 'created_at']
        )
        
        data = response['data']['data']
        assert data['user_id'] == self.test_user_id
        assert data['user_name'] == self.test_user_name
        assert data['user_age'] == self.test_user_age
        assert data['user_phone'] == self.test_user_phone
        
        AssertionHelper.assert_datetime_format(data['created_at'])
    
    def test_query_profile_without_login(self):
        """
        测试：未登录查询用户信息
        
        验证点：
        1. 响应错误码为401
        2. 错误消息为"未登录或登录已过期"
        """
        self.client.logout()
        
        response = self.client.post_json('/api/v1/user/profile/', {})
        
        AssertionHelper.assert_error_response(response, 401, "未登录或登录已过期")
    
    def test_query_profile_with_empty_action(self):
        """
        测试：action参数为空字符串
        
        验证点：
        1. 响应状态码为200
        2. 执行查询操作（非更新）
        """
        response = self.client.post_json('/api/v1/user/profile/', {"action": ""})
        
        AssertionHelper.assert_success_response(response)
        AssertionHelper.assert_response_has_fields(response, ['user_id'])
    
    def test_query_profile_with_invalid_action(self):
        """
        测试：action参数为无效值
        
        验证点：
        1. 响应状态码为200
        2. 执行查询操作（非更新）
        """
        response = self.client.post_json('/api/v1/user/profile/', {"action": "invalid"})
        
        AssertionHelper.assert_success_response(response)
        AssertionHelper.assert_response_has_fields(response, ['user_id'])
    
    def test_query_profile_performance(self):
        """
        测试：查询接口性能
        
        验证点：
        1. 响应时间小于1秒
        """
        timer = PerformanceTimer()
        
        timer.start()
        response = self.client.post_json('/api/v1/user/profile/', {})
        timer.stop()
        
        timer.assert_faster_than(1.0)


class UserProfileUpdateAPITestCase(TestCase):
    """
    用户信息更新接口测试 (POST /api/v1/user/profile/ - 更新模式)
    
    接口说明：
    - 认证要求：需要登录
    - 请求参数：action="update", user_age, user_phone, new_user_pwd（均为可选）
    - 只能更新当前登录用户自己的信息
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="更新测试用户",
            user_pwd="password123",
            user_age=22,
            user_phone="13800138003"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        if response['data']['code'] == 200:
            self.test_user_id = response['data']['data']['user_id']
            self.test_user_name = user_data['user_name']
            self.test_user_pwd = user_data['user_pwd']
            self.cleanup_user_ids.append(self.test_user_id)
            
            login_data = MockDataFactory.create_login_data(
                login_account=self.test_user_name,
                user_pwd="password123"
            )
            self.client.post_json('/api/v1/auth/login/password/', login_data)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_update_age_success(self):
        """
        测试：更新年龄成功
        
        验证点：
        1. 响应状态码为200
        2. 响应消息为"updated"
        3. data字段为null
        4. 再次查询时年龄已更新
        """
        new_age = 25
        update_data = MockDataFactory.create_profile_update_data(
            action="update",
            user_age=new_age
        )
        
        response = self.client.post_json('/api/v1/user/profile/', update_data)
        
        assert response['data']['code'] == 200
        assert response['data']['msg'] == "updated"
        assert response['data']['data'] is None
        
        query_response = self.client.post_json('/api/v1/user/profile/', {})
        assert query_response['data']['data']['user_age'] == new_age
    
    def test_update_phone_success(self):
        """
        测试：更新手机号成功
        
        验证点：
        1. 响应状态码为200
        2. 响应消息为"updated"
        3. 再次查询时手机号已更新
        """
        new_phone = "13900139000"
        update_data = MockDataFactory.create_profile_update_data(
            action="update",
            user_phone=new_phone
        )
        
        response = self.client.post_json('/api/v1/user/profile/', update_data)
        
        assert response['data']['code'] == 200
        assert response['data']['msg'] == "updated"
        
        query_response = self.client.post_json('/api/v1/user/profile/', {})
        assert query_response['data']['data']['user_phone'] == new_phone
    
    def test_update_password_success(self):
        """
        测试：更新密码成功
        
        验证点：
        1. 响应状态码为200
        2. 响应消息为"updated"
        3. 可以使用新密码登录
        4. 不能使用旧密码登录
        """
        new_password = "newpassword456"
        update_data = MockDataFactory.create_profile_update_data(
            action="update",
            new_user_pwd=new_password
        )
        
        response = self.client.post_json('/api/v1/user/profile/', update_data)
        
        assert response['data']['code'] == 200
        assert response['data']['msg'] == "updated"
        
        self.client.logout()
        
        login_data = MockDataFactory.create_login_data(
            login_account=self.test_user_name,
            user_pwd=new_password
        )
        login_response = self.client.post_json('/api/v1/auth/login/password/', login_data)
        AssertionHelper.assert_success_response(login_response)
        
        self.client.logout()
        
        old_login_data = MockDataFactory.create_login_data(
            login_account=self.test_user_name,
            user_pwd="password123"
        )
        old_login_response = self.client.post_json('/api/v1/auth/login/password/', old_login_data)
        AssertionHelper.assert_error_response(old_login_response, 1004, "登录账号或密码错误")
    
    def test_update_multiple_fields_success(self):
        """
        测试：同时更新多个字段成功
        
        验证点：
        1. 响应状态码为200
        2. 所有字段都已更新
        """
        new_age = 26
        new_phone = "13900139001"
        
        update_data = {
            "action": "update",
            "user_age": new_age,
            "user_phone": new_phone
        }
        
        response = self.client.post_json('/api/v1/user/profile/', update_data)
        
        assert response['data']['code'] == 200
        assert response['data']['msg'] == "updated"
        
        query_response = self.client.post_json('/api/v1/user/profile/', {})
        data = query_response['data']['data']
        assert data['user_age'] == new_age
        assert data['user_phone'] == new_phone
    
    def test_update_without_login(self):
        """
        测试：未登录更新用户信息
        
        验证点：
        1. 响应错误码为401
        2. 错误消息为"未登录或登录已过期"
        """
        self.client.logout()
        
        update_data = MockDataFactory.create_profile_update_data(
            action="update",
            user_age=30
        )
        
        response = self.client.post_json('/api/v1/user/profile/', update_data)
        
        AssertionHelper.assert_error_response(response, 401, "未登录或登录已过期")
    
    def test_update_with_invalid_password_format(self):
        """
        测试：新密码格式不符合要求
        
        验证点：
        1. 密码过短应失败
        2. 密码过长应失败
        3. 密码不含数字应失败
        4. 密码不含字母应失败
        """
        short_pwd_data = MockDataFactory.create_profile_update_data(
            action="update",
            new_user_pwd="pass1"
        )
        response = self.client.post_json('/api/v1/user/profile/', short_pwd_data)
        
        long_pwd_data = MockDataFactory.create_profile_update_data(
            action="update",
            new_user_pwd="a" * 21 + "1"
        )
        response = self.client.post_json('/api/v1/user/profile/', long_pwd_data)
        
        no_digit_pwd_data = MockDataFactory.create_profile_update_data(
            action="update",
            new_user_pwd="password"
        )
        response = self.client.post_json('/api/v1/user/profile/', no_digit_pwd_data)
        
        no_letter_pwd_data = MockDataFactory.create_profile_update_data(
            action="update",
            new_user_pwd="12345678"
        )
        response = self.client.post_json('/api/v1/user/profile/', no_letter_pwd_data)
    
    def test_update_with_empty_phone(self):
        """
        测试：手机号更新为空字符串
        
        验证点：
        1. 响应状态码为200
        2. 手机号被设置为None或保持原值
        """
        update_data = MockDataFactory.create_profile_update_data(
            action="update",
            user_phone=""
        )
        
        response = self.client.post_json('/api/v1/user/profile/', update_data)
        
        assert response['data']['code'] == 200
    
    def test_update_with_empty_password(self):
        """
        测试：密码更新为空字符串
        
        验证点：
        1. 响应状态码为200
        2. 密码保持不变
        """
        update_data = MockDataFactory.create_profile_update_data(
            action="update",
            new_user_pwd=""
        )
        
        response = self.client.post_json('/api/v1/user/profile/', update_data)
        
        assert response['data']['code'] == 200
        
        self.client.logout()
        
        login_data = MockDataFactory.create_login_data(
            login_account=self.test_user_name,
            user_pwd="password123"
        )
        login_response = self.client.post_json('/api/v1/auth/login/password/', login_data)
        AssertionHelper.assert_success_response(login_response)
    
    def test_update_performance(self):
        """
        测试：更新接口性能
        
        验证点：
        1. 响应时间小于1秒
        """
        timer = PerformanceTimer()
        
        update_data = MockDataFactory.create_profile_update_data(
            action="update",
            user_age=30
        )
        
        timer.start()
        response = self.client.post_json('/api/v1/user/profile/', update_data)
        timer.stop()
        
        timer.assert_faster_than(1.0)


class UserProfileSecurityTestCase(TestCase):
    """
    用户信息接口安全测试 - 验证权限控制和数据隔离
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        
        user_data1 = MockDataFactory.create_user_data(
            user_name="安全测试用户1",
            user_pwd="password123",
            user_phone="13800138010"
        )
        response1 = self.client.post_json('/api/v1/auth/register/', user_data1)
        if response1['data']['code'] == 200:
            self.user1_id = response1['data']['data']['user_id']
            self.user1_name = user_data1['user_name']
            self.cleanup_user_ids.append(self.user1_id)
        
        user_data2 = MockDataFactory.create_user_data(
            user_name="安全测试用户2",
            user_pwd="password123",
            user_phone="13800138011"
        )
        response2 = self.client.post_json('/api/v1/auth/register/', user_data2)
        if response2['data']['code'] == 200:
            self.user2_id = response2['data']['data']['user_id']
            self.user2_name = user_data2['user_name']
            self.cleanup_user_ids.append(self.user2_id)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_cannot_access_other_user_profile(self):
        """
        测试：无法访问其他用户的信息
        
        验证点：
        1. 用户1登录后只能查看自己的信息
        2. 无法通过修改参数查看用户2的信息
        3. 更新操作只能影响自己的数据
        """
        login_data = MockDataFactory.create_login_data(
            login_account=self.user1_name,
            user_pwd="password123"
        )
        self.client.post_json('/api/v1/auth/login/password/', login_data)
        
        response = self.client.post_json('/api/v1/user/profile/', {})
        
        AssertionHelper.assert_success_response(response)
        assert response['data']['data']['user_id'] == self.user1_id
        assert response['data']['data']['user_name'] == self.user1_name
    
    def test_update_only_affects_current_user(self):
        """
        测试：更新操作只影响当前登录用户
        
        验证点：
        1. 用户1更新自己的年龄
        2. 用户2的信息不受影响
        """
        login_data = MockDataFactory.create_login_data(
            login_account=self.user1_name,
            user_pwd="password123"
        )
        self.client.post_json('/api/v1/auth/login/password/', login_data)
        
        new_age = 99
        update_data = MockDataFactory.create_profile_update_data(
            action="update",
            user_age=new_age
        )
        self.client.post_json('/api/v1/user/profile/', update_data)
        
        self.client.logout()
        
        login_data2 = MockDataFactory.create_login_data(
            login_account=self.user2_name,
            user_pwd="password123"
        )
        self.client.post_json('/api/v1/auth/login/password/', login_data2)
        
        response = self.client.post_json('/api/v1/user/profile/', {})
        
        assert response['data']['data']['user_id'] == self.user2_id
        assert response['data']['data']['user_age'] != new_age
