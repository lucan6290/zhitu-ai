"""
会话管理模块API测试 - 测试会话的增删查等接口

测试范围：
1. 获取会话列表接口 (GET /api/v1/chat/sessions/)
2. 创建新会话接口 (POST /api/v1/chat/sessions/)
3. 获取会话历史消息接口 (GET /api/v1/chat/sessions/{session_id}/messages/)
4. 删除会话接口 (DELETE /api/v1/chat/sessions/{session_id}/)
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


class SessionListAPITestCase(TestCase):
    """
    会话列表接口测试 (GET /api/v1/chat/sessions/)
    
    接口说明：
    - 认证要求：需要登录
    - 响应字段：sessions数组，包含session_id, title, last_message_time
    - 排序规则：按last_message_time降序排列
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        self.cleanup_session_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="会话测试用户",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        if response['data']['code'] == 200:
            self.test_user_id = response['data']['data']['user_id']
            self.test_user_name = user_data['user_name']
            self.cleanup_user_ids.append(self.test_user_id)
            
            login_data = MockDataFactory.create_login_data(
                login_account=self.test_user_name,
                user_pwd="password123"
            )
            self.client.post_json('/api/v1/auth/login/password/', login_data)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_sessions(self.cleanup_session_ids)
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_get_session_list_empty(self):
        """
        测试：获取空会话列表
        
        验证点：
        1. 响应状态码为200
        2. sessions字段为空数组
        """
        response = self.client.get('/api/v1/chat/sessions/')
        
        AssertionHelper.assert_success_response(response)
        AssertionHelper.assert_response_has_fields(response, ['sessions'])
        
        assert response['data']['data']['sessions'] == []
    
    def test_get_session_list_with_sessions(self):
        """
        测试：获取包含会话的列表
        
        验证点：
        1. 响应状态码为200
        2. sessions数组包含会话信息
        3. 每个会话包含必需字段：session_id, title, last_message_time
        4. last_message_time格式为ISO 8601
        """
        session_data = MockDataFactory.create_session_data(title="测试会话1")
        create_response = self.client.post_json('/api/v1/chat/sessions/', session_data)
        
        if create_response['data']['code'] == 200:
            session_id = create_response['data']['data']['session_id']
            self.cleanup_session_ids.append(session_id)
        
        response = self.client.get('/api/v1/chat/sessions/')
        
        AssertionHelper.assert_success_response(response)
        AssertionHelper.assert_response_has_fields(response, ['sessions'])
        
        sessions = response['data']['data']['sessions']
        assert len(sessions) > 0
        
        for session in sessions:
            assert 'session_id' in session
            assert 'title' in session
            assert 'last_message_time' in session
            AssertionHelper.assert_datetime_format(session['last_message_time'])
    
    def test_get_session_list_without_login(self):
        """
        测试：未登录获取会话列表
        
        验证点：
        1. 响应错误码为401
        2. 错误消息为"未登录或登录已过期"
        """
        self.client.logout()
        
        response = self.client.get('/api/v1/chat/sessions/')
        
        AssertionHelper.assert_error_response(response, 401, "未登录或登录已过期")
    
    def test_get_session_list_ordering(self):
        """
        测试：会话列表按last_message_time降序排列
        
        验证点：
        1. 创建多个会话
        2. 列表按时间降序排列
        """
        import time
        
        session_data1 = MockDataFactory.create_session_data(title="会话1")
        response1 = self.client.post_json('/api/v1/chat/sessions/', session_data1)
        if response1['data']['code'] == 200:
            self.cleanup_session_ids.append(response1['data']['data']['session_id'])
        
        time.sleep(0.1)
        
        session_data2 = MockDataFactory.create_session_data(title="会话2")
        response2 = self.client.post_json('/api/v1/chat/sessions/', session_data2)
        if response2['data']['code'] == 200:
            self.cleanup_session_ids.append(response2['data']['data']['session_id'])
        
        response = self.client.get('/api/v1/chat/sessions/')
        
        AssertionHelper.assert_success_response(response)
        
        sessions = response['data']['data']['sessions']
        if len(sessions) >= 2:
            assert sessions[0]['session_id'] == response2['data']['data']['session_id']
            assert sessions[1]['session_id'] == response1['data']['data']['session_id']
    
    def test_get_session_list_performance(self):
        """
        测试：获取会话列表性能
        
        验证点：
        1. 响应时间小于1秒
        """
        timer = PerformanceTimer()
        
        timer.start()
        response = self.client.get('/api/v1/chat/sessions/')
        timer.stop()
        
        timer.assert_faster_than(1.0)


