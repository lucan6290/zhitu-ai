"""
表单验证器 - 用户输入验证函数
"""

import re
from typing import Tuple, List


def check_password(pwd: str) -> Tuple[bool, str]:
    """验证密码：6-20位，包含数字和英文字母"""
    if len(pwd) < 6 or len(pwd) > 20:
        return False, "长度必须是6-20位"
    has_letter = bool(re.search(r'[a-zA-Z]', pwd))
    has_digit = bool(re.search(r'\d', pwd))
    if not (has_letter and has_digit):
        return False, "必须包含一个数字或者一个英文"
    return True, ""


def check_phone(phone: str) -> Tuple[bool, str]:
    """验证手机号：1开头，11位数字"""
    if not re.match(r'^1\d{10}$', phone):
        return False, "手机号码1开头,11位数字"
    return True, ""


def check_age(age: int) -> Tuple[bool, str]:
    """验证年龄：1-150岁"""
    if age < 1 or age > 150:
        return False, "年龄范围应该是1-150岁之间"
    return True, ""


def validate_form_data(data: dict) -> Tuple[bool, List[str]]:
    """验证表单数据，返回(是否有效, 错误列表)"""
    errors = []
    if 'pwd' in data:
        valid, msg = check_password(data['pwd'])
        if not valid:
            errors.append(f"密码格式错误: {msg}")
    if 'pwd2' in data and 'pwd' in data:
        if data['pwd'] != data['pwd2']:
            errors.append("两次密码不一致")
    if 'phone' in data:
        valid, msg = check_phone(data['phone'])
        if not valid:
            errors.append(f"手机号格式错误: {msg}")
    if 'age' in data:
        try:
            age_int = int(data['age'])
            valid, msg = check_age(age_int)
            if not valid:
                errors.append(f"年龄格式错误: {msg}")
        except ValueError:
            errors.append("年龄必须是数字")
    return len(errors) == 0, errors
