from django.db import models


class MCPJobsCache(models.Model):
    cache_id = models.BigAutoField(primary_key=True, verbose_name='缓存ID')
    keyword = models.CharField(max_length=200, default='', verbose_name='岗位关键词')
    city = models.CharField(max_length=100, default='', verbose_name='城市')
    recruit_type = models.IntegerField(null=True, blank=True, verbose_name='职位类型')
    jobs_data = models.JSONField(verbose_name='职位数据')
    expire_at = models.DateTimeField(verbose_name='过期时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'mcp_jobs_cache'
        verbose_name = 'MCP职位缓存'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.keyword} - {self.city} - {self.recruit_type}"
