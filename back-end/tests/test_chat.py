"""
智能对话服务测试 - 测试聊天和Agent功能

测试范围：
1. ChatSession - 会话模型
2. ChatMessage - 消息模型
3. Agent流式对话
"""

import json
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from apps.chat.models import ChatSession, ChatMessage
from tests.test_utils import (
    TestClient,
    MockDataFactory,
    TestDataCleaner
)


class ChatSessionModelTestCase(TestCase):
    """
    会话模型测试
    
    测试说明：
    - 测试会话创建
    - 测试会话查询
    - 测试会话删除
    """
    
    def setUp(self):
        """测试前准备"""
        self.test_user_id = 10001
    
    def tearDown(self):
        """测试后清理"""
        ChatMessage.objects.filter(session__user_id=self.test_user_id).delete()
        ChatSession.objects.filter(user_id=self.test_user_id).delete()
    
    def test_create_session_success(self):
        """
        测试：创建会话成功
        
        验证点：
        1. 会话创建成功
        2. session_id自动生成
        3. 默认标题为"新会话"
        """
        session = ChatSession.objects.create(
            user_id=self.test_user_id,
            title="测试会话"
        )
        
        assert session.session_id is not None
        assert session.title == "测试会话"
        assert session.user_id == self.test_user_id
        assert session.created_at is not None
    
    def test_session_default_title(self):
        """
        测试：会话默认标题
        
        验证点：
        1. 不指定标题时，默认为"新会话"
        """
        session = ChatSession.objects.create(
            user_id=self.test_user_id
        )
        
        assert session.title == "新会话"
    
    def test_session_ordering(self):
        """
        测试：会话排序
        
        验证点：
        1. 会话按last_message_time降序排列
        """
        session1 = ChatSession.objects.create(
            user_id=self.test_user_id,
            title="会话1"
        )
        
        import time
        time.sleep(0.1)
        
        session2 = ChatSession.objects.create(
            user_id=self.test_user_id,
            title="会话2"
        )
        
        sessions = ChatSession.objects.filter(user_id=self.test_user_id)
        
        assert sessions.count() == 2
        assert sessions[0].session_id == session2.session_id
    
    def test_session_str_representation(self):
        """
        测试：会话字符串表示
        
        验证点：
        1. __str__方法返回正确的格式
        """
        session = ChatSession.objects.create(
            user_id=self.test_user_id,
            title="测试会话"
        )
        
        str_repr = str(session)
        assert f"Session {session.session_id}" in str_repr
        assert "测试会话" in str_repr


class ChatMessageModelTestCase(TestCase):
    """
    消息模型测试
    
    测试说明：
    - 测试消息创建
    - 测试消息查询
    - 测试消息级联删除
    """
    
    def setUp(self):
        """测试前准备"""
        self.test_user_id = 10002
        self.session = ChatSession.objects.create(
            user_id=self.test_user_id,
            title="消息测试会话"
        )
    
    def tearDown(self):
        """测试后清理"""
        ChatMessage.objects.filter(session=self.session).delete()
        ChatSession.objects.filter(user_id=self.test_user_id).delete()
    
    def test_create_user_message(self):
        """
        测试：创建用户消息
        
        验证点：
        1. 用户消息创建成功
        2. role为"user"
        3. content正确保存
        """
        message = ChatMessage.objects.create(
            session=self.session,
            role="user",
            content="这是一条用户消息"
        )
        
        assert message.message_id is not None
        assert message.role == "user"
        assert message.content == "这是一条用户消息"
        assert message.thinking_process is None
        assert message.echarts_config is None
    
    def test_create_assistant_message(self):
        """
        测试：创建AI助手消息
        
        验证点：
        1. AI消息创建成功
        2. role为"assistant"
        3. 可包含thinking_process和echarts_config
        """
        message = ChatMessage.objects.create(
            session=self.session,
            role="assistant",
            content="这是一条AI回复",
            thinking_process="AI的思考过程...",
            echarts_config=[{"title": {"text": "图表"}}]
        )
        
        assert message.role == "assistant"
        assert message.thinking_process == "AI的思考过程..."
        assert message.echarts_config is not None
    
    def test_message_ordering(self):
        """
        测试：消息排序
        
        验证点：
        1. 消息按created_at升序排列
        """
        msg1 = ChatMessage.objects.create(
            session=self.session,
            role="user",
            content="消息1"
        )
        
        import time
        time.sleep(0.1)
        
        msg2 = ChatMessage.objects.create(
            session=self.session,
            role="user",
            content="消息2"
        )
        
        messages = ChatMessage.objects.filter(session=self.session)
        
        assert messages.count() == 2
        assert messages[0].message_id == msg1.message_id
        assert messages[1].message_id == msg2.message_id
    
    def test_message_cascade_delete(self):
        """
        测试：消息级联删除
        
        验证点：
        1. 删除会话时，相关消息也被删除
        """
        ChatMessage.objects.create(
            session=self.session,
            role="user",
            content="测试消息"
        )
        
        assert ChatMessage.objects.filter(session=self.session).count() == 1
        
        self.session.delete()
        
        assert ChatMessage.objects.filter(session_id=self.session.session_id).count() == 0
    
    def test_message_str_representation(self):
        """
        测试：消息字符串表示
        
        验证点：
        1. __str__方法返回正确的格式
        """
        message = ChatMessage.objects.create(
            session=self.session,
            role="user",
            content="这是一条很长的测试消息内容，用于验证字符串表示"
        )
        
        str_repr = str(message)
        assert "user" in str_repr
        assert "这是一条很长的测试消息内容" in str_repr


