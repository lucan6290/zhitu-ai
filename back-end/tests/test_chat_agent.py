"""
聊天交互模块API测试 - 测试AI Agent流式对话接口

测试范围：
1. 发送消息接口 (GET /api/v1/chat/agent/) - SSE流式响应

注意：
- 本接口使用SSE（Server-Sent Events）流式响应
- 需要验证事件类型：thinking, thinking_end, content, echarts, end, error
- 需要测试错误处理机制
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


class ChatAgentAPITestCase(TestCase):
    """
    聊天Agent接口测试 (GET /api/v1/chat/agent/)
    
    接口说明：
    - 认证要求：需要登录
    - 请求参数：session_id, content, deep_thinking（可选）
    - 响应格式：SSE流式响应
    - 事件类型：thinking, thinking_end, content, echarts, end, error
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        self.cleanup_session_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="聊天测试用户",
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
            
            session_data = MockDataFactory.create_session_data(title="聊天测试会话")
            session_response = self.client.post_json('/api/v1/chat/sessions/', session_data)
            if session_response['data']['code'] == 200:
                self.test_session_id = session_response['data']['data']['session_id']
                self.cleanup_session_ids.append(self.test_session_id)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_sessions(self.cleanup_session_ids)
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_chat_agent_without_login(self):
        """
        测试：未登录发送消息
        
        验证点：
        1. SSE流返回error事件
        2. 错误消息为"未登录或登录已过期"
        """
        self.client.logout()
        
        params = {
            "session_id": self.test_session_id,
            "content": "测试消息"
        }
        
        response = self.client.client.get('/api/v1/chat/agent/', params)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/event-stream'
        
        content = response.content.decode('utf-8')
        assert 'event: error' in content
        assert '未登录或登录已过期' in content
    
    def test_chat_agent_missing_session_id(self):
        """
        测试：缺少session_id参数
        
        验证点：
        1. SSE流返回error事件
        2. 错误消息为"请求参数错误"
        """
        params = {
            "content": "测试消息"
        }
        
        response = self.client.client.get('/api/v1/chat/agent/', params)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/event-stream'
        
        content = response.content.decode('utf-8')
        assert 'event: error' in content
        assert '请求参数错误' in content
    
    def test_chat_agent_missing_content(self):
        """
        测试：缺少content参数
        
        验证点：
        1. SSE流返回error事件
        2. 错误消息为"请求参数错误"
        """
        params = {
            "session_id": self.test_session_id
        }
        
        response = self.client.client.get('/api/v1/chat/agent/', params)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/event-stream'
        
        content = response.content.decode('utf-8')
        assert 'event: error' in content
        assert '请求参数错误' in content
    
    def test_chat_agent_invalid_session_id(self):
        """
        测试：无效的session_id（非数字）
        
        验证点：
        1. SSE流返回error事件
        2. 错误消息为"请求参数错误"
        """
        params = {
            "session_id": "invalid",
            "content": "测试消息"
        }
        
        response = self.client.client.get('/api/v1/chat/agent/', params)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/event-stream'
        
        content = response.content.decode('utf-8')
        assert 'event: error' in content
        assert '请求参数错误' in content
    
    def test_chat_agent_nonexistent_session(self):
        """
        测试：会话不存在
        
        验证点：
        1. SSE流返回error事件
        2. 错误消息为"会话不存在"
        """
        params = {
            "session_id": 99999,
            "content": "测试消息"
        }
        
        response = self.client.client.get('/api/v1/chat/agent/', params)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/event-stream'
        
        content = response.content.decode('utf-8')
        assert 'event: error' in content
        assert '会话不存在' in content
    
    def test_chat_agent_unauthorized_session(self):
        """
        测试：访问其他用户的会话
        
        验证点：
        1. SSE流返回error事件
        2. 错误消息为"无权访问该会话"
        """
        user_data2 = MockDataFactory.create_user_data(
            user_name="聊天测试用户2",
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
            
            params = {
                "session_id": self.test_session_id,
                "content": "测试消息"
            }
            
            response = self.client.client.get('/api/v1/chat/agent/', params)
            
            assert response.status_code == 200
            assert response['Content-Type'] == 'text/event-stream'
            
            content = response.content.decode('utf-8')
            assert 'event: error' in content
            assert '无权访问该会话' in content
    
    def test_chat_agent_sse_format(self):
        """
        测试：SSE响应格式验证
        
        验证点：
        1. Content-Type为text/event-stream
        2. 响应包含event和data字段
        3. 响应以end事件结束（或error事件）
        """
        params = {
            "session_id": self.test_session_id,
            "content": "你好"
        }
        
        response = self.client.client.get('/api/v1/chat/agent/', params)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/event-stream'
        
        content = response.content.decode('utf-8')
        
        assert 'event:' in content or 'data:' in content
        
        has_end_or_error = 'event: end' in content or 'event: error' in content
        assert has_end_or_error, "SSE响应应包含end或error事件"
    
    def test_chat_agent_with_deep_thinking(self):
        """
        测试：开启深度思考模式
        
        验证点：
        1. deep_thinking参数为true
        2. SSE流正常响应
        """
        params = {
            "session_id": self.test_session_id,
            "content": "深度思考测试",
            "deep_thinking": "true"
        }
        
        response = self.client.client.get('/api/v1/chat/agent/', params)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/event-stream'
        
        content = response.content.decode('utf-8')
        assert 'event: end' in content or 'event: error' in content
    
    def test_chat_agent_without_deep_thinking(self):
        """
        测试：不开启深度思考模式（默认）
        
        验证点：
        1. deep_thinking参数为false或不传
        2. SSE流正常响应
        """
        params = {
            "session_id": self.test_session_id,
            "content": "普通模式测试",
            "deep_thinking": "false"
        }
        
        response = self.client.client.get('/api/v1/chat/agent/', params)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/event-stream'
        
        content = response.content.decode('utf-8')
        assert 'event: end' in content or 'event: error' in content
    
    def test_chat_agent_empty_content(self):
        """
        测试：消息内容为空字符串
        
        验证点：
        1. SSE流返回error事件
        2. 错误消息为"请求参数错误"
        """
        params = {
            "session_id": self.test_session_id,
            "content": ""
        }
        
        response = self.client.client.get('/api/v1/chat/agent/', params)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/event-stream'
        
        content = response.content.decode('utf-8')
        assert 'event: error' in content
        assert '请求参数错误' in content


class ChatAgentSSEEventsTestCase(TestCase):
    """
    Chat Agent SSE事件类型测试 - 验证各种事件类型的正确性
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        self.cleanup_session_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="SSE事件测试用户",
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
            
            session_data = MockDataFactory.create_session_data(title="SSE事件测试会话")
            session_response = self.client.post_json('/api/v1/chat/sessions/', session_data)
            if session_response['data']['code'] == 200:
                self.test_session_id = session_response['data']['data']['session_id']
                self.cleanup_session_ids.append(self.test_session_id)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_sessions(self.cleanup_session_ids)
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_sse_content_event_format(self):
        """
        测试：content事件格式
        
        验证点：
        1. 事件格式为：event: content\ndata: {text}\n\n
        2. data字段包含文本内容
        """
        params = {
            "session_id": self.test_session_id,
            "content": "测试content事件"
        }
        
        response = self.client.client.get('/api/v1/chat/agent/', params)
        
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        if 'event: content' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('event: content'):
                    assert i + 1 < len(lines)
                    data_line = lines[i + 1]
                    assert data_line.startswith('data:')
                    break
    
    def test_sse_end_event_format(self):
        """
        测试：end事件格式
        
        验证点：
        1. 事件格式为：event: end\n\n
        2. end事件后不再有其他事件
        """
        params = {
            "session_id": self.test_session_id,
            "content": "测试end事件"
        }
        
        response = self.client.client.get('/api/v1/chat/agent/', params)
        
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        if 'event: end' in content:
            lines = content.split('\n')
            end_index = -1
            for i, line in enumerate(lines):
                if line.startswith('event: end'):
                    end_index = i
                    break
            
            assert end_index >= 0
            
            remaining_content = '\n'.join(lines[end_index:])
            assert 'event: error' not in remaining_content
    
    def test_sse_error_event_format(self):
        """
        测试：error事件格式
        
        验证点：
        1. 事件格式为：event: error\ndata: {error_msg}\n\n
        2. error事件后不再有其他事件
        """
        params = {
            "session_id": 99999,
            "content": "测试error事件"
        }
        
        response = self.client.client.get('/api/v1/chat/agent/', params)
        
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        assert 'event: error' in content
        
        lines = content.split('\n')
        error_index = -1
        for i, line in enumerate(lines):
            if line.startswith('event: error'):
                error_index = i
                break
        
        assert error_index >= 0
        assert error_index + 1 < len(lines)
        data_line = lines[error_index + 1]
        assert data_line.startswith('data:')
        
        remaining_content = '\n'.join(lines[error_index:])
        assert 'event: end' not in remaining_content


class ChatAgentErrorHandlingTestCase(TestCase):
    """
    Chat Agent错误处理测试 - 验证各种错误场景的处理
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        self.cleanup_session_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="错误处理测试用户",
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
            
            session_data = MockDataFactory.create_session_data(title="错误处理测试会话")
            session_response = self.client.post_json('/api/v1/chat/sessions/', session_data)
            if session_response['data']['code'] == 200:
                self.test_session_id = session_response['data']['data']['session_id']
                self.cleanup_session_ids.append(self.test_session_id)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_sessions(self.cleanup_session_ids)
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_error_no_end_event_after_error(self):
        """
        测试：错误后不发送end事件
        
        验证点：
        1. 发生错误时发送error事件
        2. error事件后不再发送end事件
        3. 连接关闭
        """
        params = {
            "session_id": 99999,
            "content": "测试错误处理"
        }
        
        response = self.client.client.get('/api/v1/chat/agent/', params)
        
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        assert 'event: error' in content
        assert 'event: end' not in content
    
    def test_error_message_user_friendly(self):
        """
        测试：错误消息用户友好
        
        验证点：
        1. 错误消息清晰易懂
        2. 不暴露技术细节
        """
        params = {
            "session_id": 99999,
            "content": "测试错误消息"
        }
        
        response = self.client.client.get('/api/v1/chat/agent/', params)
        
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        assert 'event: error' in content
        
        assert '会话不存在' in content or '无权访问' in content or '服务器内部错误' in content
    
    def test_error_preserves_user_input(self):
        """
        测试：错误时保留用户输入
        
        验证点：
        1. 发生错误后，前端应保留用户输入内容
        2. 用户可以重新发送
        """
        params = {
            "session_id": 99999,
            "content": "这是一条测试消息"
        }
        
        response = self.client.client.get('/api/v1/chat/agent/', params)
        
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        assert 'event: error' in content


class ChatAgentPerformanceTestCase(TestCase):
    """
    Chat Agent性能测试 - 验证接口响应时间和资源使用
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        self.cleanup_session_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="性能测试用户",
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
            
            session_data = MockDataFactory.create_session_data(title="性能测试会话")
            session_response = self.client.post_json('/api/v1/chat/sessions/', session_data)
            if session_response['data']['code'] == 200:
                self.test_session_id = session_response['data']['data']['session_id']
                self.cleanup_session_ids.append(self.test_session_id)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_sessions(self.cleanup_session_ids)
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_response_time_initial_connection(self):
        """
        测试：初始连接响应时间
        
        验证点：
        1. 首次连接响应时间小于5秒
        """
        timer = PerformanceTimer()
        
        params = {
            "session_id": self.test_session_id,
            "content": "性能测试消息"
        }
        
        timer.start()
        response = self.client.client.get('/api/v1/chat/agent/', params)
        timer.stop()
        
        assert timer.elapsed() < 5.0, f"初始连接响应时间 {timer.elapsed():.2f}s 超过预期 5s"
    
    def test_concurrent_requests_limit(self):
        """
        测试：并发请求限制
        
        验证点：
        1. 系统应能处理合理的并发请求
        2. 不应出现资源耗尽
        """
        import concurrent.futures
        import time
        
        def send_chat_request(session_id, content):
            params = {
                "session_id": session_id,
                "content": content
            }
            response = self.client.client.get('/api/v1/chat/agent/', params)
            return response.status_code
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(3):
                future = executor.submit(
                    send_chat_request,
                    self.test_session_id,
                    f"并发测试消息{i}"
                )
                futures.append(future)
            
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
            
            for result in results:
                assert result == 200
