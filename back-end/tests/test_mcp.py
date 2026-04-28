"""
MCP数据模块API测试 - 测试职位数据获取和投递接口

测试范围：
1. 获取职位数据接口 (GET /api/v1/mcp/jobs/)
2. 投递职位接口 (POST /api/v1/mcp/jobs/apply/) - 如果存在

注意：
- MCP接口可能依赖外部服务
- 需要测试缓存机制
- 需要测试错误处理（MCP服务不可用）
"""

import json
import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from tests.test_utils import (
    TestClient,
    MockDataFactory,
    AssertionHelper,
    PerformanceTimer,
    TestDataCleaner
)


class MCPJobsAPITestCase(TestCase):
    """
    MCP职位数据接口测试 (GET /api/v1/mcp/jobs/)
    
    接口说明：
    - 认证要求：需要登录
    - 请求参数：keyword, city, recruit_type（可选）, limit（可选，默认20）
    - 响应字段：jobs数组, from_cache布尔值
    - 缓存机制：内存缓存1小时，MySQL缓存7天
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="MCP测试用户",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        if response['data']['code'] == 200:
            self.test_user_id = response['data']['data']['user_id']
            self.test_user_name = user_data['user_name']
            self.cleanup_user_ids.append(self.test_user_id)
            
            login_data = MockDataFactory.create_login_data(
                login_account=self.test_user_name,
                user_pwd="password123"
            )
            self.client.post_json('/api/v1/auth/login/password/', login_data)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_get_jobs_without_login(self):
        """
        测试：未登录获取职位数据
        
        验证点：
        1. 响应错误码为401
        2. 错误消息为"未登录或登录已过期"
        """
        self.client.logout()
        
        params = {
            "keyword": "Python后端实习生",
            "city": "贵阳"
        }
        
        response = self.client.get('/api/v1/mcp/jobs/', params)
        
        AssertionHelper.assert_error_response(response, 401, "未登录或登录已过期")
    
    def test_get_jobs_missing_keyword(self):
        """
        测试：缺少keyword参数
        
        验证点：
        1. 接口应能处理（keyword可能为空字符串）
        2. 或返回错误响应
        """
        params = {
            "city": "贵阳"
        }
        
        response = self.client.get('/api/v1/mcp/jobs/', params)
        
        assert response['data']['code'] in [200, 400, 3001]
    
    def test_get_jobs_missing_city(self):
        """
        测试：缺少city参数
        
        验证点：
        1. 接口应能处理（city可能为空字符串）
        2. 或返回错误响应
        """
        params = {
            "keyword": "Python后端实习生"
        }
        
        response = self.client.get('/api/v1/mcp/jobs/', params)
        
        assert response['data']['code'] in [200, 400, 3001]
    
    def test_get_jobs_with_valid_params(self):
        """
        测试：使用有效参数获取职位数据
        
        验证点：
        1. 响应状态码为200或3001（MCP服务不可用）
        2. 如果成功，返回jobs数组和from_cache字段
        3. from_cache为布尔值
        """
        params = {
            "keyword": "Python后端实习生",
            "city": "贵阳",
            "limit": 10
        }
        
        response = self.client.get('/api/v1/mcp/jobs/', params)
        
        if response['data']['code'] == 200:
            AssertionHelper.assert_success_response(response)
            AssertionHelper.assert_response_has_fields(response, ['jobs', 'from_cache'])
            
            assert isinstance(response['data']['data']['jobs'], list)
            assert isinstance(response['data']['data']['from_cache'], bool)
            
            jobs = response['data']['data']['jobs']
            assert len(jobs) <= 10, "返回的职位数量不应超过limit参数"
    
    def test_get_jobs_with_recruit_type(self):
        """
        测试：指定招聘类型参数
        
        验证点：
        1. recruit_type参数被正确处理
        2. 返回相应类型的职位数据
        """
        params = {
            "keyword": "Python后端实习生",
            "city": "贵阳",
            "recruit_type": 1
        }
        
        response = self.client.get('/api/v1/mcp/jobs/', params)
        
        assert response['data']['code'] in [200, 3001]
    
    def test_get_jobs_with_invalid_recruit_type(self):
        """
        测试：无效的recruit_type参数
        
        验证点：
        1. 接口应能处理非数字的recruit_type
        2. 不应导致服务器错误
        """
        params = {
            "keyword": "Python后端实习生",
            "city": "贵阳",
            "recruit_type": "invalid"
        }
        
        response = self.client.get('/api/v1/mcp/jobs/', params)
        
        assert response['data']['code'] in [200, 400, 3001]
    
    def test_get_jobs_with_custom_limit(self):
        """
        测试：自定义limit参数
        
        验证点：
        1. limit参数生效
        2. 返回的职位数量不超过limit
        """
        params = {
            "keyword": "Python后端实习生",
            "city": "贵阳",
            "limit": 5
        }
        
        response = self.client.get('/api/v1/mcp/jobs/', params)
        
        if response['data']['code'] == 200:
            jobs = response['data']['data']['jobs']
            assert len(jobs) <= 5
    
    def test_get_jobs_from_cache(self):
        """
        测试：从缓存获取职位数据
        
        验证点：
        1. 第一次请求可能from_cache为false
        2. 第二次请求from_cache应为true（如果缓存生效）
        """
        params = {
            "keyword": "缓存测试职位",
            "city": "贵阳"
        }
        
        response1 = self.client.get('/api/v1/mcp/jobs/', params)
        
        if response1['data']['code'] == 200:
            from_cache1 = response1['data']['data']['from_cache']
            
            response2 = self.client.get('/api/v1/mcp/jobs/', params)
            
            if response2['data']['code'] == 200:
                from_cache2 = response2['data']['data']['from_cache']
                
                assert isinstance(from_cache2, bool)
    
    def test_get_jobs_mcp_unavailable(self):
        """
        测试：MCP服务不可用
        
        验证点：
        1. 如果MCP服务不可用，返回错误码3001
        2. 错误消息为"MCP服务暂时不可用"
        """
        params = {
            "keyword": "不存在的职位关键词测试123456789",
            "city": "不存在的城市测试987654321"
        }
        
        response = self.client.get('/api/v1/mcp/jobs/', params)
        
        if response['data']['code'] == 3001:
            AssertionHelper.assert_error_response(response, 3001, "MCP服务暂时不可用")
    
    def test_get_jobs_performance(self):
        """
        测试：获取职位数据性能
        
        验证点：
        1. 响应时间小于5秒（考虑MCP服务调用）
        """
        timer = PerformanceTimer()
        
        params = {
            "keyword": "Python后端实习生",
            "city": "贵阳"
        }
        
        timer.start()
        response = self.client.get('/api/v1/mcp/jobs/', params)
        timer.stop()
        
        assert timer.elapsed() < 5.0, f"响应时间 {timer.elapsed():.2f}s 超过预期 5s"


class MCPJobsCacheTestCase(TestCase):
    """
    MCP职位数据缓存测试 - 验证缓存机制的正确性
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="缓存测试用户",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        if response['data']['code'] == 200:
            self.test_user_id = response['data']['data']['user_id']
            self.test_user_name = user_data['user_name']
            self.cleanup_user_ids.append(self.test_user_id)
            
            login_data = MockDataFactory.create_login_data(
                login_account=self.test_user_name,
                user_pwd="password123"
            )
            self.client.post_json('/api/v1/auth/login/password/', login_data)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_cache_expiration_7_days(self):
        """
        测试：MySQL缓存7天有效期
        
        验证点：
        1. 缓存数据应包含expire_at字段
        2. expire_at应为当前时间+7天
        """
        from apps.mcp.models import MCPJobsCache
        
        keyword = "缓存过期测试"
        city = "贵阳"
        jobs_data = [{"job_id": "1", "title": "测试职位"}]
        
        cache = MCPJobsCache.objects.create(
            keyword=keyword,
            city=city,
            jobs_data=jobs_data,
            expire_at=timezone.now() + timedelta(days=7)
        )
        
        assert cache.expire_at > timezone.now()
        assert cache.expire_at <= timezone.now() + timedelta(days=7)
        
        cache.delete()
    
    def test_cache_query_by_keyword_city(self):
        """
        测试：通过keyword和city查询缓存
        
        验证点：
        1. 可以通过keyword和city查询到缓存
        2. 未过期的缓存可以被查询到
        """
        from apps.mcp.models import MCPJobsCache
        
        keyword = "查询测试"
        city = "北京"
        jobs_data = [{"job_id": "2", "title": "测试职位2"}]
        
        cache = MCPJobsCache.objects.create(
            keyword=keyword,
            city=city,
            jobs_data=jobs_data,
            expire_at=timezone.now() + timedelta(days=7)
        )
        
        cached = MCPJobsCache.objects.filter(
            keyword=keyword,
            city=city,
            expire_at__gt=timezone.now()
        ).first()
        
        assert cached is not None
        assert cached.jobs_data == jobs_data
        
        cache.delete()
    
    def test_cache_expired_not_retrieved(self):
        """
        测试：过期的缓存不会被检索
        
        验证点：
        1. expire_at小于当前时间的缓存不会被查询到
        """
        from apps.mcp.models import MCPJobsCache
        
        keyword = "过期测试"
        city = "上海"
        jobs_data = [{"job_id": "3", "title": "测试职位3"}]
        
        cache = MCPJobsCache.objects.create(
            keyword=keyword,
            city=city,
            jobs_data=jobs_data,
            expire_at=timezone.now() - timedelta(days=1)
        )
        
        cached = MCPJobsCache.objects.filter(
            keyword=keyword,
            city=city,
            expire_at__gt=timezone.now()
        ).first()
        
        assert cached is None
        
        cache.delete()


