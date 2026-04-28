"""
聊天应用数据模型
===============

本模块定义聊天功能相关的数据库模型，包括会话管理和消息存储。

模型列表：
- ChatSession: 聊天会话模型，管理用户的对话会话
- ChatMessage: 聊天消息模型，存储会话中的每条消息

数据关系：
- 一个ChatSession可以包含多个ChatMessage（一对多）
- 删除会话时会级联删除所有相关消息

使用示例：
    from apps.chat.models import ChatSession, ChatMessage
    
    # 创建会话
    session = ChatSession.objects.create(user_id=1, title="技术咨询")
    
    # 添加消息
    message = ChatMessage.objects.create(
        session=session,
        role="user",
        content="请帮我分析Python后端岗位"
    )
"""

from django.db import models


class ChatSession(models.Model):
    """
    聊天会话模型
    
    管理用户的对话会话，每个会话包含多条消息。
    会话按最后消息时间倒序排列，方便用户快速访问最近的对话。
    
    Attributes:
        session_id: 会话唯一标识（主键，自增）
        user_id: 关联的用户ID（来自face应用的用户系统）
        title: 会话标题，默认为"新会话"
        last_message_time: 最后一条消息的时间，用于排序
        created_at: 会话创建时间
        updated_at: 会话更新时间
    
    Meta:
        db_table: 数据库表名为'chat_session'
        ordering: 按最后消息时间倒序排列
    """
    
    session_id = models.BigAutoField(primary_key=True, verbose_name='会话ID')
    user_id = models.IntegerField(verbose_name='用户ID')
    title = models.CharField(max_length=200, default='新会话', verbose_name='会话标题')
    last_message_time = models.DateTimeField(auto_now=True, verbose_name='最后消息时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'chat_session'
        verbose_name = '聊天会话'
        verbose_name_plural = verbose_name
        ordering = ['-last_message_time']

    def __str__(self):
        """
        返回会话的字符串表示
        
        Returns:
            str: 格式为"Session {id}: {title}"
        """
        return f"Session {self.session_id}: {self.title}"


class ChatMessage(models.Model):
    """
    聊天消息模型
    
    存储会话中的每条消息，包括用户消息和AI回复。
    支持存储AI的思考过程和ECharts可视化配置。
    
    Attributes:
        message_id: 消息唯一标识（主键，自增）
        session: 关联的会话（外键，级联删除）
        user_id: 用户ID（可为空，用于标识消息来源）
        role: 消息角色（user/assistant/system）
        content: 消息文本内容
        thinking_process: AI的思考过程（可选，深度思考模式时保存）
        echarts_config: ECharts图表配置（可选，JSON格式）
        created_at: 消息创建时间
    
    Meta:
        db_table: 数据库表名为'chat_message'
        ordering: 按创建时间正序排列
    
    Note:
        - role字段常见值：'user'（用户消息）、'assistant'（AI回复）
        - thinking_process仅在deep_thinking=True时保存
        - echarts_config用于前端渲染数据可视化图表
    """
    
    message_id = models.BigAutoField(primary_key=True, verbose_name='消息ID')
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', verbose_name='所属会话')
    user_id = models.IntegerField(verbose_name='用户ID', null=True, blank=True)
    role = models.CharField(max_length=20, verbose_name='角色')
    content = models.TextField(verbose_name='消息内容')
    thinking_process = models.TextField(null=True, blank=True, verbose_name='思考过程')
    echarts_config = models.JSONField(null=True, blank=True, verbose_name='ECharts配置')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'chat_message'
        verbose_name = '聊天消息'
        verbose_name_plural = verbose_name
        ordering = ['created_at']

    def __str__(self):
        """
        返回消息的字符串表示
        
        Returns:
            str: 格式为"{role}: {content前50字符}..."
        """
        return f"{self.role}: {self.content[:50]}..."
