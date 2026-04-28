import json
import asyncio
from django.views import View
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone

from .models import ChatSession, ChatMessage
from apps.face.views import get_login_user_id
from core.utils.response import api_response, format_datetime
from ai.agents.loader import load_agent


@method_decorator(csrf_exempt, name='dispatch')
class SessionListView(View):
    def get(self, request):
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
    def get(self, request, session_id):
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
    def delete(self, request, session_id):
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


def _build_sse_event(event_type, data=""):
    if data == "":
        return f"event: {event_type}\n\n"
    return f"event: {event_type}\ndata: {data}\n\n"


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
            role="user",
            content=content
        )

        full_content = ""
        full_thinking = ""

        try:
            agent = await load_agent()
            msg = {"messages": [{"role": "user", "content": content}]}

            async for event in agent.astream_events(msg, version='v2'):
                if event["event"] == "on_chat_model_stream":
                    chunk = event["data"].get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        text = chunk.content
                        full_content += text
                        yield _build_sse_event("content", text)

            yield _build_sse_event("end")

        except Exception as e:
            yield _build_sse_event("error", f"服务器内部错误，请稍后再试")

        if full_content:
            await ChatMessage.objects.acreate(
                session_id=session_id,
                role="assistant",
                content=full_content,
                thinking_process=full_thinking if full_thinking else None,
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
