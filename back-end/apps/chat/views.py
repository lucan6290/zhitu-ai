"""
聊天应用视图模块
===============

本模块提供聊天功能的HTTP接口，包括会话管理和AI对话。

主要功能：
- 会话列表管理（创建、查询、删除）
- 消息历史查询
- AI Agent流式对话（SSE实时推送）

API接口：
- GET/POST /sessions/: 会话列表和创建
- GET /sessions/<id>/messages/: 获取会话消息
- DELETE /sessions/<id>/: 删除会话
- GET /agent/: AI Agent流式对话

技术特点：
- 使用Server-Sent Events (SSE)实现流式响应
- 支持深度思考模式，展示AI推理过程
- 自动提取ECharts配置用于数据可视化
- 异步处理提升并发性能

使用示例：
    # 创建会话
    POST /chat/sessions/
    {"title": "技术咨询"}
    
    # 发送消息（SSE流式响应）
    GET /chat/agent/?session_id=1&content=你好&deep_thinking=true
"""

import json
import logging
import re
import asyncio
from django.views import View
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone

from .models import ChatSession, ChatMessage

logger = logging.getLogger(__name__)
from apps.face.views import get_login_user_id
from core.utils.response import api_response, format_datetime
from ai.agents.loader import load_llm, get_database
from ai.prompts.system_prompt import SYSTEM_PROMPT
from ai.mcp.client import mcp_client

from langchain.agents import create_agent


def _build_sse_event(event_type, data=""):
    """
    构建Server-Sent Events (SSE)事件字符串
    
    SSE是一种服务器向客户端推送数据的技术，常用于实时更新场景。
    
    Args:
        event_type: 事件类型，用于客户端区分不同消息
            - content: AI回复内容片段
            - thinking: AI思考过程
            - echarts: 图表配置
            - end: 流结束标志
            - error: 错误信息
        data: 事件数据，可选
    
    Returns:
        str: 符合SSE格式的事件字符串
    
    Format:
        event: {event_type}
        data: {data}
        
    Example:
        >>> _build_sse_event("content", "你好")
        'event: content\\ndata: 你好\\n\\n'
        
        >>> _build_sse_event("end")
        'event: end\\n\\n'
    """
    if data == "":
        return f"event: {event_type}\n\n"
    return f"event: {event_type}\ndata: {data}\n\n"


def _extract_echarts_config(content: str):
    """
    从AI回复内容中提取ECharts JSON配置
    
    AI回复中可能包含Markdown代码块格式的ECharts配置，
    此函数负责解析并提取有效的配置对象。
    
    Args:
        content: AI回复的完整文本内容
    
    Returns:
        dict | None: 第一个有效的ECharts配置对象，无则返回None
    
    Detection:
        - 查找```json代码块
        - 验证是否包含series或xAxis字段（ECharts特征）
        - 忽略JSON解析错误
    
    Example:
        >>> content = '这是图表：\\n```json\\n{"series": [...]}\\n```'
        >>> config = _extract_echarts_config(content)
        >>> print(config)
        {"series": [...]}
    """
    charts = []
    pattern = r'```json\s*\n(\{[\s\S]*?\})\s*\n```'
    matches = re.findall(pattern, content)
    for match in matches:
        try:
            config = json.loads(match)
            if 'series' in config or 'xAxis' in config:
                charts.append(config)
        except json.JSONDecodeError:
            continue
    return charts[0] if charts else None


@method_decorator(csrf_exempt, name='dispatch')
class SessionListView(View):
    """
    会话列表视图
    
    处理用户的会话列表查询和创建请求。
    
    Endpoints:
        GET /sessions/: 获取当前用户的所有会话列表
        POST /sessions/: 创建新的聊天会话
    
    Authentication:
        需要通过Session验证用户身份（get_login_user_id）
    
    GET Response:
        {
            "code": 200,
            "msg": "success",
            "data": {
                "sessions": [
                    {
                        "session_id": 1,
                        "title": "技术咨询",
                        "last_message_time": "2024-01-01T12:00:00"
                    }
                ]
            }
        }
    
    POST Request Body:
        {
            "title": "新会话标题"  // 可选，默认"新会话"
        }
    
    POST Response:
        {
            "code": 200,
            "msg": "success",
            "data": {
                "session_id": 1,
                "title": "新会话标题"
            }
        }
    """
    
    def get(self, request):
        """
        获取用户会话列表
        
        查询当前用户的所有会话，按最后消息时间倒序排列。
        
        Args:
            request: Django HTTP请求对象
        
        Returns:
            JsonResponse: 包含会话列表的API响应
                - code 401: 未登录
                - code 200: 成功，返回会话列表
        """
        user_id = get_login_user_id(request)
        if not user_id:
            return api_response(code=401, msg="未登录或登录已过期")

        sessions = ChatSession.objects.filter(user_id=user_id).order_by('-last_message_time')
        session_list = []
        for s in sessions:
            session_list.append({
                "session_id": s.session_id,
                "title": s.title,
                "last_message_time": format_datetime(s.last_message_time),
            })
        return api_response(data={"sessions": session_list})

    def post(self, request):
        """
        创建新会话
        
        为当前用户创建一个新的聊天会话。
        
        Args:
            request: Django HTTP请求对象
                - body: JSON格式的请求体（可选）
                    - title: 会话标题
        
        Returns:
            JsonResponse: 包含新会话信息的API响应
                - code 401: 未登录
                - code 200: 成功，返回会话ID和标题
        """
        user_id = get_login_user_id(request)
        if not user_id:
            return api_response(code=401, msg="未登录或登录已过期")

        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else {}
        except json.JSONDecodeError:
            data = {}

        title = data.get("title", "新会话")
        session = ChatSession.objects.create(user_id=user_id, title=title)
        return api_response(data={
            "session_id": session.session_id,
            "title": session.title,
        })


