"""
自定义异常类 - 定义项目中的异常类型
"""


# 人脸识别相关异常
class FaceRecognitionError(Exception):
    """人脸识别基础异常"""
    pass


class NoFaceDetectedError(FaceRecognitionError):
    """未检测到人脸"""
    pass


class FaceAlreadyExistsError(FaceRecognitionError):
    """人脸已存在"""
    pass


# 数据库相关异常
class DatabaseError(Exception):
    """数据库基础异常"""
    pass


class UserNotFoundError(DatabaseError):
    """用户不存在"""
    pass


class UserAlreadyExistsError(DatabaseError):
    """用户已存在"""
    pass


# 验证相关异常
class ValidationError(Exception):
    """验证基础异常"""
    pass


class InvalidPhoneError(ValidationError):
    """无效手机号"""
    pass


class InvalidPasswordError(ValidationError):
    """无效密码"""
    pass


class InvalidAgeError(ValidationError):
    """无效年龄"""
    pass
