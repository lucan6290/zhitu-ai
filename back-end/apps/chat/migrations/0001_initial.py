import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("face", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChatSession",
            fields=[
                (
                    "session_id",
                    models.BigAutoField(
                        primary_key=True, serialize=False, verbose_name="会话ID"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="face.userinfo",
                        verbose_name="用户ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        default="新会话", max_length=200, verbose_name="会话标题"
                    ),
                ),
                (
                    "last_message_time",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="最后消息时间"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
            ],
            options={
                "verbose_name": "聊天会话",
                "verbose_name_plural": "聊天会话",
                "db_table": "chat_session",
            },
        ),
        migrations.AddIndex(
            model_name="chatsession",
            index=models.Index(fields=["user", "last_message_time"], name="idx_user_last_time"),
        ),
        migrations.CreateModel(
            name="ChatMessage",
            fields=[
                (
                    "message_id",
                    models.BigAutoField(
                        primary_key=True, serialize=False, verbose_name="消息ID"
                    ),
                ),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="chat.chatsession",
                        verbose_name="会话ID",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chat_messages",
                        to="face.userinfo",
                        verbose_name="用户ID",
                    ),
                ),
                ("role", models.CharField(max_length=20, verbose_name="角色")),
                ("content", models.TextField(verbose_name="消息内容")),
                (
                    "thinking_process",
                    models.TextField(blank=True, null=True, verbose_name="思考过程"),
                ),
                (
                    "echarts_config",
                    models.JSONField(blank=True, null=True, verbose_name="ECharts配置"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
            ],
            options={
                "verbose_name": "聊天消息",
                "verbose_name_plural": "聊天消息",
                "db_table": "chat_message",
            },
        ),
        migrations.AddIndex(
            model_name="chatmessage",
            index=models.Index(fields=["session", "created_at"], name="idx_session_created"),
        ),
        migrations.CreateModel(
            name="McpJobsCache",
            fields=[
                (
                    "cache_id",
                    models.BigAutoField(
                        primary_key=True, serialize=False, verbose_name="缓存ID"
                    ),
                ),
                (
                    "keyword",
                    models.CharField(max_length=100, verbose_name="岗位关键词"),
                ),
                ("city", models.CharField(max_length=50, verbose_name="城市")),
                ("jobs_data", models.JSONField(verbose_name="职位数据JSON")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                ("expire_at", models.DateTimeField(verbose_name="过期时间")),
            ],
            options={
                "verbose_name": "MCP职位数据缓存",
                "verbose_name_plural": "MCP职位数据缓存",
                "db_table": "mcp_jobs_cache",
            },
        ),
        migrations.AddConstraint(
            model_name="mcpjobscache",
            constraint=models.UniqueConstraint(
                fields=["keyword", "city"], name="uk_keyword_city"
            ),
        ),
        migrations.AddIndex(
            model_name="mcpjobscache",
            index=models.Index(fields=["expire_at"], name="idx_expire_at"),
        ),
    ]