class CreateSessionAPITestCase(TestCase):
    """
    创建会话接口测试 (POST /api/v1/chat/sessions/)
    
    接口说明：
    - 认证要求：需要登录
    - 请求参数：title（可选，默认"新会话"）
    - 响应字段：session_id, title
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        self.cleanup_session_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="创建会话测试用户",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        if response['data']['code'] == 200:
            self.test_user_id = response['data']['data']['user_id']
            self.test_user_name = user_data['user_name']
            self.cleanup_user_ids.append(self.test_user_id)
            
            login_data = MockDataFactory.create_login_data(
                login_account=self.test_user_name,
                user_pwd="password123"
            )
            self.client.post_json('/api/v1/auth/login/password/', login_data)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_sessions(self.cleanup_session_ids)
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_create_session_with_title(self):
        """
        测试：创建带标题的会话
        
        验证点：
        1. 响应状态码为200
        2. 返回session_id和title
        3. title与请求参数一致
        4. session_id为整数类型
        """
        title = "测试会话标题"
        session_data = MockDataFactory.create_session_data(title=title)
        
        response = self.client.post_json('/api/v1/chat/sessions/', session_data)
        
        AssertionHelper.assert_success_response(response)
        AssertionHelper.assert_response_has_fields(response, ['session_id', 'title'])
        
        assert response['data']['data']['title'] == title
        assert isinstance(response['data']['data']['session_id'], int)
        
        self.cleanup_session_ids.append(response['data']['data']['session_id'])
    
    def test_create_session_without_title(self):
        """
        测试：创建不带标题的会话
        
        验证点：
        1. 响应状态码为200
        2. title默认为"新会话"
        """
        response = self.client.post_json('/api/v1/chat/sessions/', {})
        
        AssertionHelper.assert_success_response(response)
        AssertionHelper.assert_response_has_fields(response, ['session_id', 'title'])
        
        assert response['data']['data']['title'] == "新会话"
        
        self.cleanup_session_ids.append(response['data']['data']['session_id'])
    
    def test_create_session_with_empty_title(self):
        """
        测试：创建标题为空字符串的会话
        
        验证点：
        1. 响应状态码为200
        2. title为空字符串或默认值
        """
        session_data = MockDataFactory.create_session_data(title="")
        
        response = self.client.post_json('/api/v1/chat/sessions/', session_data)
        
        AssertionHelper.assert_success_response(response)
        
        self.cleanup_session_ids.append(response['data']['data']['session_id'])
    
    def test_create_session_without_login(self):
        """
        测试：未登录创建会话
        
        验证点：
        1. 响应错误码为401
        2. 错误消息为"未登录或登录已过期"
        """
        self.client.logout()
        
        session_data = MockDataFactory.create_session_data(title="未登录会话")
        
        response = self.client.post_json('/api/v1/chat/sessions/', session_data)
        
        AssertionHelper.assert_error_response(response, 401, "未登录或登录已过期")
    
    def test_create_session_performance(self):
        """
        测试：创建会话性能
        
        验证点：
        1. 响应时间小于1秒
        """
        timer = PerformanceTimer()
        
        session_data = MockDataFactory.create_session_data(title="性能测试会话")
        
        timer.start()
        response = self.client.post_json('/api/v1/chat/sessions/', session_data)
        timer.stop()
        
        timer.assert_faster_than(1.0)
        
        if response['data']['code'] == 200:
            self.cleanup_session_ids.append(response['data']['data']['session_id'])


class SessionMessagesAPITestCase(TestCase):
    """
    会话历史消息接口测试 (GET /api/v1/chat/sessions/{session_id}/messages/)
    
    接口说明：
    - 认证要求：需要登录
    - 路径参数：session_id
    - 响应字段：messages数组，包含message_id, role, content, thinking_process, echarts_config, created_at
    - 排序规则：按created_at升序排列
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        self.cleanup_session_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="消息测试用户",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        if response['data']['code'] == 200:
            self.test_user_id = response['data']['data']['user_id']
            self.test_user_name = user_data['user_name']
            self.cleanup_user_ids.append(self.test_user_id)
            
            login_data = MockDataFactory.create_login_data(
                login_account=self.test_user_name,
                user_pwd="password123"
            )
            self.client.post_json('/api/v1/auth/login/password/', login_data)
            
            session_data = MockDataFactory.create_session_data(title="消息测试会话")
            session_response = self.client.post_json('/api/v1/chat/sessions/', session_data)
            if session_response['data']['code'] == 200:
                self.test_session_id = session_response['data']['data']['session_id']
                self.cleanup_session_ids.append(self.test_session_id)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_sessions(self.cleanup_session_ids)
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_get_messages_empty(self):
        """
        测试：获取空消息列表
        
        验证点：
        1. 响应状态码为200
        2. messages字段为空数组
        """
        response = self.client.get(f'/api/v1/chat/sessions/{self.test_session_id}/messages/')
        
        AssertionHelper.assert_success_response(response)
        AssertionHelper.assert_response_has_fields(response, ['messages'])
        
        assert response['data']['data']['messages'] == []
    
    def test_get_messages_without_login(self):
        """
        测试：未登录获取消息
        
        验证点：
        1. 响应错误码为401
        2. 错误消息为"未登录或登录已过期"
        """
        self.client.logout()
        
        response = self.client.get(f'/api/v1/chat/sessions/{self.test_session_id}/messages/')
        
        AssertionHelper.assert_error_response(response, 401, "未登录或登录已过期")
    
    def test_get_messages_nonexistent_session(self):
        """
        测试：获取不存在会话的消息
        
        验证点：
        1. 响应错误码为2001
        2. 错误消息为"会话不存在"
        """
        response = self.client.get('/api/v1/chat/sessions/99999/messages/')
        
        AssertionHelper.assert_error_response(response, 2001, "会话不存在")
    
    def test_get_messages_unauthorized_session(self):
        """
        测试：访问其他用户的会话消息
        
        验证点：
        1. 响应错误码为2002
        2. 错误消息为"无权访问该会话"
        """
        user_data2 = MockDataFactory.create_user_data(
            user_name="消息测试用户2",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data2)
        if response['data']['code'] == 200:
            user2_id = response['data']['data']['user_id']
            self.cleanup_user_ids.append(user2_id)
            
            login_data = MockDataFactory.create_login_data(
                login_account=user_data2['user_name'],
                user_pwd="password123"
            )
            self.client.post_json('/api/v1/auth/login/password/', login_data)
            
            response = self.client.get(f'/api/v1/chat/sessions/{self.test_session_id}/messages/')
            
            AssertionHelper.assert_error_response(response, 2002, "无权访问该会话")
    
    def test_get_messages_performance(self):
        """
        测试：获取消息性能
        
        验证点：
        1. 响应时间小于1秒
        """
        timer = PerformanceTimer()
        
        timer.start()
        response = self.client.get(f'/api/v1/chat/sessions/{self.test_session_id}/messages/')
        timer.stop()
        
        timer.assert_faster_than(1.0)


