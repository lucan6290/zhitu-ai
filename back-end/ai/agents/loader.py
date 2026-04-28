"""
Agent加载器 - 加载LLM和Agent
支持MCP工具和本地工具
"""

import os
import asyncio
from typing import Optional, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
import requests
from django.conf import settings

from ai.mcp.client import mcp_client
from ai.prompts.system_prompt import SYSTEM_PROMPT


class LLMService:
    """LLM服务 - 单例模式管理LLM实例"""

    _instance: Optional['LLMService'] = None
    _llm: Optional[ChatOpenAI] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._llm is None:
            self._load_env()
            config = settings.LLM_CONFIG
            self._llm = ChatOpenAI(
                model=config['model'],
                api_key=config['api_key'],
                base_url=config['base_url']
            )

    @staticmethod
    def _load_env():
        """加载环境变量"""
        env_path = settings.BASE_DIR / '.env'
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)

    @property
    def llm(self) -> ChatOpenAI:
        return self._llm


def load_llm() -> ChatOpenAI:
    """加载LLM实例"""
    service = LLMService()
    return service.llm


@tool
def get_weather(city: str) -> str:
    """本地工具：查询天气"""
    url = f"https://api.seniverse.com/v3/weather/now.json?key=SQODkj_zcH9MQkxju&location={city}&language=zh-Hans&unit=c"
    try:
        res = requests.get(url, timeout=10)
        return str(res.json())
    except Exception as e:
        return f"天气查询失败: {str(e)}"


@tool
def get_age(name: str) -> str:
    """本地工具：查询年龄（模拟数据）"""
    data = [
        {"name": "张三", "age": 23},
        {"name": "李四", "age": 24},
        {"name": "王五", "age": 25},
        {"name": "赵六", "age": 26}
    ]
    for item in data:
        if name == item["name"]:
            return f"用户姓名是{name}，年龄是{item['age']}"
    return "没有该用户"


async def load_agent():
    """加载Agent - 合并MCP工具和本地工具"""
    llm = load_llm()
    tools: List = []

    # 尝试从MCP服务器加载工具
    try:
        print("正在连接 MCP 服务器加载工具...")
        tools = await mcp_client.get_tools()
        print(f"MCP 工具加载成功，共 {len(tools)} 个工具")
    except Exception as e:
        print(f"MCP 服务器连接失败：{e}")
        print("将仅使用本地工具")
        tools = []

    # 合并所有工具
    all_tools = tools + [get_weather, get_age]
    print(f"总共加载 {len(all_tools)} 个工具")

    # 创建Agent
    agent = create_agent(
        model=llm,
        tools=all_tools,
        system_prompt=SYSTEM_PROMPT
    )
    return agent
