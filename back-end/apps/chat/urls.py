"""
聊天应用URL配置
===============

定义聊天功能相关的URL路由映射。

URL模式：
- sessions/: 会话列表和创建
- sessions/<id>/messages/: 获取会话消息
- sessions/<id>/: 删除会话
- agent/: AI Agent对话接口

使用示例：
    # 在主urls.py中包含
    path('chat/', include('apps.chat.urls')),
    
    # 访问会话列表
    GET /chat/sessions/
    
    # 发送消息
    GET /chat/agent/?session_id=1&content=你好
"""

from django.urls import path
from .views import SessionListView, SessionMessagesView, SessionDeleteView, ChatAgentView

app_name = 'chat'

urlpatterns = [
    path('sessions/', SessionListView.as_view(), name='session_list'),
    path('sessions/<int:session_id>/messages/', SessionMessagesView.as_view(), name='session_messages'),
    path('sessions/<int:session_id>/', SessionDeleteView.as_view(), name='session_delete'),
    path('agent/', ChatAgentView.as_view(), name='agent'),
]
