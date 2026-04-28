import json
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta

from .models import MCPJobsCache
from apps.face.views import get_login_user_id
from core.utils.response import api_response


async def _fetch_jobs_from_mcp(keyword="", recruit_type=None):
    try:
        from ai.mcp.client import mcp_client
        async with mcp_client:
            tools = mcp_client.get_tools()
            for tool in tools:
                if tool.name == "get-job-list":
                    invoke_args = {}
                    if keyword:
                        invoke_args["keyword"] = keyword
                    if recruit_type is not None:
                        invoke_args["recruitType"] = recruit_type
                    result = await tool.ainvoke(invoke_args)
                    if isinstance(result, str):
                        try:
                            return json.loads(result)
                        except json.JSONDecodeError:
                            return result
                    return result
    except Exception as e:
        print(f"MCP工具调用失败: {e}")
    return None


async def _apply_job_from_mcp(work_pin):
    try:
        from ai.mcp.client import mcp_client
        async with mcp_client:
            tools = mcp_client.get_tools()
            for tool in tools:
                if tool.name == "apply-for-job":
                    result = await tool.ainvoke({"workPin": work_pin})
                    if isinstance(result, str):
                        try:
                            return json.loads(result)
                        except json.JSONDecodeError:
                            return result
                    return result
    except Exception as e:
        print(f"MCP投递职位失败: {e}")
    return None


@method_decorator(csrf_exempt, name='dispatch')
class JobsView(View):
    def get(self, request):
        user_id = get_login_user_id(request)
        if not user_id:
            return api_response(code=401, msg="未登录或登录已过期")

        keyword = request.GET.get("keyword", "").strip()
        city = request.GET.get("city", "").strip()
        recruit_type = request.GET.get("recruit_type")
        limit = int(request.GET.get("limit", 20))

        if recruit_type:
            try:
                recruit_type = int(recruit_type)
            except (ValueError, TypeError):
                recruit_type = None

        from_cache = True

        db_cache = MCPJobsCache.objects.filter(
            keyword=keyword,
            city=city,
            recruit_type=recruit_type,
            expire_at__gt=timezone.now()
        ).first()

        if db_cache:
            jobs_data = db_cache.jobs_data
        else:
            from_cache = False

            loop = __import__('asyncio').new_event_loop()
            try:
                jobs_data = loop.run_until_complete(
                    _fetch_jobs_from_mcp(keyword, recruit_type)
                )
            finally:
                loop.close()

            if jobs_data is None:
                return api_response(code=3001, msg="MCP服务暂时不可用")

            MCPJobsCache.objects.create(
                keyword=keyword,
                city=city,
                recruit_type=recruit_type,
                jobs_data=jobs_data,
                expire_at=timezone.now() + timedelta(days=7)
            )

        if isinstance(jobs_data, str):
            try:
                jobs_data = json.loads(jobs_data)
            except json.JSONDecodeError:
                pass

        if isinstance(jobs_data, list):
            jobs_list = jobs_data[:limit]
        elif isinstance(jobs_data, dict):
            jobs_list = [jobs_data]
        else:
            jobs_list = []

        return api_response(data={
            "jobs": jobs_list,
            "from_cache": from_cache,
        })


@method_decorator(csrf_exempt, name='dispatch')
class ApplyJobView(View):
    def post(self, request):
        user_id = get_login_user_id(request)
        if not user_id:
            return api_response(code=401, msg="未登录或登录已过期")

        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return api_response(code=400, msg="请求参数错误")

        work_pin = data.get("work_pin", "").strip()
        if not work_pin:
            return api_response(code=400, msg="请求参数错误")

        loop = __import__('asyncio').new_event_loop()
        try:
            result = loop.run_until_complete(_apply_job_from_mcp(work_pin))
        finally:
            loop.close()

        if result is None:
            return api_response(code=3001, msg="MCP服务暂时不可用")

        return api_response(data={"result": result})
