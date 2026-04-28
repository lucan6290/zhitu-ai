"""
表单验证层 - 用户注册和登录表单验证
"""

import re
from django import forms
from .models import UserInfo


class UserRegisterForm(forms.ModelForm):
    """用户注册表单 - 验证用户注册信息"""

    class Meta:
        model = UserInfo
        fields = ['user_name', 'user_pwd']
        labels = {
            'user_name': '姓名',
            'user_pwd': '密码',
        }

    def clean_user_pwd(self):
        """验证密码：6-20位，包含数字和英文字母"""
        pwd = self.cleaned_data.get('user_pwd')
        if len(pwd) < 6 or len(pwd) > 20:
            raise forms.ValidationError('密码长度必须是6-20位')
        if not (re.search(r'[a-zA-Z]', pwd) and re.search(r'\d', pwd)):
            raise forms.ValidationError('密码必须包含至少一个数字和一个英文字母')
        return pwd


class UserLoginForm(forms.Form):
    """用户登录表单"""

    user = forms.CharField(max_length=100, label='账号')
    pwd = forms.CharField(max_length=100, label='密码')