@method_decorator(csrf_exempt, name='dispatch')
class SessionMessagesView(View):
    """
    会话消息视图
    
    获取指定会话的所有消息历史记录。
    
    Endpoints:
        GET /sessions/<session_id>/messages/: 获取会话消息列表
    
    Authentication:
        需要验证用户身份和会话所有权
    
    URL Parameters:
        session_id: 会话ID（整数）
    
    Response:
        {
            "code": 200,
            "msg": "success",
            "data": {
                "messages": [
                    {
                        "message_id": 1,
                        "role": "user",
                        "content": "消息内容",
                        "thinking_process": "思考过程",
                        "echarts_config": {...},
                        "created_at": "2024-01-01T12:00:00"
                    }
                ]
            }
        }
    
    Error Codes:
        - 401: 未登录
        - 2001: 会话不存在
        - 2002: 无权访问该会话
    """
    
    def get(self, request, session_id):
        """
        获取会话消息列表
        
        查询指定会话的所有消息，按创建时间正序排列。
        验证用户是否有权访问该会话。
        
        Args:
            request: Django HTTP请求对象
            session_id: 会话ID（从URL路径获取）
        
        Returns:
            JsonResponse: 包含消息列表的API响应
        """
        user_id = get_login_user_id(request)
        if not user_id:
            return api_response(code=401, msg="未登录或登录已过期")

        try:
            session = ChatSession.objects.get(session_id=session_id)
        except ChatSession.DoesNotExist:
            return api_response(code=2001, msg="会话不存在")

        if session.user_id != user_id:
            return api_response(code=2002, msg="无权访问该会话")

        messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        msg_list = []
        for m in messages:
            msg_list.append({
                "message_id": m.message_id,
                "role": m.role,
                "content": m.content,
                "thinking_process": m.thinking_process,
                "echarts_config": m.echarts_config,
                "created_at": format_datetime(m.created_at),
            })
        return api_response(data={"messages": msg_list})


@method_decorator(csrf_exempt, name='dispatch')
class SessionDeleteView(View):
    """
    会话删除视图
    
    删除指定的聊天会话及其所有消息。
    
    Endpoints:
        DELETE /sessions/<session_id>/: 删除会话
    
    Authentication:
        需要验证用户身份和会话所有权
    
    URL Parameters:
        session_id: 会话ID（整数）
    
    Response:
        {
            "code": 200,
            "msg": "success",
            "data": null
        }
    
    Error Codes:
        - 401: 未登录
        - 2001: 会话不存在
        - 2002: 无权访问该会话
    
    Note:
        删除会话会级联删除所有关联的消息记录
    """
    
    def delete(self, request, session_id):
        """
        删除会话
        
        验证用户权限后删除指定会话。
        由于ChatMessage的外键设置了CASCADE，相关消息会自动删除。
        
        Args:
            request: Django HTTP请求对象
            session_id: 会话ID（从URL路径获取）
        
        Returns:
            JsonResponse: 删除结果的API响应
        """
        user_id = get_login_user_id(request)
        if not user_id:
            return api_response(code=401, msg="未登录或登录已过期")

        try:
            session = ChatSession.objects.get(session_id=session_id)
        except ChatSession.DoesNotExist:
            return api_response(code=2001, msg="会话不存在")

        if session.user_id != user_id:
            return api_response(code=2002, msg="无权访问该会话")

        session.delete()
        return api_response()


