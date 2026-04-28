"""
MCP客户端模块
=============

本模块负责建立与自在招聘MCP工具服务器的连接。
MCP (Model Context Protocol) 是一种标准化的工具调用协议，
允许AI模型通过统一接口调用外部工具。

主要功能：
- 通过stdio传输方式连接MCP服务器
- 使用npx启动@zizaiwork/mcp服务
- 提供招聘数据查询工具接口

使用示例：
    from ai.mcp.client import mcp_client
    
    # 异步上下文中使用
    async with mcp_client:
        tools = mcp_client.get_tools()
        # 使用tools进行Agent调用

配置说明：
- MCP_COMMAND: 启动命令，默认为'npx'
- MCP_ARGS: 命令参数，格式为逗号分隔的字符串
- ZAI_API_KEY: 自在招聘API密钥

依赖说明：
- langchain_mcp_adapters: LangChain的MCP适配器
- django.conf.settings: Django配置读取
"""

import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from django.conf import settings


def _build_mcp_client():
    """
    构建MCP客户端实例
    
    根据Django settings中的MCP_CONFIG配置创建MultiServerMCPClient实例。
    配置包括：
    - command: 启动MCP服务器的命令（通常为npx）
    - args: 传递给命令的参数列表
    - transport: 传输方式，使用stdio进行进程间通信
    - env: 环境变量，包含API密钥等认证信息
    
    Returns:
        MultiServerMCPClient: 配置完成的MCP客户端实例
    
    Configuration:
        settings.MCP_CONFIG应包含以下字段：
        - command: str - 启动命令
        - args: list - 命令参数
        - api_key: str - API密钥
    
    Example:
        client = _build_mcp_client()
        async with client:
            tools = client.get_tools()
    """
    config = settings.MCP_CONFIG
    return MultiServerMCPClient(
        {
            "zaiwork": {
                "command": config["command"],
                "args": config["args"],
                "transport": "stdio",
                "env": {
                    **os.environ,
                    "ZAI_API_KEY": config["api_key"],
                },
            }
        }
    )


mcp_client = _build_mcp_client()
