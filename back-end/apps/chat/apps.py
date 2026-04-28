"""
聊天应用配置模块
===============

定义聊天应用的Django配置类。

配置信息：
- name: 应用路径 'apps.chat'
- verbose_name: 应用显示名称 '智能对话管理'
"""

from django.apps import AppConfig


class ChatConfig(AppConfig):
    """
    聊天应用配置类
    
    继承自Django的AppConfig，提供应用的基本配置信息。
    
    Attributes:
        default_auto_field: 主键字段类型，使用BigAutoField
        name: 应用的完整Python路径
        verbose_name: 在Django Admin中显示的名称
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.chat'
    verbose_name = '智能对话管理'
