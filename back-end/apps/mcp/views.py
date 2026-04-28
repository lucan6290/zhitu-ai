import json
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta

from .models import MCPJobsCache
from apps.face.views import get_login_user_id
from core.utils.response import api_response


async def _fetch_jobs_from_mcp(keyword, city, limit=20):
    try:
        from ai.mcp.client import mcp_client
        tools = await mcp_client.get_tools()
        for tool in tools:
            if tool.name == "search_jobs":
                result = await tool.ainvoke({
                    "keyword": keyword,
                    "city": city,
                    "limit": limit
                })
                return json.loads(result) if isinstance(result, str) else result
    except Exception as e:
        print(f"MCP工具调用失败: {e}")
    return None


@method_decorator(csrf_exempt, name='dispatch')
class JobsView(View):
    def get(self, request):
        user_id = get_login_user_id(request)
        if not user_id:
            return api_response(code=401, msg="未登录或登录已过期")

        keyword = request.GET.get("keyword", "").strip()
        city = request.GET.get("city", "").strip()
        limit = int(request.GET.get("limit", 20))

        if not keyword or not city:
            return api_response(code=400, msg="请求参数错误")

        from_cache = True

        db_cache = MCPJobsCache.objects.filter(
            keyword=keyword,
            city=city,
            expire_at__gt=timezone.now()
        ).first()

        if db_cache:
            jobs_data = db_cache.jobs_data
        else:
            from_cache = False

            loop = __import__('asyncio').new_event_loop()
            try:
                jobs_data = loop.run_until_complete(_fetch_jobs_from_mcp(keyword, city, limit))
            finally:
                loop.close()

            if jobs_data is None:
                return api_response(code=3001, msg="MCP服务暂时不可用")

            MCPJobsCache.objects.create(
                keyword=keyword,
                city=city,
                jobs_data=jobs_data,
                expire_at=timezone.now() + timedelta(days=7)
            )

        if isinstance(jobs_data, str):
            try:
                jobs_data = json.loads(jobs_data)
            except json.JSONDecodeError:
                pass

        return api_response(data={
            "jobs": jobs_data if isinstance(jobs_data, list) else [jobs_data],
            "from_cache": from_cache,
        })