class DeleteSessionAPITestCase(TestCase):
    """
    删除会话接口测试 (DELETE /api/v1/chat/sessions/{session_id}/)
    
    接口说明：
    - 认证要求：需要登录
    - 路径参数：session_id
    - 只能删除自己创建的会话
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        self.cleanup_session_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="删除会话测试用户",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        if response['data']['code'] == 200:
            self.test_user_id = response['data']['data']['user_id']
            self.test_user_name = user_data['user_name']
            self.cleanup_user_ids.append(self.test_user_id)
            
            login_data = MockDataFactory.create_login_data(
                login_account=self.test_user_name,
                user_pwd="password123"
            )
            self.client.post_json('/api/v1/auth/login/password/', login_data)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_sessions(self.cleanup_session_ids)
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_delete_session_success(self):
        """
        测试：删除会话成功
        
        验证点：
        1. 响应状态码为200
        2. data字段为null
        3. 删除后无法再获取该会话
        """
        session_data = MockDataFactory.create_session_data(title="待删除会话")
        create_response = self.client.post_json('/api/v1/chat/sessions/', session_data)
        
        if create_response['data']['code'] == 200:
            session_id = create_response['data']['data']['session_id']
            
            response = self.client.delete(f'/api/v1/chat/sessions/{session_id}/')
            
            AssertionHelper.assert_success_response(response)
            assert response['data']['data'] is None
            
            list_response = self.client.get('/api/v1/chat/sessions/')
            sessions = list_response['data']['data']['sessions']
            session_ids = [s['session_id'] for s in sessions]
            assert session_id not in session_ids
    
    def test_delete_session_without_login(self):
        """
        测试：未登录删除会话
        
        验证点：
        1. 响应错误码为401
        2. 错误消息为"未登录或登录已过期"
        """
        session_data = MockDataFactory.create_session_data(title="未登录删除测试")
        create_response = self.client.post_json('/api/v1/chat/sessions/', session_data)
        
        if create_response['data']['code'] == 200:
            session_id = create_response['data']['data']['session_id']
            self.cleanup_session_ids.append(session_id)
            
            self.client.logout()
            
            response = self.client.delete(f'/api/v1/chat/sessions/{session_id}/')
            
            AssertionHelper.assert_error_response(response, 401, "未登录或登录已过期")
    
    def test_delete_nonexistent_session(self):
        """
        测试：删除不存在的会话
        
        验证点：
        1. 响应错误码为2001
        2. 错误消息为"会话不存在"
        """
        response = self.client.delete('/api/v1/chat/sessions/99999/')
        
        AssertionHelper.assert_error_response(response, 2001, "会话不存在")
    
    def test_delete_unauthorized_session(self):
        """
        测试：删除其他用户的会话
        
        验证点：
        1. 响应错误码为2002
        2. 错误消息为"无权访问该会话"
        """
        session_data = MockDataFactory.create_session_data(title="用户1的会话")
        create_response = self.client.post_json('/api/v1/chat/sessions/', session_data)
        
        if create_response['data']['code'] == 200:
            session_id = create_response['data']['data']['session_id']
            self.cleanup_session_ids.append(session_id)
            
            user_data2 = MockDataFactory.create_user_data(
                user_name="删除会话测试用户2",
                user_pwd="password123"
            )
            
            response = self.client.post_json('/api/v1/auth/register/', user_data2)
            if response['data']['code'] == 200:
                user2_id = response['data']['data']['user_id']
                self.cleanup_user_ids.append(user2_id)
                
                login_data = MockDataFactory.create_login_data(
                    login_account=user_data2['user_name'],
                    user_pwd="password123"
                )
                self.client.post_json('/api/v1/auth/login/password/', login_data)
                
                response = self.client.delete(f'/api/v1/chat/sessions/{session_id}/')
                
                AssertionHelper.assert_error_response(response, 2002, "无权访问该会话")
    
    def test_delete_session_performance(self):
        """
        测试：删除会话性能
        
        验证点：
        1. 响应时间小于1秒
        """
        session_data = MockDataFactory.create_session_data(title="性能测试删除会话")
        create_response = self.client.post_json('/api/v1/chat/sessions/', session_data)
        
        if create_response['data']['code'] == 200:
            session_id = create_response['data']['data']['session_id']
            
            timer = PerformanceTimer()
            
            timer.start()
            response = self.client.delete(f'/api/v1/chat/sessions/{session_id}/')
            timer.stop()
            
            timer.assert_faster_than(1.0)


class SessionManagementIntegrationTestCase(TestCase):
    """
    会话管理模块集成测试 - 测试完整的会话管理流程
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        self.cleanup_session_ids = []
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_sessions(self.cleanup_session_ids)
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_complete_session_flow(self):
        """
        测试：完整的会话管理流程
        
        流程：
        1. 用户注册并登录
        2. 创建会话
        3. 获取会话列表
        4. 获取会话消息
        5. 删除会话
        6. 验证会话已删除
        """
        user_data = MockDataFactory.create_user_data(
            user_name="会话集成测试用户",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        AssertionHelper.assert_success_response(response)
        user_id = response['data']['data']['user_id']
        self.cleanup_user_ids.append(user_id)
        
        login_data = MockDataFactory.create_login_data(
            login_account=user_data['user_name'],
            user_pwd="password123"
        )
        response = self.client.post_json('/api/v1/auth/login/password/', login_data)
        AssertionHelper.assert_success_response(response)
        
        session_data = MockDataFactory.create_session_data(title="集成测试会话")
        response = self.client.post_json('/api/v1/chat/sessions/', session_data)
        AssertionHelper.assert_success_response(response)
        session_id = response['data']['data']['session_id']
        
        response = self.client.get('/api/v1/chat/sessions/')
        AssertionHelper.assert_success_response(response)
        sessions = response['data']['data']['sessions']
        assert len(sessions) > 0
        
        response = self.client.get(f'/api/v1/chat/sessions/{session_id}/messages/')
        AssertionHelper.assert_success_response(response)
        
        response = self.client.delete(f'/api/v1/chat/sessions/{session_id}/')
        AssertionHelper.assert_success_response(response)
        
        response = self.client.get('/api/v1/chat/sessions/')
        sessions = response['data']['data']['sessions']
        session_ids = [s['session_id'] for s in sessions]
        assert session_id not in session_ids
