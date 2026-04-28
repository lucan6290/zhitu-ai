from django.db import models


class UserInfo(models.Model):
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
        return f"{self.user_name}({self.user_phone or 'N/A'})"
