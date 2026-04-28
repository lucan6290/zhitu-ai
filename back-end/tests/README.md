# 职途AI - API测试文档

## 📋 测试概览

本文档提供了职途AI后端API的完整测试文档，包含所有API端点的详细测试用例和验证点。

## 📁 测试文件结构

```
back-end/tests/
├── __init__.py                 # 测试包初始化
├── test_utils.py               # 测试工具和辅助函数
├── test_auth.py                # 认证模块测试
├── test_user_profile.py        # 用户模块测试
├── test_session.py             # 会话管理测试
├── test_chat_agent.py          # 聊天Agent测试
├── test_mcp.py                 # MCP数据接口测试
├── test_face.py                # 人脸识别服务测试
└── test_chat.py                # 聊天服务测试
```

## 🎯 测试覆盖范围

### 1. 认证模块 (test_auth.py)

**测试接口：**
- `POST /api/v1/auth/register/` - 用户注册
- `POST /api/v1/auth/login/password/` - 账号密码登录
- `POST /api/v1/auth/login/face/` - 人脸识别登录
- `POST /api/v1/auth/logout/` - 退出登录

**测试场景：**
- ✅ 用户注册成功（带/不带头像）
- ✅ 邀请码验证
- ✅ 用户名重复检测
- ✅ 密码格式验证
- ✅ 账号密码登录成功
- ✅ 手机号登录成功
- ✅ 登录失败场景
- ✅ 人脸识别登录
- ✅ 退出登录
- ✅ 完整认证流程

### 2. 用户模块 (test_user_profile.py)

**测试接口：**
- `POST /api/v1/user/profile/` - 获取/更新用户信息

**测试场景：**
- ✅ 查询用户信息成功
- ✅ 更新年龄、手机号、密码
- ✅ 未登录访问控制
- ✅ 权限验证（只能访问自己的信息）
- ✅ 数据隔离验证

### 3. 会话管理模块 (test_session.py)

**测试接口：**
- `GET /api/v1/chat/sessions/` - 获取会话列表
- `POST /api/v1/chat/sessions/` - 创建新会话
- `GET /api/v1/chat/sessions/{session_id}/messages/` - 获取会话消息
- `DELETE /api/v1/chat/sessions/{session_id}/` - 删除会话

**测试场景：**
- ✅ 创建会话（带/不带标题）
- ✅ 获取会话列表
- ✅ 会话排序验证
- ✅ 获取会话消息
- ✅ 删除会话
- ✅ 权限控制
- ✅ 会话不存在处理
- ✅ 完整会话管理流程

### 4. 聊天Agent模块 (test_chat_agent.py)

**测试接口：**
- `GET /api/v1/chat/agent/` - 发送消息（SSE流式响应）

**测试场景：**
- ✅ SSE流式响应格式验证
- ✅ 事件类型验证（thinking, content, echarts, end, error）
- ✅ 参数验证（session_id, content）
- ✅ 权限验证
- ✅ 错误处理机制
- ✅ 性能测试

### 5. MCP数据模块 (test_mcp.py)

**测试接口：**
- `GET /api/v1/mcp/jobs/` - 获取职位数据
- `POST /api/v1/mcp/jobs/apply/` - 投递职位

**测试场景：**
- ✅ 获取职位数据成功
- ✅ 缓存机制验证
- ✅ 参数验证
- ✅ MCP服务不可用处理
- ✅ 投递职位
- ✅ 数据格式验证

### 6. 人脸识别服务 (test_face.py)

**测试服务：**
- FaceService - 人脸识别服务
- DatabaseService - 数据库服务
- ImageService - 图像处理服务

**测试场景：**
- ✅ 人脸特征提取
- ✅ 人脸比对
- ✅ 数据库CRUD操作
- ✅ 图像处理

### 7. 聊天服务 (test_chat.py)

**测试模型：**
- ChatSession - 会话模型
- ChatMessage - 消息模型

**测试场景：**
- ✅ 会话创建和管理
- ✅ 消息创建和查询
- ✅ 级联删除
- ✅ 完整聊天流程

## 🛠️ 测试工具

### TestClient - 测试客户端封装

```python
from tests.test_utils import TestClient

client = TestClient()

# 模拟登录
client.login_as_user(user_id=1, user_name="测试用户")

# 发送POST请求
response = client.post_json('/api/v1/auth/register/', data)

# 发送GET请求
response = client.get('/api/v1/chat/sessions/')

# 发送DELETE请求
response = client.delete('/api/v1/chat/sessions/1/')
```

### MockDataFactory - 模拟数据工厂

```python
from tests.test_utils import MockDataFactory

# 创建用户注册数据
user_data = MockDataFactory.create_user_data(
    user_name="测试用户",
    user_pwd="password123"
)

# 创建登录数据
login_data = MockDataFactory.create_login_data(
    login_account="测试用户",
    user_pwd="password123"
)

# 创建人脸图片Base64
face_image = MockDataFactory.create_face_image_base64()
```

### AssertionHelper - 断言辅助类

