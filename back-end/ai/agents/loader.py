"""
Agent加载器模块
================

本模块负责加载和初始化大语言模型(LLM)及Agent实例。

主要功能：
- 提供单例模式的LLM服务管理
- 加载MCP招聘数据工具和本地数据库查询工具
- 创建配置完整的LangChain Agent实例

使用示例：
    from ai.agents.loader import load_llm, load_agent
    
    # 获取LLM实例
    llm = load_llm()
    
    # 加载完整Agent（异步）
    agent = await load_agent()

依赖说明：
- langchain_openai: OpenAI兼容的LLM接口
- langchain.agents: Agent创建和管理
- ai.mcp.client: MCP工具客户端
- ai.mcp.server: 本地数据库查询服务
"""

import os
import asyncio
from typing import Optional, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from django.conf import settings

from ai.mcp.client import mcp_client
from ai.mcp.server import query_database
from ai.prompts.system_prompt import SYSTEM_PROMPT


class LLMService:
    """
    LLM服务单例类
    
    采用单例模式管理LLM实例，确保全局只有一个LLM连接，
    避免重复初始化和资源浪费。
    
    Attributes:
        _instance: 类级别的单例实例
        _llm: ChatOpenAI实例，用于与LLM交互
    
    Example:
        service = LLMService()
        llm = service.llm  # 获取LLM实例
    """
    
    _instance: Optional['LLMService'] = None
    _llm: Optional[ChatOpenAI] = None

    def __new__(cls):
        """
        创建或返回单例实例
        
        Returns:
            LLMService: 唯一的服务实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        初始化LLM服务
        
        仅在首次创建时初始化LLM实例，后续调用直接复用已有实例。
        从Django settings中读取LLM配置（模型名称、API密钥、API地址）。
        """
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
        """
        加载环境变量配置
        
        从项目根目录的.env文件加载环境变量。
        如果.env文件不存在，则跳过加载。
        """
        env_path = settings.BASE_DIR / '.env'
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)

    @property
    def llm(self) -> ChatOpenAI:
        """
        获取LLM实例
        
        Returns:
            ChatOpenAI: 配置完成的LLM实例，可直接用于对话和推理
        """
        return self._llm


def load_llm() -> ChatOpenAI:
    """
    加载LLM实例的便捷函数
    
    通过单例模式获取全局唯一的LLM实例。
    适用于只需要LLM而不需要Agent工具的场景。
    
    Returns:
        ChatOpenAI: 配置完成的LLM实例
    
    Example:
        llm = load_llm()
        response = llm.invoke("你好")
    """
    service = LLMService()
    return service.llm


@tool
def get_database(sql: str) -> str:
    """
    数据库查询工具（LangChain Tool装饰器）
    
    提供安全的数据库查询功能，仅允许执行SELECT语句，
    防止SQL注入和数据篡改。
    
    Args:
        sql: SQL查询语句，仅支持SELECT语句
    
    Returns:
        str: 查询结果的字符串表示，或错误信息
    
    Security:
        - 自动过滤INSERT、UPDATE、DELETE、DROP、ALTER、CREATE、TRUNCATE等危险操作
        - 仅支持MySQL 8.0.37版本
    
    Example:
        result = get_database("SELECT * FROM users LIMIT 10")
    """
    sql_stripped = sql.strip().upper()
    if sql_stripped.startswith(('INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE')):
        return "错误：只能执行SELECT查询，不能修改数据库内容"
    return query_database(sql)


async def load_agent():
    """
    异步加载完整的Agent实例
    
    加载并配置包含所有工具的Agent实例，包括：
    1. MCP招聘工具（通过MCP服务器获取）
    2. 本地数据库查询工具
    
    Returns:
        Agent: 配置完成的LangChain Agent实例
    
    Workflow:
        1. 加载LLM实例
        2. 连接MCP服务器获取招聘工具
        3. 合并MCP工具和本地工具
        4. 创建并返回Agent实例
    
    Note:
        - MCP服务器连接失败时，将仅使用本地工具
        - 工具加载过程会打印详细日志
    
    Example:
        agent = await load_agent()
        result = await agent.ainvoke({"messages": [...]})
    """
    llm = load_llm()
    tools: List = []

    try:
        print("正在连接招聘 MCP 服务器加载工具...")
        async with mcp_client:
            tools = mcp_client.get_tools()
            print(f"MCP 招聘工具加载成功，共 {len(tools)} 个工具")
            for t in tools:
                print(f"  - {t.name}: {t.description[:50] if t.description else '无描述'}")
    except Exception as e:
        print(f"MCP 服务器连接失败：{e}")
        print("将仅使用本地工具")
        tools = []

    all_tools = tools + [get_database]
    print(f"总共加载 {len(all_tools)} 个工具")

    agent = create_agent(
        model=llm,
        tools=all_tools,
        system_prompt=SYSTEM_PROMPT
    )
    return agent