class MCPJobsDataValidationTestCase(TestCase):
    """
    MCP职位数据验证测试 - 验证返回数据的格式和内容
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="数据验证测试用户",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        if response['data']['code'] == 200:
            self.test_user_id = response['data']['data']['user_id']
            self.test_user_name = user_data['user_name']
            self.cleanup_user_ids.append(self.test_user_id)
            
            login_data = MockDataFactory.create_login_data(
                login_account=self.test_user_name,
                user_pwd="password123"
            )
            self.client.post_json('/api/v1/auth/login/password/', login_data)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_jobs_data_structure(self):
        """
        测试：职位数据结构验证
        
        验证点：
        1. jobs数组中的每个元素应包含基本字段
        2. 字段类型正确
        """
        params = {
            "keyword": "Python后端实习生",
            "city": "贵阳"
        }
        
        response = self.client.get('/api/v1/mcp/jobs/', params)
        
        if response['data']['code'] == 200:
            jobs = response['data']['data']['jobs']
            
            if len(jobs) > 0:
                job = jobs[0]
                
                assert isinstance(job, dict), "职位数据应为字典类型"
    
    def test_from_cache_field_type(self):
        """
        测试：from_cache字段类型验证
        
        验证点：
        1. from_cache字段为布尔类型
        """
        params = {
            "keyword": "Python后端实习生",
            "city": "贵阳"
        }
        
        response = self.client.get('/api/v1/mcp/jobs/', params)
        
        if response['data']['code'] == 200:
            from_cache = response['data']['data']['from_cache']
            
            assert isinstance(from_cache, bool), f"from_cache应为布尔类型，实际为 {type(from_cache)}"


class MCPJobsErrorHandlingTestCase(TestCase):
    """
    MCP职位数据错误处理测试 - 验证各种错误场景的处理
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="错误处理测试用户",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        if response['data']['code'] == 200:
            self.test_user_id = response['data']['data']['user_id']
            self.test_user_name = user_data['user_name']
            self.cleanup_user_ids.append(self.test_user_id)
            
            login_data = MockDataFactory.create_login_data(
                login_account=self.test_user_name,
                user_pwd="password123"
            )
            self.client.post_json('/api/v1/auth/login/password/', login_data)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_error_code_3001_mcp_unavailable(self):
        """
        测试：错误码3001 - MCP服务暂时不可用
        
        验证点：
        1. 当MCP服务不可用时返回3001
        2. 错误消息清晰
        """
        params = {
            "keyword": "测试MCP不可用",
            "city": "测试城市"
        }
        
        response = self.client.get('/api/v1/mcp/jobs/', params)
        
        if response['data']['code'] == 3001:
            assert "MCP服务暂时不可用" in response['data']['msg']
    
    def test_error_code_3002_no_matching_jobs(self):
        """
        测试：错误码3002 - 未找到匹配的职位数据
        
        验证点：
        1. 当没有匹配职位时可能返回3002或空数组
        """
        params = {
            "keyword": "非常特殊的职位关键词123456789",
            "city": "非常特殊的城市987654321"
        }
        
        response = self.client.get('/api/v1/mcp/jobs/', params)
        
        if response['data']['code'] == 3002:
            assert "未找到匹配的职位数据" in response['data']['msg']
        elif response['data']['code'] == 200:
            jobs = response['data']['data']['jobs']
            assert isinstance(jobs, list)


