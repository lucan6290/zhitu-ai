from django.db import models


class ChatSession(models.Model):
    session_id = models.BigAutoField(primary_key=True, verbose_name='会话ID')
    user_id = models.IntegerField(verbose_name='用户ID')
    title = models.CharField(max_length=200, default='新会话', verbose_name='会话标题')
    last_message_time = models.DateTimeField(auto_now=True, verbose_name='最后消息时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'chat_session'
        verbose_name = '聊天会话'
        verbose_name_plural = verbose_name
        ordering = ['-last_message_time']

    def __str__(self):
        return f"Session {self.session_id}: {self.title}"


class ChatMessage(models.Model):
    message_id = models.BigAutoField(primary_key=True, verbose_name='消息ID')
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', verbose_name='所属会话')
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
        return f"{self.role}: {self.content[:50]}..."