class ChatServiceIntegrationTestCase(TestCase):
    """
    聊天服务集成测试 - 测试完整的聊天流程
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        self.cleanup_session_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="聊天集成测试用户",
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
    
    def test_complete_chat_flow(self):
        """
        测试：完整的聊天流程
        
        流程：
        1. 创建会话
        2. 发送消息
        3. 获取消息列表
        4. 验证消息内容
        """
        session_data = MockDataFactory.create_session_data(title="集成测试会话")
        response = self.client.post_json('/api/v1/chat/sessions/', session_data)
        
        assert response['data']['code'] == 200
        session_id = response['data']['data']['session_id']
        self.cleanup_session_ids.append(session_id)
        
        params = {
            "session_id": session_id,
            "content": "你好，这是一条测试消息"
        }
        
        chat_response = self.client.client.get('/api/v1/chat/agent/', params)
        assert chat_response.status_code == 200
        
        messages_response = self.client.get(f'/api/v1/chat/sessions/{session_id}/messages/')
        assert messages_response['data']['code'] == 200
        
        messages = messages_response['data']['data']['messages']
        assert len(messages) >= 1
        
        user_message = messages[0]
        assert user_message['role'] == 'user'
        assert user_message['content'] == "你好，这是一条测试消息"
    
    def test_multiple_sessions_management(self):
        """
        测试：多会话管理
        
        验证点：
        1. 可以创建多个会话
        2. 会话列表正确显示
        3. 可以在不同会话间切换
        """
        session_ids = []
        
        for i in range(3):
            session_data = MockDataFactory.create_session_data(title=f"会话{i+1}")
            response = self.client.post_json('/api/v1/chat/sessions/', session_data)
            
            if response['data']['code'] == 200:
                session_id = response['data']['data']['session_id']
                session_ids.append(session_id)
                self.cleanup_session_ids.append(session_id)
        
        list_response = self.client.get('/api/v1/chat/sessions/')
        assert list_response['data']['code'] == 200
        
        sessions = list_response['data']['data']['sessions']
        assert len(sessions) >= 3
        
        for session_id in session_ids:
            messages_response = self.client.get(f'/api/v1/chat/sessions/{session_id}/messages/')
            assert messages_response['data']['code'] == 200
    
    def test_session_isolation(self):
        """
        测试：会话隔离
        
        验证点：
        1. 不同会话的消息相互独立
        2. 删除一个会话不影响其他会话
        """
        session_data1 = MockDataFactory.create_session_data(title="会话1")
        response1 = self.client.post_json('/api/v1/chat/sessions/', session_data1)
        session_id1 = response1['data']['data']['session_id']
        self.cleanup_session_ids.append(session_id1)
        
        session_data2 = MockDataFactory.create_session_data(title="会话2")
        response2 = self.client.post_json('/api/v1/chat/sessions/', session_data2)
        session_id2 = response2['data']['data']['session_id']
        self.cleanup_session_ids.append(session_id2)
        
        params1 = {
            "session_id": session_id1,
            "content": "会话1的消息"
        }
        self.client.client.get('/api/v1/chat/agent/', params1)
        
        params2 = {
            "session_id": session_id2,
            "content": "会话2的消息"
        }
        self.client.client.get('/api/v1/chat/agent/', params2)
        
        messages1 = self.client.get(f'/api/v1/chat/sessions/{session_id1}/messages/')
        messages2 = self.client.get(f'/api/v1/chat/sessions/{session_id2}/messages/')
        
        assert messages1['data']['code'] == 200
        assert messages2['data']['code'] == 200
        
        msgs1 = messages1['data']['data']['messages']
        msgs2 = messages2['data']['data']['messages']
        
        assert len(msgs1) >= 1
        assert len(msgs2) >= 1
        
        assert msgs1[0]['content'] == "会话1的消息"
        assert msgs2[0]['content'] == "会话2的消息"
        
        self.client.delete(f'/api/v1/chat/sessions/{session_id1}/')
        
        messages2_after_delete = self.client.get(f'/api/v1/chat/sessions/{session_id2}/messages/')
        assert messages2_after_delete['data']['code'] == 200
        assert len(messages2_after_delete['data']['data']['messages']) >= 1