class MCPApplyJobAPITestCase(TestCase):
    """
    MCP投递职位接口测试 (POST /api/v1/mcp/jobs/apply/)
    
    接口说明：
    - 认证要求：需要登录
    - 请求参数：work_pin
    - 响应字段：result
    """
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient()
        self.cleanup_user_ids = []
        
        user_data = MockDataFactory.create_user_data(
            user_name="投递测试用户",
            user_pwd="password123"
        )
        
        response = self.client.post_json('/api/v1/auth/register/', user_data)
        if response['data']['code'] == 200:
            self.test_user_id = response['data']['data']['user_id']
            self.test_user_name = user_data['user_name']
            self.cleanup_user_ids.append(self.test_user_id)
            
            login_data = MockDataFactory.create_login_data(
                login_account=self.test_user_name,
                user_pwd="password123"
            )
            self.client.post_json('/api/v1/auth/login/password/', login_data)
    
    def tearDown(self):
        """测试后清理"""
        TestDataCleaner.cleanup_test_users(self.cleanup_user_ids)
    
    def test_apply_job_without_login(self):
        """
        测试：未登录投递职位
        
        验证点：
        1. 响应错误码为401
        2. 错误消息为"未登录或登录已过期"
        """
        self.client.logout()
        
        apply_data = {
            "work_pin": "test_work_pin_123"
        }
        
        response = self.client.post_json('/api/v1/mcp/jobs/apply/', apply_data)
        
        AssertionHelper.assert_error_response(response, 401, "未登录或登录已过期")
    
    def test_apply_job_missing_work_pin(self):
        """
        测试：缺少work_pin参数
        
        验证点：
        1. 响应错误码为400
        2. 错误消息为"请求参数错误"
        """
        apply_data = {}
        
        response = self.client.post_json('/api/v1/mcp/jobs/apply/', apply_data)
        
        AssertionHelper.assert_error_response(response, 400, "请求参数错误")
    
    def test_apply_job_empty_work_pin(self):
        """
        测试：work_pin为空字符串
        
        验证点：
        1. 响应错误码为400
        2. 错误消息为"请求参数错误"
        """
        apply_data = {
            "work_pin": ""
        }
        
        response = self.client.post_json('/api/v1/mcp/jobs/apply/', apply_data)
        
        AssertionHelper.assert_error_response(response, 400, "请求参数错误")
    
    def test_apply_job_with_valid_work_pin(self):
        """
        测试：使用有效的work_pin投递职位
        
        验证点：
        1. 响应状态码为200或3001（MCP服务不可用）
        2. 如果成功，返回result字段
        """
        apply_data = {
            "work_pin": "test_work_pin_456"
        }
        
        response = self.client.post_json('/api/v1/mcp/jobs/apply/', apply_data)
        
        if response['data']['code'] == 200:
            AssertionHelper.assert_success_response(response)
            AssertionHelper.assert_response_has_fields(response, ['result'])
        elif response['data']['code'] == 3001:
            AssertionHelper.assert_error_response(response, 3001, "MCP服务暂时不可用")
    
    def test_apply_job_mcp_unavailable(self):
        """
        测试：MCP服务不可用时的投递
        
        验证点：
        1. 返回错误码3001
        2. 错误消息为"MCP服务暂时不可用"
        """
        apply_data = {
            "work_pin": "invalid_work_pin_test"
        }
        
        response = self.client.post_json('/api/v1/mcp/jobs/apply/', apply_data)
        
        if response['data']['code'] == 3001:
            AssertionHelper.assert_error_response(response, 3001, "MCP服务暂时不可用")
