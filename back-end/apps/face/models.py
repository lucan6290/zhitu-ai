"""
人脸识别应用数据模型
==================

本模块定义用户信息相关的数据库模型，用于存储用户基本信息。

模型列表：
- UserInfo: 用户信息模型，存储用户账号、密码、手机号等

使用示例：
    from apps.face.models import UserInfo
    
    # 创建用户
    user = UserInfo.objects.create(
        user_name="张三",
        user_pwd="password123",
        user_age=25,
        user_phone="13800138000"
    )
    
    # 查询用户
    user = UserInfo.objects.get(user_name="张三")

Note:
    - 密码存储为明文，生产环境建议使用加密存储
    - 人脸图像存储在文件系统中，不在此模型中
"""

from django.db import models


class UserInfo(models.Model):
    """
    用户信息模型
    
    存储用户的基本信息，包括账号、密码、年龄、手机号等。
    用户ID与人脸图像文件名对应，用于人脸识别登录。
    
    Attributes:
        user_id: 用户唯一标识（主键，自增）
            - 与人脸图像文件名对应（如：1.jpg）
        user_name: 用户名（唯一，用于账号登录）
        user_age: 用户年龄
        user_phone: 手机号码（索引，用于手机号登录）
        user_pwd: 用户密码
        created_at: 账号创建时间
        updated_at: 信息更新时间
    
    Meta:
        db_table: 数据库表名为'user_info'
    
    Security Warning:
        密码以明文形式存储，生产环境应使用加密算法（如bcrypt）
    """
    
    user_id = models.AutoField(primary_key=True, verbose_name='用户ID')
    user_name = models.CharField(max_length=100, unique=True, verbose_name='用户名')
    user_age = models.IntegerField(default=0, verbose_name='用户年龄')
    user_phone = models.CharField(max_length=20, default='', db_index=True, verbose_name='手机号码')
    user_pwd = models.CharField(max_length=100, verbose_name='用户密码')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'user_info'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        """
        返回用户的字符串表示
        
        Returns:
            str: 格式为"用户名(手机号)"，无手机号显示N/A
        """
        return f"{self.user_name}({self.user_phone or 'N/A'})"