```python
from tests.test_utils import AssertionHelper

# 断言成功响应
AssertionHelper.assert_success_response(response)

# 断言错误响应
AssertionHelper.assert_error_response(response, 401, "未登录")

# 断言响应包含字段
AssertionHelper.assert_response_has_fields(response, ['user_id', 'user_name'])

# 断言时间格式
AssertionHelper.assert_datetime_format("2026-04-28T10:30:00")
```

### PerformanceTimer - 性能计时器

```python
from tests.test_utils import PerformanceTimer

timer = PerformanceTimer()
timer.start()

# 执行测试操作
response = client.get('/api/v1/chat/sessions/')

timer.stop()
timer.assert_faster_than(1.0)  # 断言响应时间小于1秒
```

## 🚀 运行测试

### 运行所有测试

```bash
cd back-end
python manage.py test
```

### 运行特定测试文件

```bash
# 运行认证模块测试
python manage.py test tests.test_auth

# 运行用户模块测试
python manage.py test tests.test_user_profile

# 运行会话管理测试
python manage.py test tests.test_session

# 运行聊天Agent测试
python manage.py test tests.test_chat_agent

# 运行MCP模块测试
python manage.py test tests.test_mcp
```

### 运行特定测试类

```bash
python manage.py test tests.test_auth.UserRegistrationAPITestCase
```

### 运行特定测试方法

```bash
python manage.py test tests.test_auth.UserRegistrationAPITestCase.test_register_success_without_face
```

### 生成测试覆盖率报告

```bash
# 安装coverage
pip install coverage

# 运行测试并生成覆盖率报告
coverage run --source='.' manage.py test
coverage report
coverage html  # 生成HTML报告
```

## 📊 测试数据管理

### 测试数据清理

所有测试用例都实现了 `setUp()` 和 `tearDown()` 方法，确保测试数据的自动清理：

```python
def setUp(self):
    """测试前准备"""
    self.client = TestClient()
    self.cleanup_user_ids = []
    self.cleanup_session_ids = []

def tearDown(self):
    """测试后清理"""
    TestDataCleaner.cleanup_test_sessions(self.cleanup_session_ids)
    TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
```

### TestDataCleaner - 测试数据清理器

```python
from tests.test_utils import TestDataCleaner

# 清理测试用户
TestDataCleaner.cleanup_test_users([1, 2, 3])

# 清理测试会话
TestDataCleaner.cleanup_test_sessions([1, 2, 3])

# 清理测试人脸图片
TestDataCleaner.cleanup_test_face_images([1, 2, 3])
```

## 📝 测试最佳实践

### 1. 测试命名规范

- 测试类命名：`{模块名}APITestCase` 或 `{功能名}TestCase`
- 测试方法命名：`test_{场景描述}`
- 使用中文注释说明测试目的和验证点

### 2. 测试结构

每个测试方法应包含：
- **测试说明**：描述测试目的
- **验证点**：列出需要验证的内容
- **测试步骤**：执行测试操作
- **断言验证**：验证测试结果

### 3. 数据隔离

- 每个测试用例使用独立的测试数据
- 测试完成后自动清理数据
- 避免测试用例之间的数据依赖

### 4. 错误处理

- 测试正常流程和异常流程
- 验证错误码和错误消息
- 测试边界条件

### 5. 性能测试

- 对关键接口进行性能测试
- 设置合理的响应时间阈值
- 使用 `PerformanceTimer` 工具

## 🔍 测试验证点

### 接口响应验证

- ✅ 响应状态码正确
- ✅ 响应数据格式正确
- ✅ 响应字段完整
- ✅ 字段类型正确
- ✅ 时间格式符合ISO 8601

### 业务逻辑验证

- ✅ 正常流程成功
- ✅ 异常流程正确处理
- ✅ 边界条件处理
- ✅ 权限控制有效
- ✅ 数据隔离正确

### 性能验证

- ✅ 响应时间符合要求
- ✅ 并发处理能力
- ✅ 资源使用合理

## 📈 测试覆盖率目标

- **语句覆盖率**：≥ 80%
- **分支覆盖率**：≥ 70%
- **函数覆盖率**：≥ 90%
- **类覆盖率**：100%

## 🐛 常见问题

### 1. 测试数据库配置

确保测试使用独立的数据库，避免污染开发数据：

```python
# settings/test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test_agent_face_pro',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 2. 测试环境变量

确保测试环境变量正确配置：

```bash
export DJANGO_SETTINGS_MODULE=config.settings.development
export INVITATION_CODE=INVITE2026
```

### 3. 测试依赖安装

确保所有测试依赖已安装：

```bash
pip install -r requirements/development.txt
```

## 📚 参考资料

- [Django测试文档](https://docs.djangoproject.com/en/4.2/topics/testing/)
- [接口设计文档](../docs/05-接口设计文档.md)
- [数据库设计文档](../docs/04-数据库设计文档.md)

## 🤝 贡献指南

添加新的测试用例时，请遵循以下步骤：

1. 在对应的测试文件中添加新的测试类或方法
2. 使用 `MockDataFactory` 创建测试数据
3. 使用 `AssertionHelper` 进行断言验证
4. 在 `tearDown` 中清理测试数据
5. 更新本文档的测试覆盖范围

## 📧 联系方式

如有问题或建议，请联系开发团队。

---

**最后更新时间**：2026-04-28  
**文档版本**：v1.0.0