def stream_agent_chat_sse(session_id, user_id, content, deep_thinking=False):
    async def _async_stream():
        try:
            session = await ChatSession.objects.aget(session_id=session_id)
            if session.user_id != user_id:
                yield _build_sse_event("error", "无权访问该会话")
                return
        except ChatSession.DoesNotExist:
            yield _build_sse_event("error", "会话不存在")
            return

        await ChatMessage.objects.acreate(
            session_id=session_id,
            user_id=user_id,
            role="user",
            content=content
        )

        full_content = ""
        full_thinking = ""
        echarts_config = None

        try:
            llm = load_llm()

            mcp_tools = await mcp_client.get_tools()
            all_tools = list(mcp_tools) + [get_database]

            agent = create_agent(
                model=llm,
                tools=all_tools,
                system_prompt=SYSTEM_PROMPT
            )

            msg = {"messages": [{"role": "user", "content": content}]}

            async for event in agent.astream_events(msg, version='v2'):
                event_type = event.get("event", "")
                event_name = event.get("name", "")

                # 工具调用开始 - 思考过程
                if event_type == "on_tool_start" and deep_thinking:
                    tool_name = event_name or event.get("tags", ["tool"])[0]
                    tool_input = event.get("data", {}).get("input", {})
                    thinking_text = f"[工具调用] {tool_name}({json.dumps(tool_input, ensure_ascii=False)})\n"
                    full_thinking += thinking_text
                    yield _build_sse_event("thinking", thinking_text)

                # 工具调用返回 - 思考过程
                elif event_type == "on_tool_end" and deep_thinking:
                    tool_name = event_name or event.get("tags", ["tool"])[0]
                    tool_output = event.get("data", {}).get("output", "")
                    output_preview = str(tool_output)[:200]
                    thinking_text = f"[工具返回] {tool_name}: {output_preview}\n\n"
                    full_thinking += thinking_text
                    yield _build_sse_event("thinking", thinking_text)

                # 链式调用事件（数据分析等）- 思考过程
                elif event_type == "on_chain_stream" and deep_thinking:
                    chunk = event.get("data", {}).get("chunk")
                    if chunk:
                        if hasattr(chunk, 'content'):
                            chain_text = str(chunk.content)
                        else:
                            chain_text = str(chunk)
                        if chain_text and len(chain_text) > 0:
                            thinking_text = f"[数据分析] {chain_text}\n"
                            full_thinking += thinking_text
                            yield _build_sse_event("thinking", thinking_text)

                # 聊天模型流式输出 - 最终内容
                elif event_type == "on_chat_model_stream":
                    chunk = event["data"].get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        text = chunk.content
                        full_content += text
                        if deep_thinking:
                            full_thinking += text
                        yield _build_sse_event("content", text)

            # 提取ECharts配置
            echarts_config = _extract_echarts_config(full_content)
            if echarts_config:
                yield _build_sse_event("echarts", json.dumps(echarts_config, ensure_ascii=False))

            yield _build_sse_event("end")

        except Exception as e:
            logger.exception(f"Agent stream error: {e}")
            yield _build_sse_event("error", "服务器内部错误，请稍后再试")

        # 保存AI回复到数据库
        if full_content:
            thinking_to_save = full_thinking if deep_thinking else None
            await ChatMessage.objects.acreate(
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=full_content,
                thinking_process=thinking_to_save,
                echarts_config=echarts_config,
            )
            await ChatSession.objects.filter(session_id=session_id).aupdate(
                last_message_time=timezone.now()
            )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async_gen = _async_stream()

    try:
        while True:
            try:
                chunk = loop.run_until_complete(async_gen.__anext__())
                yield chunk
            except StopAsyncIteration:
                break
            except Exception as e:
                logger.exception(f"Stream iteration error: {e}")
                yield _build_sse_event("error", "服务器内部错误，请稍后再试")
                break
    finally:
        loop.close()


@method_decorator(csrf_exempt, name='dispatch')
class ChatAgentView(View):
    def get(self, request):
        user_id = get_login_user_id(request)
        if not user_id:
            return StreamingHttpResponse(
                iter([_build_sse_event("error", "未登录或登录已过期")]),
                content_type="text/event-stream"
            )

        session_id = request.GET.get("session_id")
        content = request.GET.get("content")
        deep_thinking = request.GET.get("deep_thinking", "false").lower() == "true"

        if not session_id or not content:
            return StreamingHttpResponse(
                iter([_build_sse_event("error", "请求参数错误")]),
                content_type="text/event-stream"
            )

        try:
            session_id = int(session_id)
        except (ValueError, TypeError):
            return StreamingHttpResponse(
                iter([_build_sse_event("error", "请求参数错误")]),
                content_type="text/event-stream"
            )

        try:
            return StreamingHttpResponse(
                stream_agent_chat_sse(session_id, user_id, content, deep_thinking),
                content_type="text/event-stream"
            )
        except Exception as e:
            return StreamingHttpResponse(
                iter([_build_sse_event("error", "服务器内部错误，请稍后再试")]),
                content_type="text/event-stream"
            )
